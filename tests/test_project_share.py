from http import HTTPStatus
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener

import pytest

from app.database import Database
from app.project_share import ProjectShareServer


@pytest.fixture
def project_share(tmp_path):
    database_path = tmp_path / "petcare.db"
    database = Database(database_path)
    admin_id = database.create_default_admin()
    database.set_actor(admin_id)
    viewer_id = database.create_user(
        "viewer", "Project Viewer", "Viewer-password-123", "REPORT_ANALYST"
    )

    project_root = tmp_path / "project"
    html_root = project_root / "HTML"
    html_root.mkdir(parents=True)
    (project_root / "SC.HTML").write_text(
        "<!doctype html><html><body>Project report</body></html>",
        encoding="utf-8",
    )
    (html_root / "index.html").write_text(
        "<!doctype html><html><body>Website content</body></html>",
        encoding="utf-8",
    )
    (html_root / "catalog.json").write_text('{"example": true}', encoding="utf-8")
    (project_root / "secret.json").write_text('{"secret": true}', encoding="utf-8")

    server = ProjectShareServer(database_path, project_root)
    base_url = server.start()
    try:
        yield database, viewer_id, server, base_url
    finally:
        server.stop()
        database.close()


def _request(url, *, opener=None, method="GET", data=None, headers=None):
    request = Request(url, data=data, headers=headers or {}, method=method)
    try:
        response = (opener or build_opener()).open(request, timeout=3)
        return response.status, response.read(), response.headers
    except HTTPError as error:
        return error.code, error.read(), error.headers


def _login(base_url, username="viewer", password="Viewer-password-123"):
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    status, _, _ = _request(f"{base_url}/share/login", opener=opener)
    assert status == HTTPStatus.METHOD_NOT_ALLOWED
    body = urlencode({"username": username, "password": password}).encode()
    status, _, _ = _request(
        f"{base_url}/share/login",
        opener=opener,
        method="POST",
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": base_url,
        },
    )
    return opener, status


def test_requires_viewer_login_and_serves_only_allowed_static_files(project_share):
    _, _, _, base_url = project_share

    status, body, headers = _request(f"{base_url}/SC.HTML")
    assert status == HTTPStatus.UNAUTHORIZED
    assert b"Ch\xe1\xba\xbf \xc4\x91\xe1\xbb\x99 quan s\xc3\xa1t" in body
    assert headers["Cache-Control"] == "no-store"

    opener, status = _login(base_url)
    assert status == HTTPStatus.OK
    assert opener.open(f"{base_url}/SC.HTML", timeout=3).status == HTTPStatus.OK
    assert b"Tho\xc3\xa1t ch\xe1\xba\xbf \xc4\x91\xe1\xbb\x99 quan s\xc3\xa1t" in (
        opener.open(f"{base_url}/SC.HTML", timeout=3).read()
    )
    assert opener.open(f"{base_url}/HTML/catalog.json", timeout=3).read() == (
        b'{"example": true}'
    )

    for path in (
        "/api/customers",
        "/customer/1",
        "/HTML/../../secret.json",
        "/secret.json",
        "/HTML/catalog.json/extra",
    ):
        status, _, _ = _request(f"{base_url}{path}", opener=opener)
        assert status == HTTPStatus.NOT_FOUND


def test_login_role_gating_and_session_revocation(project_share):
    database, viewer_id, _, base_url = project_share

    _, status = _login(base_url, username="admin", password="admin")
    assert status == HTTPStatus.UNAUTHORIZED

    opener, status = _login(base_url)
    assert status == HTTPStatus.OK
    database.set_user_active(viewer_id, False, actor_id=1)
    status, _, _ = _request(f"{base_url}/SC.HTML", opener=opener)
    assert status == HTTPStatus.UNAUTHORIZED


def test_share_rejects_write_methods_and_bad_login_origin(project_share):
    _, _, _, base_url = project_share
    opener, status = _login(base_url)
    assert status == HTTPStatus.OK

    for method in ("PUT", "PATCH", "DELETE", "OPTIONS"):
        status, _, _ = _request(
            f"{base_url}/HTML/index.html",
            opener=opener,
            method=method,
            data=b"write attempt",
        )
        assert status == HTTPStatus.METHOD_NOT_ALLOWED

    body = urlencode(
        {"username": "viewer", "password": "Viewer-password-123"}
    ).encode()
    status, _, _ = _request(
        f"{base_url}/share/login",
        method="POST",
        data=body,
        headers={"Origin": "https://attacker.example"},
    )
    assert status == HTTPStatus.FORBIDDEN


def test_malformed_login_form_returns_bad_request(project_share):
    _, _, _, base_url = project_share
    body = urlencode(
        [("username", "viewer"), ("password", "pw"), ("extra", "1"),
         ("extra2", "2"), ("extra3", "3")]
    ).encode()

    status, _, _ = _request(
        f"{base_url}/share/login",
        method="POST",
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": base_url,
        },
    )
    assert status == HTTPStatus.BAD_REQUEST
