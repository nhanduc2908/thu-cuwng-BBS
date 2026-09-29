from scripts.github_sync import _is_publishable


def test_github_sync_allows_project_source_and_docs():
    assert _is_publishable("app/modules/animals/repository.py")
    assert _is_publishable("tests/test_database.py")
    assert _is_publishable("scripts/github_sync.py")
    assert _is_publishable("README.md")
    assert _is_publishable(".gitignore")


def test_github_sync_excludes_local_or_generated_files():
    assert not _is_publishable("app/__pycache__/database.py")
    assert not _is_publishable("app/database.pyc")
    assert not _is_publishable("app/.env")
    assert not _is_publishable("app/secrets.py")
    assert not _is_publishable("uploads/intake-photo.jpg")
    assert not _is_publishable("data/pet_store.db")
    assert not _is_publishable(".env.example")
