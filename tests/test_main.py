from fastapi.testclient import TestClient

from app.app_logging import logger
from app.main import app

client = TestClient(app)


def test_db_endpoint():
    response = client.get("/api/payment/test_db")

    # Print the response content
    logger.info(response)
    logger.info(response.json())

    assert response.status_code == 200
    assert response.json() == True