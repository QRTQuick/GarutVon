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
