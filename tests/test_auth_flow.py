import os
import pytest
from server import create_app

@pytest.fixture(scope="module")
def app():
    # Ensure test config uses existing .env
    os.environ.setdefault("FLASK_ENV", "testing")
    application = create_app()
    return application

@pytest.fixture()
def client(app):
    return app.test_client()


def test_login_logout_flow(client):
    # Register if not exists (ignore conflict 409)
    payload_reg = {
        "nik": 999001,
        "nama": "Tester",
        "jenis_kelamin": "L",
        "email": "tester@example.com",
        "nomor_hp": "08123456789",
        "password": "secret123",
    }
    client.post("/auth/register", json=payload_reg)

    # Login with device_id
    payload_login = {"nik": 999001, "password": "secret123", "device_id": "dev-unit-1", "device_name": "UnitTest"}
    res_login = client.post("/auth/login", json=payload_login)
    assert res_login.status_code == 200
    data = res_login.get_json()
    assert "access_token" in data
    token = data["access_token"]

    # Access a protected endpoint (use logout as protected example will be 200)
    res_logout = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"}, json={"device_id": "dev-unit-1"})
    assert res_logout.status_code == 200

    # After logout, the same token should be rejected by middleware (revoked)
    res_again = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res_again.status_code == 401
