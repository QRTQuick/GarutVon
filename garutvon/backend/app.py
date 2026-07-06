from a2wsgi import ASGIMiddleware
from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from garutvon.api.main import api_app
from garutvon.backend.config import Config
from garutvon.backend.routes import site
from garutvon.database import User, db_session, init_db

csrf = CSRFProtect()
login_manager = LoginManager()


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static",
    )
    app.config.from_object(Config)

    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "site.login"
    app.register_blueprint(site)

    init_db()

    @login_manager.user_loader
    def load_user(user_id: str):
        return db_session.get(User, int(user_id))

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    app.wsgi_app = Dispatcher(app.wsgi_app, {"/api": ASGIMiddleware(api_app)})
    return app


class Dispatcher:
    def __init__(self, flask_app, mounts):
        self.flask_app = flask_app
        self.mounts = mounts

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        for prefix, app in self.mounts.items():
            if path == prefix or path.startswith(prefix + "/"):
                environ["SCRIPT_NAME"] = environ.get("SCRIPT_NAME", "") + prefix
                environ["PATH_INFO"] = path[len(prefix):] or "/"
                return app(environ, start_response)
        return self.flask_app(environ, start_response)
