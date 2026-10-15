
import asyncio
import json

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static
from textual import work

from api_toolkit.http_client import send_request


class ApiToolkitApp(App):
    """Interactive terminal interface for a generic REST API client."""

    TITLE = "API Toolkit"
    SUB_TITLE = "Generic REST API Client"

    CSS = """
    Screen {
        padding: 1 2;
    }

    #request-bar {
        height: 3;
        margin-bottom: 1;
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

    #status {
        margin-bottom: 1;
    }

    #response-headers {
        height: 8;
        overflow-y: auto;
        margin-bottom: 1;
    }

    #response {
        height: 1fr;
        overflow-y: auto;
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
            yield Button("Send", id="send", variant="primary")

        with Horizontal(id="workspace"):
            with Vertical(id="request-panel"):
                yield Label("REQUEST", classes="section-title")
                yield Static(
                    "HTTP request builder\n\n"
                    "Current features:\n"
                    "- HTTP method selection\n"
                    "- URL input\n"
                    "- Send request\n\n"
                    "Next: query parameters, headers, "
                    "authentication and JSON body."
                )

            with Vertical(id="response-panel"):
                yield Label("RESPONSE", classes="section-title")
                yield Static("Status: Not sent", id="status")
                yield Label("Response headers")
                yield Static("No response yet.", id="response-headers")
                yield Label("Response body")
                yield Static("No response yet.", id="response")

        yield Footer()

    @on(Button.Pressed, "#send")
    def on_send_pressed(self) -> None:
        method = self.query_one("#method", Select).value
        url = self.query_one("#url", Input).value.strip()

        if not isinstance(method, str):
            return

        if not url:
            self.query_one("#status", Static).update(
                "Error: Please enter a URL."
            )
            return

        self.query_one("#status", Static).update("Sending request...")
        self.query_one("#response-headers", Static).update(
            "Waiting for response..."
        )
        self.query_one("#response", Static).update(
            "Waiting for response..."
        )

        self.send_request_worker(method, url)

    @work(exclusive=True)
    async def send_request_worker(self, method: str, url: str) -> None:
        response = await asyncio.to_thread(
            send_request,
            method,
            url,
        )

        if response.error:
            self.query_one("#status", Static).update(
                f"Request failed | {response.elapsed_ms:.2f} ms\n"
                f"{response.error}"
            )
        else:
            self.query_one("#status", Static).update(
                f"HTTP {response.status_code} | "
                f"{response.elapsed_ms:.2f} ms"
            )

        formatted_headers = json.dumps(
            response.headers,
            indent=2,
            ensure_ascii=False,
        )

        self.query_one("#response-headers", Static).update(
            formatted_headers if response.headers else "No headers available."
        )

        self.query_one("#response", Static).update(
            response.body or "(Empty response body)"
        )


if __name__ == "__main__":
    ApiToolkitApp().run()
