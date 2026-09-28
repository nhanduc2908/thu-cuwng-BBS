import hashlib
import hmac
import secrets


PASSWORD_ITERATIONS = 600_000
PASSWORD_SALT_BYTES = 16


def hash_password(password: str) -> tuple[str, str]:
    if len(password) < 10:
        raise ValueError("Mật khẩu phải có ít nhất 10 ký tự.")
    if len(password) > 1024:
        raise ValueError("Mật khẩu vượt quá giới hạn cho phép.")
    salt = secrets.token_bytes(PASSWORD_SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return salt.hex(), derived_key.hex()


def verify_password(password: str, salt_hex: str, password_hash: str) -> bool:
    if len(password) > 1024:
        return False
    try:
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(password_hash)
    except ValueError:
        return False
    if len(salt) != PASSWORD_SALT_BYTES or len(expected) != hashlib.sha256().digest_size:
        return False
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return hmac.compare_digest(actual, expected)
