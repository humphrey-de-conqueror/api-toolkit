
import json
import shlex

import httpx


def build_curl_command(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    json_body: dict | list | None = None,
    auth: tuple[str, str] | None = None,
) -> str:
    """Build a shell-safe cURL command matching the configured request."""

    request_url = str(httpx.URL(url).copy_merge_params(params or {}))

    parts = [
        "curl",
        "--request",
        shlex.quote(method),
        "--url",
        shlex.quote(request_url),
    ]

    request_headers = dict(headers or {})

    if json_body is not None and not any(
        key.lower() == "content-type"
        for key in request_headers
    ):
        request_headers["Content-Type"] = "application/json"

    for name, value in request_headers.items():
        parts.extend(
            ["--header", shlex.quote(f"{name}: {value}")]
        )

    if auth is not None:
        username, password = auth
        parts.extend(
            ["--user", shlex.quote(f"{username}:{password}")]
        )

    if json_body is not None:
        body_text = json.dumps(
            json_body,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        parts.extend(["--data-raw", shlex.quote(body_text)])

    return " \\\n  ".join(parts)
