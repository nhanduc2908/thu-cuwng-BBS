from __future__ import annotations

from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

from app import remote_storefront_bridge
from app.remote_storefront_bridge import RemoteStorefrontBridge


class _FakeResponse:
    status_code = 200
    headers = {"content-type": "application/json"}
    content = b'{"products":[]}'


class _FakeClient:
    requested: list[tuple[str, str, object]] = []

    def __init__(self, **_kwargs) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def request(self, method: str, path: str, json=None) -> _FakeResponse:
        self.requested.append((method, path, json))
        return _FakeResponse()


def test_remote_storefront_serves_files_and_proxies_only_storefront_api(
    tmp_path: Path, monkeypatch
) -> None:
    web_root = tmp_path / "HTML"
    store_root = web_root / "store"
    store_root.mkdir(parents=True)
    (store_root / "index.html").write_text(
        "<h1>PetCare Storefront</h1>", encoding="utf-8"
    )
    monkeypatch.setattr(remote_storefront_bridge.httpx, "Client", _FakeClient)
    _FakeClient.requested = []
    bridge = RemoteStorefrontBridge("https://api.example.test", web_root, port=0)
    bridge.start()

    try:
        with urlopen(f"{bridge.base_url}/{quote('store')}/index.html") as response:
            assert response.status == 200
            assert b"PetCare Storefront" in response.read()

        with urlopen(f"{bridge.base_url}/api/storefront/catalog") as response:
            assert response.status == 200
            assert response.read() == b'{"products":[]}'

        assert _FakeClient.requested == [
            ("GET", "/api/storefront/catalog", None)
        ]
    finally:
        bridge.stop()
