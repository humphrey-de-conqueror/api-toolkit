import pytest

from api_toolkit import request_storage


@pytest.fixture
def storage_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(
        request_storage,
        "SAVED_REQUESTS_DIR",
        tmp_path / "saved_requests",
    )
    return tmp_path / "saved_requests"


def test_save_and_load_request(storage_directory):
    configuration = {
        "method": "GET",
        "url": "https://httpbin.org/get",
        "params": {"page": "2"},
    }

    request_storage.save_request("demo", configuration)

    assert request_storage.load_request("demo") == configuration


def test_list_saved_requests(storage_directory):
    request_storage.save_request("beta", {"method": "GET"})
    request_storage.save_request("alpha", {"method": "POST"})

    assert request_storage.list_saved_requests() == [
        "alpha",
        "beta",
    ]


def test_load_missing_request_raises_error(storage_directory):
    with pytest.raises(FileNotFoundError):
        request_storage.load_request("missing")


def test_empty_request_name_is_rejected(storage_directory):
    with pytest.raises(ValueError):
        request_storage.save_request("   ", {"method": "GET"})


def test_request_name_is_sanitized(storage_directory):
    request_storage.save_request(
        "../demo",
        {"method": "GET"},
    )

    assert request_storage.load_request("../demo") == {
        "method": "GET",
    }
    assert (
        storage_directory.resolve()
        in (storage_directory / "demo.json").resolve().parents
    )
