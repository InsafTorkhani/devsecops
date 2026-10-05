from app import app


def test_hello_endpoint():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"Hello" in response.data
