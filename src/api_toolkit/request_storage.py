
import json
import re
from pathlib import Path
from typing import Any


SAVED_REQUESTS_DIR = (
    Path.home() / ".config" / "api-toolkit" / "saved_requests"
)


def _get_request_path(name: str) -> Path:
    """Convert a request name into a safe JSON filename."""

    cleaned_name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        name.strip(),
    ).strip("_")

    if not cleaned_name:
        raise ValueError(
            "Request name must contain letters or numbers."
        )

    return SAVED_REQUESTS_DIR / f"{cleaned_name}.json"


def save_request(
    name: str,
    configuration: dict[str, Any],
) -> Path:
    """Save a request configuration as a JSON file."""

    path = _get_request_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)

    saved_data = {
        "name": name.strip(),
        "configuration": configuration,
    }

    path.write_text(
        json.dumps(
            saved_data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return path


def load_request(name: str) -> dict[str, Any]:
    """Load a saved request configuration."""

    path = _get_request_path(name)

    if not path.is_file():
        raise FileNotFoundError(
            f"Saved request '{name}' was not found."
        )

    saved_data = json.loads(
        path.read_text(encoding="utf-8")
    )

    configuration = saved_data.get("configuration")

    if not isinstance(configuration, dict):
        raise ValueError(
            "Saved request contains an invalid configuration."
        )

    return configuration


def list_saved_requests() -> list[str]:
    """Return the names of saved requests."""

    if not SAVED_REQUESTS_DIR.is_dir():
        return []

    names = []

    for path in SAVED_REQUESTS_DIR.glob("*.json"):
        try:
            saved_data = json.loads(
                path.read_text(encoding="utf-8")
            )
            name = saved_data.get("name")

            if isinstance(name, str):
                names.append(name)
        except (OSError, json.JSONDecodeError):
            continue

    return sorted(names, key=str.casefold)
