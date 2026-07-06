from garutvon.backend.app import create_app


def test_home_page_renders():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"GarutVON One Platform" in response.data


def test_api_version_renders_through_mount():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    client = app.test_client()
    response = client.get("/api/version")
    assert response.status_code == 200
    assert response.json["latest_version"]


def test_support_and_seo_routes_render():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    client = app.test_client()

    support = client.get("/support-garutvon")
    robots = client.get("/robots.txt")
    sitemap = client.get("/sitemap.xml")

    assert support.status_code == 200
    assert b"myhappr.com/embed/chisomlifeeugsh" in support.data
    assert robots.status_code == 200
    assert b"Sitemap:" in robots.data
    assert sitemap.status_code == 200
    assert b"/support-garutvon" in sitemap.data


def test_register_rejects_weak_password():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    client = app.test_client()

    response = client.post(
        "/register",
        data={
            "name": "Weak User",
            "email": "weak-user@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Your password is too weak" in response.data
