
import asyncio
import json

import httpx
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
    TextArea,
)

from api_toolkit.http_client import send_request
from api_toolkit.curl_generator import build_curl_command


class ApiToolkitApp(App):
    """Interactive terminal interface for a generic REST API client."""

    TITLE = "API Toolkit"
    SUB_TITLE = "Generic REST API Client"

    CSS = """
    Screen {
        padding: 0 2 1 2;
    }

    Header {
        height: 1;
        margin-bottom: 1;
    }

    #request-bar {
        height: 3;
        margin-top: 1;
        margin-bottom: 1;
    }

    #method {
        width: 12;
        margin-right: 1;
    }

    #url {
        width: 1fr;
        margin-right: 1;
    }

    #send {
        width: 12;
    }

    #curl-toolbar {
        height: 3;
        margin-bottom: 1;
    }

    #generate-curl {
        width: 1fr;
        margin-right: 1;
    }

    #copy-curl {
        width: 1fr;
        margin-right: 1;
    }

    #copy-url {
        width: 1fr;
    }

    #curl-command {
        height: 5;
        margin-bottom: 0;
    }

    #curl-warning {
        height: 1;
        margin-bottom: 1;
    }

    #workspace {
        height: 1fr;
    }

    #request-panel {
        width: 1fr;
        border: round $primary;
        padding: 1;
        margin-right: 1;
    }

    #response-panel {
        width: 2fr;
        border: round $primary;
        padding: 1;
    }

    .section-title {
        text-style: bold;
        margin-bottom: 1;
    }

    .field-label {
        margin-top: 1;
        margin-bottom: 1;
    }

    #params {
        height: 7;
    }

    #headers {
        height: 9;
    }

    #body {
        height: 12;
    }

    #auth-type {
        margin-bottom: 1;
    }

    .auth-input {
        margin-bottom: 1;
    }

    #status {
        margin-bottom: 1;
    }

    #response-content {
        height: 1fr;
    }

    #response-headers {
        height: auto;
        margin-bottom: 1;
    }

    #response-body {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="request-bar"):
            yield Select(
                [
                    ("GET", "GET"),
                    ("POST", "POST"),
                    ("PUT", "PUT"),
                    ("PATCH", "PATCH"),
                    ("DELETE", "DELETE"),
                ],
                value="GET",
                id="method",
                allow_blank=False,
            )

            yield Input(
                placeholder="https://httpbin.org/get",
                id="url",
            )

            yield Button(
                "Send",
                id="send",
                variant="primary",
            )

        # These controls are outside the scrollable panels.
        with Horizontal(id="curl-toolbar"):
            yield Button(
                "Generate cURL",
                id="generate-curl",
            )
            yield Button(
                "Copy cURL",
                id="copy-curl",
            )
            yield Button(
                "Copy URL",
                id="copy-url",
            )

        yield TextArea(
            "",
            id="curl-command",
            read_only=True,
        )

        yield Static(
            "Generate a command, or copy the request URL directly.",
            id="curl-warning",
        )

        with Horizontal(id="workspace"):
            with VerticalScroll(id="request-panel"):
                yield Label("REQUEST", classes="section-title")

                yield Label(
                    "Query parameters (JSON)",
                    classes="field-label",
                )
                yield TextArea(
                    '{\n  "page": "2",\n  "limit": "10"\n}',
                    id="params",
                    language="json",
                )

                yield Label(
                    "Headers (JSON)",
                    classes="field-label",
                )
                yield TextArea(
                    '{\n  "Accept": "application/json"\n}',
                    id="headers",
                    language="json",
                )

                yield Label(
                    "Authentication",
                    classes="field-label",
                )
                yield Select(
                    [
                        ("None", "none"),
                        ("Bearer token", "bearer"),
                        ("API key", "api_key"),
                        ("Basic authentication", "basic"),
                    ],
                    value="none",
                    id="auth-type",
                    allow_blank=False,
                )

                yield Label(
                    "Bearer token",
                    classes="field-label",
                )
                yield Input(
                    placeholder="Enter access token",
                    password=True,
                    id="bearer-token",
                    classes="auth-input",
                )

                yield Label(
                    "API key name",
                    classes="field-label",
                )
                yield Input(
                    placeholder="e.g. X-API-Key",
                    id="api-key-name",
                    classes="auth-input",
                )

                yield Label(
                    "API key value",
                    classes="field-label",
                )
                yield Input(
                    placeholder="Enter API key",
                    password=True,
                    id="api-key-value",
                    classes="auth-input",
                )

                yield Label(
                    "API key location",
                    classes="field-label",
                )
                yield Select(
                    [
                        ("Request header", "header"),
                        ("Query parameter", "query"),
                    ],
                    value="header",
                    id="api-key-location",
                    allow_blank=False,
                )

                yield Label(
                    "Username",
                    classes="field-label",
                )
                yield Input(
                    placeholder="Username",
                    id="basic-username",
                    classes="auth-input",
                )

                yield Label(
                    "Password",
                    classes="field-label",
                )
                yield Input(
                    placeholder="Password",
                    password=True,
                    id="basic-password",
                    classes="auth-input",
                )

                yield Label(
                    "Request body (JSON)",
                    classes="field-label",
                )
                yield TextArea(
                    "",
                    id="body",
                    language="json",
                )

            with Vertical(id="response-panel"):
                yield Label("RESPONSE", classes="section-title")

                yield Static(
                    "Status: Not sent",
                    id="status",
                )

                with VerticalScroll(id="response-content"):
                    yield Label("Response headers")

                    yield Static(
                        "No response yet.",
                        id="response-headers",
                    )

                    yield Label("Response body")

                    yield Static(
                        "No response yet.",
                        id="response-body",
                    )

        yield Footer()

    @staticmethod
    def parse_json_object(
        raw_text: str,
        field_name: str,
    ) -> dict[str, str]:
        """Parse a JSON object containing string keys and values."""

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{field_name}: invalid JSON at line {exc.lineno}, "
                f"column {exc.colno}."
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(f"{field_name} must be a JSON object.")

        for key, value in data.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError(
                    f"{field_name}: keys and values must be strings."
                )

        return data

    @staticmethod
    def parse_json_body(raw_text: str) -> dict | list | None:
        """Parse an optional JSON object or array."""

        if not raw_text.strip():
            return None

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Request body: invalid JSON at line {exc.lineno}, "
                f"column {exc.colno}."
            ) from exc

        if not isinstance(data, (dict, list)):
            raise ValueError(
                "Request body must be a JSON object or array."
            )

        return data

    def build_authentication(
        self,
        params: dict[str, str],
        headers: dict[str, str],
    ) -> tuple[
        tuple[str, str] | None,
        dict[str, str],
        dict[str, str],
    ]:
        """Build authentication settings for the request."""

        auth_type = self.query_one("#auth-type", Select).value

        if auth_type == "bearer":
            token = self.query_one(
                "#bearer-token", Input
            ).value.strip()

            if not token:
                raise ValueError("Please enter a Bearer token.")

            headers = dict(headers)
            headers["Authorization"] = f"Bearer {token}"

        elif auth_type == "api_key":
            name = self.query_one(
                "#api-key-name", Input
            ).value.strip()
            value = self.query_one(
                "#api-key-value", Input
            ).value

            if not name or not value:
                raise ValueError(
                    "Enter both the API key name and value."
                )

            location = self.query_one(
                "#api-key-location", Select
            ).value

            params = dict(params)
            headers = dict(headers)

            if location == "header":
                headers[name] = value
            elif location == "query":
                params[name] = value
            else:
                raise ValueError("Unsupported API key location.")

        elif auth_type == "basic":
            username = self.query_one(
                "#basic-username", Input
            ).value
            password = self.query_one(
                "#basic-password", Input
            ).value

            if not username:
                raise ValueError("Please enter a username.")

            return (username, password), params, headers

        elif auth_type != "none":
            raise ValueError("Unsupported authentication method.")

        return None, params, headers

    def get_request_configuration(
        self,
    ) -> tuple[
        str,
        str,
        dict[str, str],
        dict[str, str],
        dict | list | None,
        tuple[str, str] | None,
    ]:
        """Read and validate the current request configuration."""

        method = self.query_one("#method", Select).value
        url = self.query_one("#url", Input).value.strip()

        if not isinstance(method, str):
            raise ValueError("Please select an HTTP method.")

        if not url:
            raise ValueError("Please enter a URL.")

        try:
            parsed_url = httpx.URL(url)
        except httpx.InvalidURL as exc:
            raise ValueError(f"Invalid URL: {exc}") from exc

        if parsed_url.scheme not in ("http", "https") or not parsed_url.host:
            raise ValueError("Enter a valid HTTP or HTTPS URL.")

        params = self.parse_json_object(
            self.query_one("#params", TextArea).text,
            "Query parameters",
        )

        headers = self.parse_json_object(
            self.query_one("#headers", TextArea).text,
            "Headers",
        )

        json_body = self.parse_json_body(
            self.query_one("#body", TextArea).text
        )

        auth, params, headers = self.build_authentication(
            params,
            headers,
        )

        if method in ("GET", "DELETE"):
            json_body = None

        return method, url, params, headers, json_body, auth

    @on(Button.Pressed, "#send")
    def on_send_pressed(self) -> None:
        try:
            method, url, params, headers, json_body, auth = (
                self.get_request_configuration()
            )
        except ValueError as exc:
            self.query_one("#status", Static).update(
                f"Input error: {exc}"
            )
            return

        self.query_one("#status", Static).update(
            "Sending request..."
        )
        self.query_one("#response-headers", Static).update(
            "Waiting for response..."
        )
        self.query_one("#response-body", Static).update(
            "Waiting for response..."
        )

        self.send_request_worker(
            method,
            url,
            params,
            headers,
            json_body,
            auth,
        )

    @on(Button.Pressed, "#generate-curl")
    def on_generate_curl_pressed(self) -> None:
        try:
            method, url, params, headers, json_body, auth = (
                self.get_request_configuration()
            )

            command = build_curl_command(
                method,
                url,
                params=params,
                headers=headers,
                json_body=json_body,
                auth=auth,
            )

            self.query_one("#curl-command", TextArea).text = command
            self.query_one("#curl-warning", Static).update(
                "Generated. Check for credentials before sharing."
            )

        except (ValueError, httpx.InvalidURL) as exc:
            self.query_one("#curl-warning", Static).update(
                f"Cannot generate cURL: {exc}"
            )

    @on(Button.Pressed, "#copy-curl")
    def on_copy_curl_pressed(self) -> None:
        command = self.query_one("#curl-command", TextArea).text

        if not command.strip():
            self.query_one("#curl-warning", Static).update(
                "Click Generate cURL first."
            )
            return

        try:
            self.copy_to_clipboard(command)
            self.query_one("#curl-warning", Static).update(
                "cURL copy requested. Try pasting into your terminal."
            )
        except Exception as exc:
            self.query_one("#curl-warning", Static).update(
                f"Clipboard failed: {exc}. Select and copy manually."
            )

    @on(Button.Pressed, "#copy-url")
    def on_copy_url_pressed(self) -> None:
        try:
            url = self.query_one("#url", Input).value.strip()

            if not url:
                raise ValueError("Please enter a URL.")

            params = self.parse_json_object(
                self.query_one("#params", TextArea).text,
                "Query parameters",
            )

            # Include the API key when configured as a query parameter.
            auth_type = self.query_one(
                "#auth-type", Select
            ).value

            if (
                auth_type == "api_key"
                and self.query_one(
                    "#api-key-location", Select
                ).value == "query"
            ):
                name = self.query_one(
                    "#api-key-name", Input
                ).value.strip()
                value = self.query_one(
                    "#api-key-value", Input
                ).value

                if not name or not value:
                    raise ValueError(
                        "Enter both the API key name and value."
                    )

                params[name] = value

            parsed_url = httpx.URL(url)

            if (
                parsed_url.scheme not in ("http", "https")
                or not parsed_url.host
            ):
                raise ValueError(
                    "Enter a valid HTTP or HTTPS URL."
                )

            complete_url = str(
                parsed_url.copy_merge_params(params)
            )

            self.copy_to_clipboard(complete_url)

            self.query_one("#curl-warning", Static).update(
                "URL copy requested. Try pasting it into your editor."
            )

        except (ValueError, httpx.InvalidURL) as exc:
            self.query_one("#curl-warning", Static).update(
                f"Cannot copy URL: {exc}"
            )
        except Exception as exc:
            self.query_one("#curl-warning", Static).update(
                f"Clipboard failed: {exc}. Copy the URL manually."
            )

    @work(exclusive=True)
    async def send_request_worker(
        self,
        method: str,
        url: str,
        params: dict[str, str],
        headers: dict[str, str],
        json_body: dict | list | None,
        auth: tuple[str, str] | None,
    ) -> None:
        response = await asyncio.to_thread(
            send_request,
            method,
            url,
            params=params,
            headers=headers,
            json_body=json_body,
            auth=auth,
        )

        if response.error:
            status_text = (
                f"Request failed | {response.elapsed_ms:.2f} ms\n"
                f"{response.error}"
            )
        else:
            status_text = (
                f"HTTP {response.status_code} | "
                f"{response.elapsed_ms:.2f} ms"
            )

        self.query_one("#status", Static).update(status_text)

        formatted_headers = json.dumps(
            response.headers,
            indent=2,
            ensure_ascii=False,
        )

        self.query_one("#response-headers", Static).update(
            formatted_headers
            if response.headers
            else "No headers available."
        )

        self.query_one("#response-body", Static).update(
            response.body or "(Empty response body)"
        )


if __name__ == "__main__":
    ApiToolkitApp().run()
