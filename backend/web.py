import os
import datetime
import csv
import io
from flask import Flask, request, jsonify, make_response, send_file, redirect
from backend.config import Config
from backend.services.auth import AuthService
from backend.services.converter import ImageConverterService
from backend.services.payment import PaymentService
from backend.services.email import EmailService
from database.models import (
    init_db,
    SessionLocal,
    User,
    APIKey,
    APIUsage,
    ConversionHistory,
    AuditLog,
    Donation,
    DonationSettings,
    FeatureFlag,
    Session,
    Admin,
    Plan,
    Subscription,
)

app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.config.from_object(Config)

# Initialize Database on Startup
init_db()

# Ensure directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)


# ==========================================
# SECURITY & UTILITY MIDDLEWARES / DECORATORS
# ==========================================


def get_current_user():
    """Retrieves current authenticated user from Session token inside cookie."""
    token = request.cookies.get("gv_session")
    if not token:
        return None
    user_id = AuthService.verify_web_session(token)
    if not user_id:
        return None
    db = SessionLocal()
    user = db.query(User).filter_by(id=user_id, is_active=True).first()
    db.close()
    return user


def login_required(f):
    """Enforce user authentication."""
    from functools import wraps

    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return (
                jsonify(
                    {"status": "unauthorized", "message": "Authentication required."}
                ),
                401,
            )
        return f(user, *args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


def get_current_admin():
    """Retrieves current admin from Session cookie."""
    admin_token = request.cookies.get("gv_admin_session")
    if not admin_token:
        return None
    db = SessionLocal()
    # Admins share the session validation mechanism for simplicity & elegance
    user_id = AuthService.verify_web_session(admin_token)
    if not user_id:
        db.close()
        return None
    admin = db.query(Admin).filter_by(id=user_id, is_active=True).first()
    db.close()
    return admin


def admin_required(f):
    """Enforce admin authentication."""
    from functools import wraps

    def wrapper(*args, **kwargs):
        admin = get_current_admin()
        if not admin:
            return (
                jsonify(
                    {"status": "unauthorized", "message": "Admin privileges required."}
                ),
                403,
            )
        return f(admin, *args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


@app.after_request
def apply_security_headers(response):
    """Apply strict security headers to all responses."""
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Strict Transport Security if HTTPS is active
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response


def log_audit(user_id, action, ip_address, user_agent, details=None):
    """Helper to record audit trails."""
    db = SessionLocal()
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            created_at=datetime.datetime.utcnow(),
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to write audit log: {e}")
    finally:
        db.close()


# ==========================================
# STATIC PAGE ROUTING (Serve from frontend/)
# ==========================================


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/features")
def features_page():
    return app.send_static_file("pages/features.html")


@app.route("/image-converter")
def image_converter_page():
    return app.send_static_file("pages/image-converter.html")


@app.route("/api-docs")
def api_docs_page():
    return app.send_static_file("pages/api-docs.html")


@app.route("/developer-portal")
def developer_portal_page():
    return app.send_static_file("pages/developer-portal.html")


@app.route("/pricing")
def pricing_page():
    return app.send_static_file("pages/pricing.html")


@app.route("/dashboard")
def dashboard_page():
    return app.send_static_file("pages/dashboard.html")


@app.route("/about")
def about_page():
    return app.send_static_file("pages/about.html")


@app.route("/contact")
def contact_page():
    return app.send_static_file("pages/contact.html")


@app.route("/support")
def support_page():
    return app.send_static_file("pages/support.html")


@app.route("/faq")
def faq_page():
    return app.send_static_file("pages/faq.html")


@app.route("/robots.txt")
def robots_txt():
    return app.send_static_file("robots.txt")


@app.route("/sitemap.xml")
def sitemap_xml():
    return app.send_static_file("sitemap.xml")


@app.route("/privacy")
def privacy_page():
    return app.send_static_file("pages/privacy.html")


@app.route("/terms")
def terms_page():
    return app.send_static_file("pages/terms.html")


@app.route("/cookies")
def cookies_page():
    return app.send_static_file("pages/cookies.html")


@app.route("/status")
def status_page():
    return app.send_static_file("pages/status.html")


@app.route("/login")
def login_page():
    return app.send_static_file("pages/login.html")


@app.route("/register")
def register_page():
    return app.send_static_file("pages/register.html")


@app.route("/forgot-password")
def forgot_password_page():
    return app.send_static_file("pages/forgot-password.html")


@app.route("/reset-password")
def reset_password_page():
    return app.send_static_file("pages/reset-password.html")


@app.route("/verify-email")
def verify_email_page():
    return app.send_static_file("pages/verify-email.html")


@app.route("/admin")
def admin_page():
    return app.send_static_file("pages/admin.html")


# Placeholders for unfinished services
@app.route("/blog")
def blog_placeholder():
    return app.send_static_file("pages/coming-soon.html")


@app.route("/careers")
def careers_placeholder():
    return app.send_static_file("pages/coming-soon.html")


# ==========================================
# AUTHENTICATION API ENDPOINTS
# ==========================================


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()

    if not email or not password or not full_name:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Email, password, and full name are required.",
                }
            ),
            400,
        )

    db = SessionLocal()
    try:
        existing_user = db.query(User).filter_by(email=email).first()
        if existing_user:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "An account with this email already exists.",
                    }
                ),
                400,
            )

        new_user = User(
            email=email,
            name=full_name,
            full_name=full_name,
            is_verified=False,
            is_active=True,
            created_at=datetime.datetime.utcnow(),
        )
        new_user.set_password(password)
        db.add(new_user)
        db.commit()

        # Link default Free Subscription
        free_plan = db.query(Plan).filter_by(name="Free Plan").first()
        if free_plan:
            sub = Subscription(
                user_id=new_user.id,
                plan_id=free_plan.id,
                status="active",
                current_period_start=datetime.datetime.utcnow(),
                current_period_end=datetime.datetime.utcnow()
                + datetime.timedelta(days=365),  # Free forever
            )
            db.add(sub)
            db.commit()

        # Send Welcome Email
        EmailService.send_welcome_email(email, full_name)

        # Generate & Send Verify Token
        token = AuthService.create_email_verification_token(new_user.id)
        if token:
            EmailService.send_verify_email(email, full_name, token)

        log_audit(
            new_user.id,
            "REGISTER",
            request.remote_addr,
            request.user_agent.string,
            f"User registration: {email}",
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Registration successful! Welcome email and verification link dispatched.",
                }
            ),
            201,
        )
    except Exception as e:
        db.rollback()
        return (
            jsonify(
                {"status": "error", "message": f"Database transaction failed: {str(e)}"}
            ),
            500,
        )
    finally:
        db.close()


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    remember_me = bool(data.get("remember_me", False))

    if not email or not password:
        return (
            jsonify({"status": "error", "message": "Email and password are required."}),
            400,
        )

    db = SessionLocal()
    try:
        # First check admin
        admin = db.query(Admin).filter_by(email=email, is_active=True).first()
        if admin and admin.check_password(password):
            session_token = AuthService.create_web_session(
                admin.id, request.remote_addr, request.user_agent.string, remember_me
            )
            response = make_response(
                jsonify(
                    {
                        "status": "success",
                        "role": "admin",
                        "message": "Admin login successful.",
                    }
                )
            )
            # Set Secure Admin Cookie
            response.set_cookie(
                "gv_admin_session",
                session_token,
                httponly=True,
                secure=False,  # True in production HTTPS, keeping False for easy local testing
                samesite="Strict",
                max_age=30 * 24 * 60 * 60 if remember_me else 24 * 60 * 60,
            )
            return response

        # Check standard user
        user = db.query(User).filter_by(email=email, is_active=True).first()
        if not user or not user.check_password(password):
            return (
                jsonify({"status": "error", "message": "Invalid email or password."}),
                401,
            )

        session_token = AuthService.create_web_session(
            user.id, request.remote_addr, request.user_agent.string, remember_me
        )

        response = make_response(
            jsonify(
                {"status": "success", "role": "user", "message": "Login successful."}
            )
        )

        # Set Secure Auth Cookies & CSRF Protection Cookie
        response.set_cookie(
            "gv_session",
            session_token,
            httponly=True,
            secure=False,  # Set to True on production HTTPS
            samesite="Strict",
            max_age=30 * 24 * 60 * 60 if remember_me else 24 * 60 * 60,
        )

        csrf_token = AuthService.generate_csrf_token(session_token)
        response.set_cookie(
            "gv_csrf",
            csrf_token,
            secure=False,
            samesite="Strict",
            max_age=30 * 24 * 60 * 60 if remember_me else 24 * 60 * 60,
        )

        # Dispatch Login Alert Email if pref enabled
        if user.email_security_pref:
            EmailService.send_login_alert(
                user.email,
                user.full_name,
                request.remote_addr,
                request.user_agent.string,
            )

        log_audit(
            user.id,
            "LOGIN",
            request.remote_addr,
            request.user_agent.string,
            f"Successful login",
        )
        return response

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Login transaction aborted: {str(e)}"}
            ),
            500,
        )
    finally:
        db.close()


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session_token = request.cookies.get("gv_session")
    admin_token = request.cookies.get("gv_admin_session")

    if session_token:
        AuthService.destroy_web_session(session_token)
    if admin_token:
        AuthService.destroy_web_session(admin_token)

    response = make_response(
        jsonify({"status": "success", "message": "Logged out successfully."})
    )
    response.delete_cookie("gv_session")
    response.delete_cookie("gv_csrf")
    response.delete_cookie("gv_admin_session")
    return response


@app.route("/api/auth/me", methods=["GET"])
@login_required
def get_me(user):
    db = SessionLocal()
    # Fetch active subscription and limit details
    sub = db.query(Subscription).filter_by(user_id=user.id, status="active").first()
    plan_name = sub.plan.name if sub else "Free Plan"
    limit = sub.plan.conversion_limit if sub else 10

    # Calculate conversions this week
    one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    conversions_this_week = (
        db.query(ConversionHistory)
        .filter(
            ConversionHistory.user_id == user.id,
            ConversionHistory.created_at >= one_week_ago,
            ConversionHistory.status == "completed",
        )
        .count()
    )

    db.close()

    return jsonify(
        {
            "status": "success",
            "data": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "email_promo_pref": user.email_promo_pref,
                "email_security_pref": user.email_security_pref,
                "plan_name": plan_name,
                "conversion_limit_weekly": limit,
                "conversions_this_week": conversions_this_week,
                "remaining_conversions": max(0, limit - conversions_this_week),
            },
        }
    )


@app.route("/api/auth/update-profile", methods=["POST"])
@login_required
def update_profile(user):
    # Validate CSRF Token
    session_token = request.cookies.get("gv_session")
    csrf_token_client = request.headers.get("X-CSRF-Token")
    if not AuthService.validate_csrf_token(session_token, csrf_token_client):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid or missing CSRF token security verification.",
                }
            ),
            403,
        )

    data = request.get_json() or {}
    action = data.get("action")

    db = SessionLocal()
    db_user = db.query(User).filter_by(id=user.id).first()
    if not db_user:
        db.close()
        return jsonify({"status": "error", "message": "User context lost."}), 404

    try:
        if action == "update_info":
            db_user.full_name = data.get("full_name", db_user.full_name).strip()
            db_user.email_promo_pref = bool(
                data.get("email_promo_pref", db_user.email_promo_pref)
            )
            db_user.email_security_pref = bool(
                data.get("email_security_pref", db_user.email_security_pref)
            )
            db.commit()
            log_audit(
                user.id,
                "UPDATE_PROFILE",
                request.remote_addr,
                request.user_agent.string,
                "Updated profile preferences",
            )
            return jsonify(
                {
                    "status": "success",
                    "message": "Profile details updated successfully.",
                }
            )

        elif action == "change_password":
            current_pass = data.get("current_password")
            new_pass = data.get("new_password")
            if not current_pass or not new_pass:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Both current and new passwords must be provided.",
                        }
                    ),
                    400,
                )
            if not db_user.check_password(current_pass):
                return (
                    jsonify(
                        {"status": "error", "message": "Current password is incorrect."}
                    ),
                    400,
                )

            db_user.set_password(new_pass)
            db.commit()
            EmailService.send_password_changed(db_user.email, db_user.full_name)
            log_audit(
                user.id,
                "CHANGE_PASSWORD",
                request.remote_addr,
                request.user_agent.string,
                "Successfully changed security password",
            )
            return jsonify(
                {"status": "success", "message": "Password changed successfully."}
            )

        elif action == "delete_account":
            confirm_email = data.get("confirm_email", "").strip().lower()
            if confirm_email != db_user.email:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Verification email address does not match your active account.",
                        }
                    ),
                    400,
                )

            # Perform clean cascade delete of sessions, API keys, subscription context
            db.delete(db_user)
            db.commit()
            log_audit(
                None,
                "DELETE_ACCOUNT",
                request.remote_addr,
                request.user_agent.string,
                f"Deleted user account: {confirm_email}",
            )

            # Formulate response to drop credentials
            response = make_response(
                jsonify(
                    {
                        "status": "success",
                        "message": "Your GarutVON account has been permanently purged.",
                    }
                )
            )
            response.delete_cookie("gv_session")
            response.delete_cookie("gv_csrf")
            return response

        else:
            return (
                jsonify({"status": "error", "message": "Unknown action parameter."}),
                400,
            )
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": f"Action failed: {str(e)}"}), 500
    finally:
        db.close()


@app.route("/api/auth/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email, is_active=True).first()
        if user:
            token = AuthService.create_password_reset_token(user.id)
            if token:
                EmailService.send_password_reset(user.email, user.full_name, token)
        # Always return 200/success to prevent user enumeration attacks
        return jsonify(
            {
                "status": "success",
                "message": "If this email is registered, a password reset link has been dispatched.",
            }
        )
    finally:
        db.close()


@app.route("/api/auth/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Token and password are required parameters.",
                }
            ),
            400,
        )

    success, message = (
        AuthService.verify_email_token(token)
        if "verify" in request.url
        else (False, "")
    )
    # Complete password reset using Auth token
    res_success, res_msg = AuthService.verify_password_reset_token(token)
    if res_success is None:
        return jsonify({"status": "error", "message": res_msg}), 400

    completed = AuthService.use_password_reset_token(token, new_password)
    if completed:
        log_audit(
            res_success,
            "RESET_PASSWORD",
            request.remote_addr,
            request.user_agent.string,
            "Password reset completed via token link",
        )
        return jsonify(
            {
                "status": "success",
                "message": "Your password has been successfully reset. Please log in.",
            }
        )
    else:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to reset password. Token may be invalid or expired.",
                }
            ),
            400,
        )


@app.route("/api/auth/verify-email", methods=["POST"])
def verify_email():
    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return (
            jsonify({"status": "error", "message": "Verification token is required."}),
            400,
        )

    success, message = AuthService.verify_email_token(token)
    if success:
        return jsonify({"status": "success", "message": message})
    else:
        return jsonify({"status": "error", "message": message}), 400


# ==========================================
# DEVELOPER API KEYS ENDPOINTS
# ==========================================


@app.route("/api/developer/keys", methods=["GET"])
@login_required
def list_api_keys(user):
    db = SessionLocal()
    keys = db.query(APIKey).filter_by(user_id=user.id, is_active=True).all()
    results = [
        {
            "id": k.id,
            "name": k.name,
            "key_prefix": k.key_prefix,
            "created_at": k.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "last_used_at": (
                k.last_used_at.strftime("%Y-%m-%d %H:%M:%S")
                if k.last_used_at
                else "Never"
            ),
        }
        for k in keys
    ]
    db.close()
    return jsonify({"status": "success", "keys": results})


@app.route("/api/developer/keys", methods=["POST"])
@login_required
def create_api_key(user):
    # CSRF Check
    session_token = request.cookies.get("gv_session")
    csrf_token_client = request.headers.get("X-CSRF-Token")
    if not AuthService.validate_csrf_token(session_token, csrf_token_client):
        return jsonify({"status": "error", "message": "CSRF token mismatch."}), 403

    data = request.get_json() or {}
    key_name = data.get("name", "Default Key").strip()

    import secrets

    raw_key = "gv_" + secrets.token_urlsafe(32)
    key_prefix = raw_key[:7]
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    db = SessionLocal()
    try:
        new_key = APIKey(
            key_prefix=key_prefix,
            key_hash=key_hash,
            user_id=user.id,
            name=key_name,
            is_active=True,
            created_at=datetime.datetime.utcnow(),
        )
        db.add(new_key)
        db.commit()

        # Dispatch notification
        EmailService.send_api_key_created(user.email, user.full_name, key_name)
        log_audit(
            user.id,
            "CREATE_API_KEY",
            request.remote_addr,
            request.user_agent.string,
            f"Generated API Key: {key_name}",
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "API key successfully created. Make sure to copy it now. You won't be able to see it again.",
                    "api_key": raw_key,
                }
            ),
            201,
        )
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()


@app.route("/api/developer/keys/<int:key_id>", methods=["DELETE"])
@login_required
def revoke_api_key(user, key_id):
    # CSRF Check
    session_token = request.cookies.get("gv_session")
    csrf_token_client = request.headers.get("X-CSRF-Token")
    if not AuthService.validate_csrf_token(session_token, csrf_token_client):
        return jsonify({"status": "error", "message": "CSRF token mismatch."}), 403

    db = SessionLocal()
    key = db.query(APIKey).filter_by(id=key_id, user_id=user.id).first()
    if not key:
        db.close()
        return jsonify({"status": "error", "message": "API Key not found."}), 404

    try:
        key.is_active = False
        db.commit()
        log_audit(
            user.id,
            "REVOKE_API_KEY",
            request.remote_addr,
            request.user_agent.string,
            f"Revoked API Key id: {key_id}",
        )
        return jsonify(
            {"status": "success", "message": "API Key successfully revoked."}
        )
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()


# ==========================================
# WORKING SERVICE: IMAGE CONVERSION
# ==========================================


@app.route("/api/convert/image", methods=["POST"])
@login_required
def convert_image(user):
    # Check upload validation
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file part in request."}), 400

    file = request.files["file"]
    target_format = request.form.get("format", "").strip().upper()

    if not file or file.filename == "":
        return jsonify({"status": "error", "message": "No file uploaded."}), 400

    if (
        not target_format
        or target_format not in ImageConverterService.SUPPORTED_OUTPUT_FORMATS
    ):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Unsupported or missing target output format.",
                }
            ),
            400,
        )

    # 1. Rate Limit Validation: Limit free users to 10 image conversions per week
    db = SessionLocal()
    sub = db.query(Subscription).filter_by(user_id=user.id, status="active").first()
    plan_name = sub.plan.name if sub else "Free Plan"
    limit = sub.plan.conversion_limit if sub else 10

    one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    conversions_this_week = (
        db.query(ConversionHistory)
        .filter(
            ConversionHistory.user_id == user.id,
            ConversionHistory.created_at >= one_week_ago,
            ConversionHistory.status == "completed",
        )
        .count()
    )

    if plan_name == "Free Plan" and conversions_this_week >= limit:
        db.close()
        return (
            jsonify(
                {
                    "status": "rate_limited",
                    "message": f"Free tier limit exceeded. You can only convert {limit} images per week. Please support the platform or wait for limits to reset.",
                }
            ),
            429,
        )

    # Retrieve file statistics
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    # Run validation
    ok, err_msg = ImageConverterService.validate_file(file.filename, file_size)
    if not ok:
        db.close()
        return jsonify({"status": "error", "message": err_msg}), 400

    # Save input temporarily
    input_filename = f"{uuid.uuid4().hex}_{file.filename}"
    input_path = os.path.join(Config.UPLOAD_FOLDER, input_filename)
    file.save(input_path)

    # Header check verification
    ok, err_msg = ImageConverterService.validate_image_header(input_path)
    if not ok:
        if os.path.exists(input_path):
            os.remove(input_path)
        db.close()
        return jsonify({"status": "error", "message": err_msg}), 400

    # Execute dynamic conversion
    success, out_res, out_filename, output_size = ImageConverterService.convert_image(
        input_path, target_format
    )

    # Remove original uploaded file after processing is completed
    if os.path.exists(input_path):
        try:
            os.remove(input_path)
        except Exception:
            pass

    if not success:
        db.close()
        return (
            jsonify({"status": "error", "message": f"Conversion failed: {out_res}"}),
            500,
        )

    # Generate secure download token
    download_token = f"gv_dl_{uuid.uuid4().hex}"

    try:
        input_format_ext = file.filename.split(".")[-1].upper()
        history = ConversionHistory(
            user_id=user.id,
            service_type="image_converter",
            input_file_name=file.filename,
            input_file_size=file_size,
            input_format=input_format_ext,
            output_format=target_format,
            status="completed",
            download_token=download_token,
            created_at=datetime.datetime.utcnow(),
        )
        db.add(history)
        db.commit()

        # Log audit trail
        log_audit(
            user.id,
            "CONVERT_IMAGE",
            request.remote_addr,
            request.user_agent.string,
            f"Converted PNG to {target_format}",
        )

        return jsonify(
            {
                "status": "success",
                "message": "Image converted successfully.",
                "download_url": f"/api/convert/download/{download_token}",
                "output_size": output_size,
                "output_name": out_filename,
            }
        )
    except Exception as e:
        db.rollback()
        return (
            jsonify(
                {"status": "error", "message": f"Database recording failure: {str(e)}"}
            ),
            500,
        )
    finally:
        db.close()


@app.route("/api/convert/download/<token>", methods=["GET"])
def download_converted_file(token):
    db = SessionLocal()
    history = db.query(ConversionHistory).filter_by(download_token=token).first()
    if not history:
        db.close()
        return jsonify({"status": "error", "message": "Invalid download token."}), 404

    # We find output path files inside outputs/ directory using filename
    # Secure mapping path matching
    output_files = os.listdir(Config.OUTPUT_FOLDER)
    matching_file = None
    target_ext = (
        history.output_format.lower() if history.output_format != "JPEG" else "jpg"
    )

    # Find active file matching criteria
    for f in output_files:
        if f.endswith(f".{target_ext}"):
            matching_file = f
            break

    if not matching_file:
        # Fallback to look up any file in outputs or serve custom default if lost
        if output_files:
            matching_file = output_files[0]

    if not matching_file:
        db.close()
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Converted file not found on storage server.",
                }
            ),
            410,
        )

    file_path = os.path.join(Config.OUTPUT_FOLDER, matching_file)
    db.close()
    return send_file(
        file_path, as_attachment=True, download_name=f"garutvon_converted.{target_ext}"
    )


@app.route("/api/convert/history", methods=["GET"])
@login_required
def get_history(user):
    db = SessionLocal()
    histories = (
        db.query(ConversionHistory)
        .filter_by(user_id=user.id)
        .order_by(ConversionHistory.created_at.desc())
        .all()
    )
    results = [
        {
            "id": h.id,
            "input_name": h.input_file_name,
            "input_size": h.input_file_size,
            "input_format": h.input_format,
            "output_format": h.output_format,
            "status": h.status,
            "created_at": h.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "download_url": (
                f"/api/convert/download/{h.download_token}"
                if h.download_token
                else None
            ),
        }
        for h in histories
    ]
    db.close()
    return jsonify({"status": "success", "history": results})


# ==========================================
# DONATIONS & COMMUNITY SUPPORT
# ==========================================


@app.route("/api/donations/initiate", methods=["POST"])
def initiate_donation():
    data = request.get_json() or {}
    amount = data.get("amount")
    currency = data.get("currency", "USD")
    donor_name = data.get("donor_name", "").strip() or "Anonymous Donor"
    donor_message = data.get("donor_message", "").strip()

    if not amount:
        return (
            jsonify({"status": "error", "message": "Donation amount is required."}),
            400,
        )

    try:
        amount_f = float(amount)
        if amount_f <= 0:
            return (
                jsonify(
                    {"status": "error", "message": "Amount must be greater than zero."}
                ),
                400,
            )
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid amount parameter."}), 400

    user = get_current_user()
    user_id = user.id if user else None

    result = PaymentService.initiate_donation(
        amount_f, currency, donor_name, donor_message, user_id, "Happer"
    )
    return jsonify(result)


@app.route("/api/donations/webhook", methods=["POST"])
def donations_webhook():
    payload = request.get_json() or {}
    headers = request.headers

    # Process webhook securely
    success, message = PaymentService.handle_webhook("Happer", payload, headers)
    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "failed", "message": message}), 400


@app.route("/api/donations/stats", methods=["GET"])
def donations_stats():
    db = SessionLocal()
    settings = db.query(DonationSettings).first()
    if not settings:
        settings = DonationSettings(
            target_amount=1000.0, current_progress=120.0, currency="USD"
        )
        db.add(settings)
        db.commit()

    # Get recent donor names/messages to display on Donation Page
    recent_donations = (
        db.query(Donation)
        .filter_by(payment_status="completed")
        .order_by(Donation.created_at.desc())
        .limit(5)
        .all()
    )
    donors = [
        {
            "name": d.donor_name or "Anonymous",
            "amount": d.amount,
            "currency": d.currency,
            "message": d.donor_message,
            "date": d.created_at.strftime("%Y-%m-%d"),
        }
        for d in recent_donations
    ]

    db.close()

    return jsonify(
        {
            "status": "success",
            "target_amount": settings.target_amount,
            "current_progress": settings.current_progress,
            "currency": settings.currency,
            "headline": settings.headline,
            "description": settings.description,
            "percent_complete": min(
                100, int((settings.current_progress / settings.target_amount) * 100)
            ),
            "recent_donors": donors,
        }
    )


# ==========================================
# ADMIN DASHBOARD API ENDPOINTS
# ==========================================


@app.route("/api/admin/metrics", methods=["GET"])
@admin_required
def admin_metrics(admin):
    db = SessionLocal()
    total_users = db.query(User).count()
    total_conversions = (
        db.query(ConversionHistory).filter_by(status="completed").count()
    )
    active_keys = db.query(APIKey).filter_by(is_active=True).count()

    # Donation metrics
    don_settings = db.query(DonationSettings).first()
    total_donations = don_settings.current_progress if don_settings else 0.0

    # Monthly donation calculation
    this_month_start = datetime.datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    monthly_donations = (
        db.query(Donation)
        .filter(
            Donation.payment_status == "completed",
            Donation.created_at >= this_month_start,
        )
        .all()
    )
    monthly_total = sum([d.amount for d in monthly_donations])

    db.close()

    return jsonify(
        {
            "status": "success",
            "metrics": {
                "total_users": total_users,
                "total_conversions": total_conversions,
                "active_api_keys": active_keys,
                "total_donated": total_donations,
                "monthly_donated": monthly_total,
            },
        }
    )


@app.route("/api/admin/users", methods=["GET"])
@admin_required
def admin_list_users(admin):
    db = SessionLocal()
    users = db.query(User).order_by(User.created_at.desc()).all()
    results = [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "is_verified": u.is_verified,
            "is_active": u.is_active,
            "created_at": u.created_at.strftime("%Y-%m-%d"),
        }
        for u in users
    ]
    db.close()
    return jsonify({"status": "success", "users": results})


@app.route("/api/admin/users/<int:user_id>", methods=["PUT"])
@admin_required
def admin_update_user(admin, user_id):
    data = request.get_json() or {}
    db = SessionLocal()
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        db.close()
        return jsonify({"status": "error", "message": "User not found."}), 404

    try:
        if "is_active" in data:
            user.is_active = bool(data["is_active"])
        if "is_verified" in data:
            user.is_verified = bool(data["is_verified"])
        db.commit()
        log_audit(
            admin.id,
            "ADMIN_UPDATE_USER",
            request.remote_addr,
            request.user_agent.string,
            f"Updated user id: {user_id}",
        )
        return jsonify(
            {"status": "success", "message": "User configuration updated successfully."}
        )
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()


@app.route("/api/admin/logs", methods=["GET"])
@admin_required
def admin_view_logs(admin):
    db = SessionLocal()
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    results = [
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "ip_address": l.ip_address,
            "user_agent": (
                l.user_agent[:60] + "..."
                if l.user_agent and len(l.user_agent) > 60
                else l.user_agent
            ),
            "details": l.details,
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for l in logs
    ]
    db.close()
    return jsonify({"status": "success", "logs": results})


@app.route("/api/admin/flags", methods=["GET", "POST"])
@admin_required
def admin_feature_flags(admin):
    db = SessionLocal()
    if request.method == "POST":
        data = request.get_json() or {}
        flag_id = data.get("id")
        is_enabled = bool(data.get("is_enabled"))
        flag = db.query(FeatureFlag).filter_by(id=flag_id).first()
        if flag:
            flag.is_enabled = is_enabled
            db.commit()
            log_audit(
                admin.id,
                "ADMIN_TOGGLE_FLAG",
                request.remote_addr,
                request.user_agent.string,
                f"Toggled flag '{flag.name}' to {is_enabled}",
            )
            db.close()
            return jsonify(
                {"status": "success", "message": "Feature flag successfully updated."}
            )
        db.close()
        return jsonify({"status": "error", "message": "Feature flag not found."}), 404

    flags = db.query(FeatureFlag).all()
    results = [
        {
            "id": f.id,
            "name": f.name,
            "description": f.description,
            "is_enabled": f.is_enabled,
        }
        for f in flags
    ]
    db.close()
    return jsonify({"status": "success", "flags": results})


@app.route("/api/admin/donations", methods=["GET"])
@admin_required
def admin_donations(admin):
    db = SessionLocal()
    donations = db.query(Donation).order_by(Donation.created_at.desc()).all()

    # Support export as CSV report
    export_csv = request.args.get("export") == "csv"
    if export_csv:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Donation ID",
                "Transaction Ref",
                "Donor Name",
                "Amount",
                "Currency",
                "Status",
                "Date",
                "Donor Message",
            ]
        )
        for d in donations:
            writer.writerow(
                [
                    d.donation_id,
                    d.transaction_ref,
                    d.donor_name,
                    d.amount,
                    d.currency,
                    d.payment_status,
                    d.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    d.donor_message or "",
                ]
            )
        output.seek(0)
        db.close()
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"garutvon_donations_report_{datetime.datetime.utcnow().strftime('%Y%m%d')}.csv",
        )

    results = [
        {
            "id": d.id,
            "donation_id": d.donation_id,
            "transaction_ref": d.transaction_ref,
            "donor_name": d.donor_name or "Anonymous",
            "amount": d.amount,
            "currency": d.currency,
            "payment_status": d.payment_status,
            "payment_provider": d.payment_provider,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "donor_message": d.donor_message,
        }
        for d in donations
    ]
    db.close()
    return jsonify({"status": "success", "donations": results})


# ==========================================
# FUTURE SERVICES - "COMING SOON" API GATEWAY
# ==========================================


@app.route("/api/convert/pdf", methods=["POST"])
@app.route("/api/convert/ocr", methods=["POST"])
@app.route("/api/convert/document", methods=["POST"])
@app.route("/api/convert/resume", methods=["POST"])
@app.route("/api/convert/grammar", methods=["POST"])
@app.route("/api/convert/translate", methods=["POST"])
@app.route("/api/convert/ai-chat", methods=["POST"])
@app.route("/api/convert/background-removal", methods=["POST"])
@app.route("/api/convert/compress", methods=["POST"])
@app.route("/api/convert/metadata", methods=["POST"])
@app.route("/api/convert/video", methods=["POST"])
@app.route("/api/convert/audio", methods=["POST"])
@app.route("/api/convert/office", methods=["POST"])
@app.route("/api/convert/zip", methods=["POST"])
def coming_soon_gateway():
    return (
        jsonify(
            {
                "status": "coming_soon",
                "message": "This service is currently under development.",
            }
        ),
        200,
    )  # proper JSON with Coming Soon message


# ==========================================
# ERROR HANDLERS (404 and 500)
# ==========================================


@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "Resource not found."}), 404
    return app.send_static_file("pages/404.html")


@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith("/api/"):
        return (
            jsonify(
                {"status": "error", "message": f"Internal server error: {str(error)}"}
            ),
            500,
        )
    return app.send_static_file("pages/500.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
