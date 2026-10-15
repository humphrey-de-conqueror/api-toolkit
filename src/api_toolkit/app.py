
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Label, Select, Static


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
        margin-top: 1;
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
                placeholder="Enter API URL, e.g. https://httpbin.org/get",
                id="url",
            )

        with Horizontal(id="workspace"):
            with Vertical(id="request-panel"):
                yield Label("REQUEST", classes="section-title")
                yield Static(
                    "Next: query parameters, headers, authentication, "
                    "and JSON body."
                )

            with Vertical(id="response-panel"):
                yield Label("RESPONSE", classes="section-title")
                yield Static(
                    "No request sent yet.",
                    id="response",
                )
                yield Static(
                    "Status: Not sent",
                    id="status",
                )

        yield Footer()


if __name__ == "__main__":
    ApiToolkitApp().run()
