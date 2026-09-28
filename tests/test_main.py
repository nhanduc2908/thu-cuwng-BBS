from pathlib import Path

import main


def test_database_path_uses_local_app_data(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert main.database_path() == (
        tmp_path / "PetStoreManagement" / "pet_store.db"
    )


def test_database_path_has_windows_fallback(monkeypatch, tmp_path):
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setattr(main.sys, "platform", "win32")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert main.database_path() == (
        tmp_path / "AppData" / "Local" / "PetStoreManagement" / "pet_store.db"
    )
