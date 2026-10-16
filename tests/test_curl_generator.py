import shlex

from api_toolkit.curl_generator import build_curl_command


def test_build_curl_command_includes_method_url_and_params():
    command = build_curl_command(
        "GET",
        "https://httpbin.org/get",
        params={"page": "2"},
    )

    assert "curl" in command
    assert "--request" in command
    assert "GET" in command
    assert "page=2" in command
    assert "https://httpbin.org/get" in command


def test_build_curl_command_includes_headers():
    command = build_curl_command(
        "GET",
        "https://httpbin.org/get",
        headers={"Accept": "application/json"},
    )

    assert "Accept: application/json" in command


def test_build_curl_command_includes_json_body():
    command = build_curl_command(
        "POST",
        "https://httpbin.org/post",
        json_body={"name": "test"},
    )

    assert "--data-raw" in command
    assert "Content-Type: application/json" in command
    assert '"name":"test"' in command


def test_build_curl_command_includes_basic_auth():
    command = build_curl_command(
        "GET",
        "https://httpbin.org/get",
        auth=("demo", "secret"),
    )

    assert "--user" in command
    assert shlex.quote("demo:secret") in command


def test_build_curl_command_quotes_special_characters():
    command = build_curl_command(
        "GET",
        "https://httpbin.org/get",
        headers={"X-Test": "value with spaces"},
    )

    assert shlex.quote("X-Test: value with spaces") in command
