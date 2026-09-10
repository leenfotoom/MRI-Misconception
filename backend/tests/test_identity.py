from app.security import hash_password, token_hash, validate_password, verify_password


def test_argon2_password_round_trip():
    password = "StrongPass!123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_token_hash_is_deterministic_and_not_raw():
    raw = "very-secret-token"
    digest = token_hash(raw)
    assert digest != raw
    assert digest == token_hash(raw)
    assert len(digest) == 64
