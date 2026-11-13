
import pytest

from app import app, ACCOUNTS


@pytest.fixture
def client():

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home(client):

    response = client.get("/")

    assert response.status_code == 200
    assert response.json["application"] == "SecureBank"


def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_account_exists(client):

    response = client.get("/accounts/1001")

    assert response.status_code == 200
    assert response.json["customer"] == "Customer A"


def test_account_missing(client):

    response = client.get("/accounts/9999")

    assert response.status_code == 404


def test_valid_transaction(client):

    original_balance = ACCOUNTS["1001"]["balance"]

    response = client.post(
        "/transactions",
        json={
            "account_id": "1001",
            "amount": 100
        }
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"

    ACCOUNTS["1001"]["balance"] = original_balance


def test_invalid_transaction(client):

    response = client.post(
        "/transactions",
        json={
            "account_id": "1001",
            "amount": -100
        }
    )

    assert response.status_code == 400
