# API Toolkit

A terminal-based REST API client built with Python and Textual. Send HTTP requests, configure authentication, inspect responses, generate cURL commands, and save request configurations directly from a terminal interface.

## Features

- **HTTP requests:** Send GET, POST, PUT, PATCH, DELETE, and other HTTP methods.
- **Request configuration:** Configure URLs, query parameters, headers, and JSON request bodies.
- **Authentication:** Support Bearer tokens, API keys in headers or query parameters, and Basic authentication.
- **Response inspection:** View HTTP status codes, response headers, response bodies, and request timing.
- **cURL generation:** Generate cURL commands from configured requests.
- **Clipboard integration:** Copy generated cURL commands and request URLs.
- **Saved requests:** Save and reload request configurations locally.
- **Credential protection:** Redact sensitive URL query parameters and authentication credentials when saving requests.
- **Automated tests:** Test request handling, cURL generation, and request storage.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Installation

Clone the repository and enter the project directory:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd api-toolkit
```

Install the project dependencies and run the application:

```bash
uv sync
uv run python -m api_toolkit.app
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the actual URL of this repository.

## Usage

Launch the application:

```bash
uv run python -m api_toolkit.app
```

Configure the HTTP method and URL, then add any required query parameters, headers, authentication details, or JSON body. Send the request and inspect the returned response in the interface.

You can also generate a cURL command, copy the request URL, and save or reload request configurations.

## Authentication

The application supports the following authentication methods:

- **None:** Send a request without configured authentication.
- **Bearer token:** Include a token in the Authorization header.
- **API key:** Supply a key through a request header or URL query parameter.
- **Basic authentication:** Provide a username and password.

Use test credentials when experimenting with public APIs. Avoid committing real credentials or sensitive request data to version control.

## Running Tests

Run the automated test suite:

```bash
uv run pytest -v
```

Check code quality with Ruff:

```bash
uv run ruff check .
uv run ruff format --check .
```

## Local Data and Security

Saved request configurations are stored locally in:

```text
~/.config/api-toolkit/saved_requests/
```

Sensitive authentication information and URL query secrets are redacted when request configurations are saved. This reduces accidental credential exposure but should not be treated as a substitute for secure secret management.

Review saved configurations before sharing them, and avoid including real credentials in screenshots, issue reports, or commits.

## Technology Stack

- Python
- Textual
- httpx
- uv
- pytest
- Ruff

## Project Status

This project is intended as a lightweight terminal-based tool for working with REST APIs and learning API client development.
