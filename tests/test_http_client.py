import httpx

from api_toolkit.http_client import send_request


def test_send_request_returns_json_response(monkeypatch):
    def mock_request(self, method, url, **kwargs):
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": "success"},
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(httpx.Client, "request", mock_request)

    response = send_request(
        "GET",
        "https://example.com/api",
    )

    assert response.status_code == 200
    assert '"message": "success"' in response.body
    assert response.error is None
    assert response.elapsed_ms >= 0


def test_send_request_passes_request_configuration(monkeypatch):
    captured = {}

    def mock_request(self, method, url, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured.update(kwargs)

        return httpx.Response(
            201,
            json={"created": True},
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(httpx.Client, "request", mock_request)

    response = send_request(
        "POST",
        "https://example.com/api",
        headers={"X-Test": "demo"},
        params={"page": "2"},
        json_body={"name": "demo"},
        auth=("user", "password"),
    )

    assert response.status_code == 201
    assert captured["method"] == "POST"
    assert captured["headers"] == {"X-Test": "demo"}
    assert captured["params"] == {"page": "2"}
    assert captured["json"] == {"name": "demo"}
    assert captured["auth"] == ("user", "password")


def test_send_request_handles_http_error(monkeypatch):
    def mock_request(self, method, url, **kwargs):
        raise httpx.ConnectError(
            "Connection failed",
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(httpx.Client, "request", mock_request)

    response = send_request(
        "GET",
        "https://example.com/api",
    )

    assert response.status_code is None
    assert response.error is not None
    assert "ConnectError" in response.error
    assert response.body == ""


def test_send_request_handles_invalid_url():
    response = send_request(
        "GET",
        "not-a-valid-url",
    )

    assert response.status_code is None
    assert response.error is not None
