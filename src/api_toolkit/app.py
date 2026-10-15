
import asyncio
import json

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
        margin-bottom: 2;
    }

    #method {
        width: 16;
        margin-right: 1;
    }

    #url {
        width: 1fr;
        margin-right: 1;
    }

    #send {
        width: 14;
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

        # Row 2: HTTP method, URL and Send button.
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
            yield Button("Send", id="send", variant="primary")

        # Row 3: Request editor and independently scrollable response.
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

                yield Label("Headers (JSON)", classes="field-label")
                yield TextArea(
                    '{\n  "Accept": "application/json"\n}',
                    id="headers",
                    language="json",
                )

                yield Label("Request body (JSON)", classes="field-label")
                yield TextArea(
                    "",
                    id="body",
                    language="json",
                )
                yield Static(
                    "Used for POST, PUT and PATCH.",
                )

            with Vertical(id="response-panel"):
                yield Label("RESPONSE", classes="section-title")
                yield Static("Status: Not sent", id="status")

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
        """Parse a JSON object with string keys and values."""

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

    @on(Select.Changed, "#method")
    def on_method_changed(self, event: Select.Changed) -> None:
        """Clear the body when switching to a method that does not use it."""

        if event.value in ("GET", "DELETE"):
            self.query_one("#body", TextArea).load_text("")

    @on(Button.Pressed, "#send")
    def on_send_pressed(self) -> None:
        method = self.query_one("#method", Select).value
        url = self.query_one("#url", Input).value.strip()

        if not isinstance(method, str):
            return

        if not url:
            self.query_one("#status", Static).update(
                "Input error: Please enter a URL."
            )
            return

        try:
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
        except ValueError as exc:
            self.query_one("#status", Static).update(
                f"Input error: {exc}"
            )
            return

        if method in ("GET", "DELETE"):
            json_body = None

        self.query_one("#status", Static).update("Sending request...")
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
        )

    @work(exclusive=True)
    async def send_request_worker(
        self,
        method: str,
        url: str,
        params: dict[str, str],
        headers: dict[str, str],
        json_body: dict | list | None,
    ) -> None:
        response = await asyncio.to_thread(
            send_request,
            method,
            url,
            params=params,
            headers=headers,
            json_body=json_body,
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
