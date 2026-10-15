
import json
import time
from dataclasses import dataclass

import httpx


@dataclass
class ApiResponse:
    status_code: int | None
    elapsed_ms: float
    headers: dict[str, str]
    body: str
    error: str | None = None


def send_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    json_body: dict | list | None = None,
    timeout: float = 15.0,
) -> ApiResponse:
    """Send an HTTP request and return a structured response."""

    start = time.perf_counter()

    try:
        with httpx.Client(
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
            )

        elapsed_ms = (time.perf_counter() - start) * 1000

        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            try:
                body = json.dumps(
                    response.json(),
                    indent=2,
                    ensure_ascii=False,
                )
            except ValueError:
                body = response.text
        else:
            body = response.text

        return ApiResponse(
            status_code=response.status_code,
            elapsed_ms=elapsed_ms,
            headers=dict(response.headers),
            body=body,
        )

    except (httpx.HTTPError, ValueError) as exc:
        return ApiResponse(
            status_code=None,
            elapsed_ms=(time.perf_counter() - start) * 1000,
            headers={},
            body="",
            error=f"{type(exc).__name__}: {exc}",
        )
