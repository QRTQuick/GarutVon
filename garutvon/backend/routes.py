from functools import wraps
import re

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from garutvon.database import ApiKey, ApiLog, Download, SupportTicket, User, db_session

site = Blueprint("site", __name__)

COMMON_PASSWORDS = {
    "password",
    "password123",
    "12345678",
    "123456789",
    "qwerty123",
    "garutvon",
    "admin123",
    "letmein123",
}

PAGES = {
    "/": ("home", "index.html", "Home"),
    "/about": ("about", "about.html", "About"),
    "/features": ("features", "features.html", "Features"),
    "/download": ("download", "download.html", "Download"),
    "/pricing": ("pricing", "pricing.html", "Pricing"),
    "/api-page": ("api_page", "api.html", "API"),
    "/developers": ("developers", "developers.html", "Developers"),
    "/documentation": ("documentation", "documentation.html", "Documentation"),
    "/support-garutvon": ("support_page", "support.html", "Support"),
}


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Administrator access is required.", "error")
            return redirect(url_for("site.dashboard"))
        return view(*args, **kwargs)

    return wrapped


def password_issues(password: str, email: str = "", name: str = "") -> list[str]:
    lowered = password.lower()
    issues = []
    if len(password) < 10:
        issues.append("Use at least 10 characters.")
    if not re.search(r"[A-Z]", password):
        issues.append("Add an uppercase letter.")
    if not re.search(r"[a-z]", password):
        issues.append("Add a lowercase letter.")
    if not re.search(r"\d", password):
        issues.append("Add a number.")
    if not re.search(r"[^A-Za-z0-9]", password):
        issues.append("Add a symbol.")
    if lowered in COMMON_PASSWORDS:
        issues.append("This password is too common.")
    email_name = email.split("@", 1)[0].lower()
    if email_name and email_name in lowered:
        issues.append("Do not include your email name in the password.")
    if name and name.lower().replace(" ", "") in lowered.replace(" ", ""):
        issues.append("Do not include your name in the password.")
    return issues


@site.context_processor
def globals_for_templates():
    return {
        "donation_url": current_app.config["DONATION_URL"],
        "download_url": current_app.config["DOWNLOAD_URL"],
        "latest_version": current_app.config["LATEST_VERSION"],
        "public_base_url": current_app.config["PUBLIC_BASE_URL"],
        "support_email": "garutvon@gmail.com",
        "x_url": "https://x.com/GarutVon",
    }


for route, page in PAGES.items():
    site.add_url_rule(route, page[0], lambda template=page[1], title=page[2]: render_template(template, title=title))


@site.get("/login")
def login():
    return render_template("login.html", title="Login")


@site.post("/login")
def login_post():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    try:
        user = db_session.query(User).filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for("site.dashboard"))
    except SQLAlchemyError:
        db_session.rollback()
        current_app.logger.exception("Login database error")
        flash("Login is temporarily unavailable. Please try again.", "error")
        return redirect(url_for("site.login"))
    flash("Invalid email or password.", "error")
    return redirect(url_for("site.login"))


@site.get("/register")
def register():
    return render_template("register.html", title="Register")


@site.post("/register")
def register_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    if not name or len(name) < 2 or "@" not in email:
        flash("Use a valid name and email address.", "error")
        return redirect(url_for("site.register"))
    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for("site.register"))
    issues = password_issues(password, email=email, name=name)
    if issues:
        flash("Your password is too weak: " + " ".join(issues), "error")
        return redirect(url_for("site.register"))
    try:
        if db_session.query(User).filter_by(email=email).first():
            flash("That email is already registered. Please log in instead.", "error")
            return redirect(url_for("site.login"))
        user = User(name=name, email=email, is_admin=db_session.query(User).count() == 0)
        user.set_password(password)
        db_session.add(user)
        db_session.flush()
        db_session.add(ApiKey(user_id=user.id, label="Production key"))
        db_session.commit()
        login_user(user)
        return redirect(url_for("site.dashboard"))
    except IntegrityError:
        db_session.rollback()
        flash("That email is already registered. Please log in instead.", "error")
        return redirect(url_for("site.login"))
    except SQLAlchemyError:
        db_session.rollback()
        current_app.logger.exception("Registration database error")
        flash("Account creation is temporarily unavailable. Please try again in a moment.", "error")
        return redirect(url_for("site.register"))
    except Exception:
        db_session.rollback()
        current_app.logger.exception("Registration error")
        flash("We could not create your account right now. Please try again.", "error")
        return redirect(url_for("site.register"))


@site.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("site.home"))


@site.get("/dashboard")
@login_required
def dashboard():
    keys = db_session.query(ApiKey).filter_by(user_id=current_user.id).all()
    tickets = db_session.query(SupportTicket).filter_by(user_email=current_user.email).order_by(SupportTicket.created_at.desc()).all()
    return render_template("dashboard.html", title="Dashboard", keys=keys, tickets=tickets)


@site.post("/dashboard/api-keys")
@login_required
def create_api_key():
    label = request.form.get("label", "New key").strip()[:120] or "New key"
    db_session.add(ApiKey(user_id=current_user.id, label=label))
    db_session.commit()
    flash("API key created.", "success")
    return redirect(url_for("site.dashboard"))


@site.post("/support")
def support():
    ticket = SupportTicket(
        user_email=request.form.get("email", getattr(current_user, "email", "")).strip().lower(),
        subject=request.form.get("subject", "GarutVON support").strip()[:180],
        message=request.form.get("message", "").strip(),
    )
    if not ticket.user_email or not ticket.message:
        flash("Email and message are required.", "error")
        return redirect(request.referrer or url_for("site.contact"))
    db_session.add(ticket)
    db_session.commit()
    flash("Support request received.", "success")
    return redirect(request.referrer or url_for("site.contact"))


@site.get("/contact")
def contact():
    return render_template("contact.html", title="Contact")


@site.get("/robots.txt")
def robots_txt():
    base_url = current_app.config["PUBLIC_BASE_URL"]
    body = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /dashboard
Disallow: /login
Disallow: /register

Sitemap: {base_url}/sitemap.xml
"""
    return Response(body, mimetype="text/plain")


@site.get("/sitemap.xml")
def sitemap_xml():
    base_url = current_app.config["PUBLIC_BASE_URL"]
    urls = [
        ("/", "1.0", "daily"),
        ("/about", "0.8", "weekly"),
        ("/features", "0.9", "weekly"),
        ("/download", "0.9", "weekly"),
        ("/pricing", "0.8", "weekly"),
        ("/api-page", "0.8", "weekly"),
        ("/developers", "0.8", "weekly"),
        ("/documentation", "0.8", "weekly"),
        ("/contact", "0.6", "monthly"),
        ("/support-garutvon", "0.7", "weekly"),
    ]
    items = "\n".join(
        f"  <url><loc>{base_url}{path}</loc><changefreq>{freq}</changefreq><priority>{priority}</priority></url>"
        for path, priority, freq in urls
    )
    body = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n'
    return Response(body, mimetype="application/xml")


@site.get("/download/track")
def track_download():
    db_session.add(Download(platform=request.args.get("platform", "windows"), ip_address=request.remote_addr or ""))
    db_session.commit()
    return redirect(current_app.config["DOWNLOAD_URL"])


@site.get("/admin")
@login_required
@admin_required
def admin():
    stats = {
        "users": db_session.query(User).count(),
        "downloads": db_session.query(Download).count(),
        "api_requests": db_session.query(ApiLog).count(),
        "tickets": db_session.query(SupportTicket).count(),
        "latest_version": current_app.config["LATEST_VERSION"],
    }
    logs = db_session.query(ApiLog).order_by(ApiLog.created_at.desc()).limit(20).all()
    tickets = db_session.query(SupportTicket).order_by(SupportTicket.created_at.desc()).limit(20).all()
    return render_template("admin.html", title="Admin", stats=stats, logs=logs, tickets=tickets)
