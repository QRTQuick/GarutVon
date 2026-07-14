import os
import unittest
import datetime
from database.models import Base, create_engine, SessionLocal, User, APIKey, Donation
from backend.services.auth import AuthService
from backend.services.converter import ImageConverterService
from backend.services.payment import PaymentService

class TestGarutVonPlatform(unittest.TestCase):
    def setUp(self):
        # Initialize database tables for testing
        from database.models import init_db
        init_db()
        self.db = SessionLocal()
        
    def tearDown(self):
        self.db.close()

    def test_user_creation_and_auth(self):
        # Verify user seeding & security methods
        from database.models import Admin
        user = self.db.query(Admin).filter_by(email="admin@garutvon.com").first()
        self.assertIsNotNone(user, "Default admin user should have been successfully seeded.")
        self.assertTrue(user.check_password("AdminSecurePass2026!"), "Secure password hashing verification failed.")
        
    def test_jwt_generation_and_decode(self):
        # Verify AuthService cryptographies
        user = self.db.query(User).first()
        if user:
            token = AuthService.generate_jwt(user.id, expires_in_days=1)
            self.assertIsNotNone(token)
            
            ok, payload = AuthService.verify_jwt(token)
            self.assertTrue(ok)
            self.assertEqual(payload["sub"], str(user.id))

    def test_image_converter_extension_validation(self):
        # Valid files check
        ok, msg = ImageConverterService.validate_file("photo.png", 5 * 1024 * 1024)
        self.assertTrue(ok)
        
        # Too large files check
        ok, msg = ImageConverterService.validate_file("large.png", 20 * 1024 * 1024)
        self.assertFalse(ok)
        self.assertIn("too large", msg.lower())
        
        # Corrupt extension checks
        ok, msg = ImageConverterService.validate_file("doc.exe", 1024)
        self.assertFalse(ok)
        self.assertIn("unsupported", msg.lower())

    def test_happer_donation_initiation(self):
        # Initiate a test donation trace
        result = PaymentService.initiate_donation(25.0, "USD", "Test Sponsor", "Keep up the amazing work!", user_id=None)
        self.assertTrue(result["success"])
        self.assertIn("gv_hap_", result["transaction_ref"])
        
        # Verify transaction registration in database
        donation = self.db.query(Donation).filter_by(transaction_ref=result["transaction_ref"]).first()
        self.assertIsNotNone(donation)
        self.assertEqual(donation.amount, 25.0)
        self.assertEqual(donation.payment_status, "pending")

if __name__ == "__main__":
    unittest.main()
