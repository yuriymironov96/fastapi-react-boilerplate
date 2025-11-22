import pytest
from datetime import timedelta

from app.core.security import (
    create_access_token,
    get_password_hash,
    validate_token,
    verify_password,
)


@pytest.mark.asyncio
async def test_get_password_hash():
    """Test password hashing."""
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert len(hashed) > 0
    assert hashed.startswith("$2b$")  # bcrypt hash format


@pytest.mark.asyncio
async def test_get_password_hash_different_hashes():
    """Test that same password produces different hashes (due to salt)."""
    password = "testpassword123"
    hashed1 = get_password_hash(password)
    hashed2 = get_password_hash(password)

    # Hashes should be different due to salt, but both should verify
    assert hashed1 != hashed2
    assert verify_password(password, hashed1) is True
    assert verify_password(password, hashed2) is True


@pytest.mark.asyncio
async def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


@pytest.mark.asyncio
async def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "testpassword123"
    wrong_password = "wrongpassword"
    hashed = get_password_hash(password)

    assert verify_password(wrong_password, hashed) is False


@pytest.mark.asyncio
async def test_create_access_token():
    """Test creating an access token."""
    subject = "123"
    expires_delta = timedelta(hours=1)
    token = create_access_token(subject=subject, expires_delta=expires_delta)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_create_access_token_different_subjects():
    """Test that different subjects produce different tokens."""
    subject1 = "123"
    subject2 = "456"
    expires_delta = timedelta(hours=1)

    token1 = create_access_token(subject=subject1, expires_delta=expires_delta)
    token2 = create_access_token(subject=subject2, expires_delta=expires_delta)

    assert token1 != token2


@pytest.mark.asyncio
async def test_validate_token_valid():
    """Test validating a valid token."""
    subject = "123"
    expires_delta = timedelta(hours=1)
    token = create_access_token(subject=subject, expires_delta=expires_delta)

    validated_subject = await validate_token(token)

    assert validated_subject == subject


@pytest.mark.asyncio
async def test_validate_token_invalid():
    """Test validating an invalid token."""
    invalid_token = "invalid.token.here"

    validated_subject = await validate_token(invalid_token)

    assert validated_subject is None


@pytest.mark.asyncio
async def test_validate_token_expired():
    """Test validating an expired token."""
    subject = "123"
    # Create an expired token (negative expiry)
    expires_delta = timedelta(hours=-1)
    token = create_access_token(subject=subject, expires_delta=expires_delta)

    validated_subject = await validate_token(token)

    assert validated_subject is None


@pytest.mark.asyncio
async def test_validate_token_empty_string():
    """Test validating an empty token."""
    validated_subject = await validate_token("")

    assert validated_subject is None


@pytest.mark.asyncio
async def test_validate_token_malformed():
    """Test validating a malformed token."""
    malformed_tokens = [
        "not.a.valid.jwt.token",
        "header.payload",  # Missing signature
        "header",  # Only header
        "a.b.c.d",  # Too many parts
    ]

    for token in malformed_tokens:
        validated_subject = await validate_token(token)
        assert validated_subject is None


@pytest.mark.asyncio
async def test_token_roundtrip():
    """Test creating and validating a token in a roundtrip."""
    subject = "test_user_123"
    expires_delta = timedelta(hours=1)
    token = create_access_token(subject=subject, expires_delta=expires_delta)

    validated_subject = await validate_token(token)

    assert validated_subject == subject

