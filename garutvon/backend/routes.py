from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

site = Blueprint("site", __name__)

PAGES = {
    "": "index.html",
    "about": "about.html",
    "features": "features.html",
    "download": "download.html",
    "pricing": "pricing.html",
    "api-page": "api.html",
    "developers": "developers.html",
    "documentation": "documentation.html",
    "support-garutvon": "support.html",
    "login": "login.html",
    "forgot-password": "forgot-password.html",
    "register": "register.html",
    "dashboard": "dashboard.html",
}


@site.route("/", defaults={"path": ""})
@site.route("/<path:path>")
def page(path: str):
    normalized = path.strip("/")
    template_name = PAGES.get(normalized)
    if template_name is None:
        raise abort(404)
    try:
        return render_template(template_name)
    except TemplateNotFound:
        abort(404)
