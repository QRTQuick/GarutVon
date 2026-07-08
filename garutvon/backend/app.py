from flask import Flask
from a2wsgi import ASGIMiddleware

from .config import Config
from .routes import site
from garutvon.api_prod.main import app as api_app


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
    app.register_blueprint(site)
    app.wsgi_app = Dispatcher(app.wsgi_app, {"/api": ASGIMiddleware(api_app)})
    return app
