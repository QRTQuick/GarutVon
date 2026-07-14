import datetime
import logging
import requests
from database.models import Donation, DonationSettings, SessionLocal
from backend.config import Config

logger = logging.getLogger("payment_service")

class BasePaymentProvider:
    """Base interface for all payment/donation providers to enable modular expansion."""
    provider_name = "Base"

    def initiate_payment(self, amount, currency, donor_name=None, donor_message=None, user_id=None):
        raise NotImplementedError

    def verify_webhook(self, payload, headers):
        raise NotImplementedError


class HapperPaymentProvider(BasePaymentProvider):
    provider_name = "Happer"

    def initiate_payment(self, amount, currency, donor_name=None, donor_message=None, user_id=None):
        """
        Initiates a Happer donation. Since Happer runs in an iframe, the primary initiation
        is user-driven. We record a pending transaction reference in our system to track it.
        """
        import uuid
        transaction_ref = f"gv_hap_{uuid.uuid4().hex[:12]}"
        
        db = SessionLocal()
        try:
            pending_donation = Donation(
                donation_id=f"hap_{uuid.uuid4().hex[:12]}",
                transaction_ref=transaction_ref,
                user_id=user_id,
                amount=float(amount),
                currency=currency,
                payment_status="pending",
                payment_provider=self.provider_name,
                donor_name=donor_name,
                donor_message=donor_message,
                created_at=datetime.datetime.utcnow()
            )
            db.add(pending_donation)
            db.commit()
            return {
                "success": True,
                "transaction_ref": transaction_ref,
                "embed_url": Config.HAPPER_DONATION_EMBED
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to initiate Happer payment: {str(e)}")
            return {"success": False, "message": str(e)}
        finally:
            db.close()

    def verify_webhook(self, payload, headers):
        """
        Verifies a Happer webhook payload.
        Happer secures its callback. In a live system, we verify the signature using the webhook secret.
        """
        signature = headers.get("X-Happer-Signature") or headers.get("Authorization")
        if not signature:
            logger.warning("Missing verification signature on Happer webhook callback.")
            return False, "Missing signature"

        # Simulating verification of Happer payload integrity.
        # Check against local secret:
        expected_secret = Config.HAPPER_WEBHOOK_SECRET
        if signature != expected_secret:
            logger.error("Happer webhook signature mismatch. Unauthorized payment completion attempt.")
            return False, "Invalid signature"

        transaction_ref = payload.get("transaction_ref")
        amount = payload.get("amount")
        status = payload.get("status") # e.g. 'completed'
        
        if not transaction_ref or status != "completed":
            logger.warning(f"Incomplete transaction parameters: Ref={transaction_ref}, Status={status}")
            return False, "Invalid parameters"

        db = SessionLocal()
        try:
            donation = db.query(Donation).filter_by(transaction_ref=transaction_ref).first()
            if not donation:
                logger.error(f"No donation record found for transaction ref: {transaction_ref}")
                return False, "Donation record not found"

            if donation.payment_status == "completed":
                return True, "Payment already verified and completed"

            # Check that the amount paid matches the expected amount
            if float(amount) < donation.amount:
                logger.error(f"Amount mismatch for {transaction_ref}: Paid {amount}, expected {donation.amount}")
                return False, "Amount mismatch"

            # Update donation state
            donation.payment_status = "completed"
            donation.created_at = datetime.datetime.utcnow()
            
            # Update overall donation goals
            settings = db.query(DonationSettings).first()
            if settings:
                settings.current_progress += float(amount)
                
            db.commit()
            logger.info(f"Happer payment verification successful for transaction {transaction_ref}")
            return True, "Payment completed successfully"
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating verified donation: {str(e)}")
            return False, str(e)
        finally:
            db.close()


# Future Expansion payment providers placeholders to keep the architecture completely modular!
class StripePaymentProvider(BasePaymentProvider):
    provider_name = "Stripe"
    # Placeholder for future integration
    pass

class PayPalPaymentProvider(BasePaymentProvider):
    provider_name = "PayPal"
    # Placeholder for future integration
    pass


class PaymentService:
    _providers = {
        "Happer": HapperPaymentProvider(),
        "Stripe": StripePaymentProvider(),
        "PayPal": PayPalPaymentProvider()
    }

    @classmethod
    def get_provider(cls, name):
        return cls._providers.get(name, HapperPaymentProvider())

    @classmethod
    def initiate_donation(cls, amount, currency, donor_name=None, donor_message=None, user_id=None, provider="Happer"):
        prov = cls.get_provider(provider)
        return prov.initiate_payment(amount, currency, donor_name, donor_message, user_id)

    @classmethod
    def handle_webhook(cls, provider, payload, headers):
        prov = cls.get_provider(provider)
        if not prov:
            logger.error(f"Unknown payment provider webhook attempt: {provider}")
            return False, "Unknown provider"
        return prov.verify_webhook(payload, headers)
