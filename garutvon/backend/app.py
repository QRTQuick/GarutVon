from flask import Flask
from a2wsgi import ASGIMiddleware
from flask_login import LoginManager

from .config import Config
from .routes import site
from garutvon.database import init_db, SessionLocal
from garutvon.database.models import User

# import API app if present
try:
    from garutvon.api_prod.main import app as api_app
except Exception:
    api_app = None


login_manager = LoginManager()


class Dispatcher:
    def __init__(self, flask_app, mounts):
        self.flask_app = flask_app
        self.mounts = mounts

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        for prefix, app in self.mounts.items():
            if path == prefix or path.startswith(prefix + "/"):
                environ["SCRIPT_NAME"] = environ.get("SCRIPT_NAME", "") + prefix
                environ["PATH_INFO"] = path[len(prefix) :] or "/"
                return app(environ, start_response)
        return self.flask_app(environ, start_response)


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static",
    )
    app.config.from_object(Config)

    # initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    app.register_blueprint(site)

    # initialize database tables
    init_db()

    mounts = {}
    if api_app is not None:
        mounts['/api'] = ASGIMiddleware(api_app)

    app.wsgi_app = Dispatcher(app.wsgi_app, mounts)

    @app.context_processor
    def inject_globals():
        return {
            'donation_url': app.config.get('DONATION_URL'),
            'download_url': app.config.get('DOWNLOAD_URL'),
            'latest_version': app.config.get('LATEST_VERSION'),
            'public_base_url': app.config.get('PUBLIC_BASE_URL'),
        }

    @login_manager.user_loader
    def load_user(user_id):
        try:
            db = SessionLocal()
            user = db.get(User, int(user_id))
            db.close()
            return user
        except Exception:
            return None

    return app
