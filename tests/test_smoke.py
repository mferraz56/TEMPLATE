from fastapi.testclient import TestClient

from src.app.config.settings import settings
from src.app.factory import create_app


def test_health_endpoint():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_favicon_redirect():
    app = create_app()
    client = TestClient(app, follow_redirects=False)
    resp = client.get("/favicon.ico")
    assert resp.status_code == 308
    assert resp.headers["location"] == "/static/favicon.svg"


def test_production_security_headers(monkeypatch):
    monkeypatch.setattr(settings, "env", "production")
    monkeypatch.setattr(settings, "force_https", True)
    app = create_app()
    client = TestClient(app, base_url="https://example.test")
    resp = client.get("/health", headers={"x-forwarded-proto": "https"})
    assert resp.status_code == 200
    assert "upgrade-insecure-requests" in resp.headers["content-security-policy"]
    assert resp.headers["strict-transport-security"].startswith("max-age=31536000")


def test_force_https_redirect_uses_forwarded_proto(monkeypatch):
    monkeypatch.setattr(settings, "force_https", True)
    app = create_app()
    client = TestClient(app, base_url="http://example.test", follow_redirects=False)
    resp = client.get("/health", headers={"x-forwarded-proto": "http"})
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.test/health"
