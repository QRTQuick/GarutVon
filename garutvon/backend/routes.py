from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from jinja2 import TemplateNotFound
from flask_login import login_user, logout_user, current_user, login_required
from garutvon.database import SessionLocal
from garutvon.database.models import User, ApiKey, SupportTicket
from garutvon.auth import generate_reset_token, confirm_reset_token
from garutvon.backend.email import send_password_reset

site = Blueprint("site", __name__)

PAGES = {
    "": "index.html",
    "about": "about.html",
    "features": "features.html",
    "download": "download.html",
    "pricing": "pricing.html",
    "api-page": "api.html",
    "api-testing": "api-testing.html",
    "developers": "developers.html",
    "documentation": "documentation.html",
    "support-garutvon": "support.html",
}


@site.route("/", defaults={"path": ""})
@site.route("/<path:path>")
def page(path: str):
    normalized = path.strip("/")
    # map some known single-word routes to specific templates
    if not normalized:
        template_name = "index.html"
    else:
        template_name = PAGES.get(normalized)
    if template_name is None:
        # handle auth and dashboard separately
        if normalized in ("login", "register", "forgot-password", "reset-password", "dashboard"):
            return globals()[normalized.replace('-', '_')]()
        raise abort(404)
    try:
        return render_template(template_name)
    except TemplateNotFound:
        abort(404)


@site.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    if user and user.check_password(password):
        login_user(user)
        db.close()
        next_url = request.args.get('next') or url_for('site.page', path='dashboard')
        return redirect(next_url)
    db.close()
    flash('Invalid email or password.', 'error')
    return redirect(url_for('site.login'))


@site.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.page', path=''))


@site.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    db = SessionLocal()
    if db.query(User).filter_by(email=email).first():
        db.close()
        flash('That email is already registered.', 'error')
        return redirect(url_for('site.register'))
    user = User(email=email, name=name)
    user.set_password(password)
    db.add(user)
    db.commit()
    login_user(user)
    db.close()
    return redirect(url_for('site.page', path='dashboard'))


@site.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot-password.html')
    email = request.form.get('email', '').strip().lower()
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    db.close()
    if user:
        token = generate_reset_token(email)
        reset_url = url_for('site.reset_password', token=token, _external=True)
        send_password_reset(email, reset_url)
    flash('If that email is registered, password reset instructions have been sent.', 'success')
    return redirect(url_for('site.login'))


@site.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token') or request.form.get('token')
    if request.method == 'GET':
        return render_template('reset-password.html', token=token)
    new_password = request.form.get('new_password', '')
    email = confirm_reset_token(token)
    if not email:
        flash('Invalid or expired token.', 'error')
        return redirect(url_for('site.login'))
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    if not user:
        db.close()
        flash('Account not found.', 'error')
        return redirect(url_for('site.register'))
    user.set_password(new_password)
    db.add(user)
    db.commit()
    db.close()
    flash('Password has been reset. Please log in.', 'success')
    return redirect(url_for('site.login'))


@site.route('/dashboard/api-keys', methods=['POST'])
@login_required
def dashboard_api_keys():
    label = request.form.get('label', '').strip()
    db = SessionLocal()
    api_key = ApiKey(user_id=current_user.id, label=label or 'default')
    db.add(api_key)
    db.commit()
    db.close()
    flash('New API key created. Save it securely.', 'success')
    return redirect(url_for('site.dashboard'))


@site.route('/dashboard')
@login_required
def dashboard():
    db = SessionLocal()
    keys = db.query(ApiKey).filter_by(user_id=current_user.id, is_active=True).all()
    tickets = db.query(SupportTicket).filter_by(user_email=current_user.email).all()
    db.close()
    return render_template('dashboard.html', keys=keys, tickets=tickets)
