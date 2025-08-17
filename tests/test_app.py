# tests/test_app.py
import os
import pytest
import openai
from openai.error import AuthenticationError
from app.magabot import app as flask_app


@pytest.fixture()
def client():
    flask_app.testing = True
    with flask_app.test_client() as c:
        yield c


def test_openai_key_present_in_env():
    """Fail fast if the key isn't provided in CI."""
    key = os.getenv("OPENAI_API_KEY", "")
    assert isinstance(key, str) and len(key.strip()) > 0, "OPENAI_API_KEY missing/empty"


def test_home_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_iphone_ok(client):
    # Your app serves /iphone; adjust/remove if you prefer only "/"
    resp = client.get("/iphone")
    assert resp.status_code == 200


def test_android_ok(client):
    # Your app serves /android; adjust/remove if you prefer only "/"
    resp = client.get("/android")
    assert resp.status_code == 200


def test_get_endpoint_happy_path_mocked_openai(client, monkeypatch):
    """Mock OpenAI to avoid real API calls (fast & free)."""
    def fake_create(**kwargs):
        # Mimic the structure your code reads:
        return {"choices": [{"message": {"content": "fake reply"}}]}
    monkeypatch.setattr(openai.ChatCompletion, "create", fake_create)

    resp = client.get("/get", query_string={"msg": "hello"})
    assert resp.status_code == 200
    assert b"fake reply" in resp.data


def test_get_endpoint_unauthorized_401(client):
    resp = client.get("/get", query_string={"msg": "unauthorized"})
    assert resp.status_code == 401


def test_get_endpoint_auth_error_returns_500(client, monkeypatch):
    """Simulate invalid key → your app should return 500."""
    def raise_auth_error(**kwargs):
        raise AuthenticationError("bad key")
    monkeypatch.setattr(openai.ChatCompletion, "create", raise_auth_error)

    resp = client.get("/get", query_string={"msg": "hello"})
    assert resp.status_code == 500