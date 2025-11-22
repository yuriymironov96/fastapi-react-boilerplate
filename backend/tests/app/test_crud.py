import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import authenticate, create_user, get_current_user, get_user_by_username
from app.models import User
from app.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_user(test_db_session: AsyncSession, user_create_data: dict):
    """Test creating a new user."""
    user_create = UserCreate(**user_create_data)
    user = await create_user(session=test_db_session, user_create=user_create)

    assert user.id is not None
    assert user.username == user_create_data["username"]
    assert user.email == user_create_data["email"]
    assert user.first_name == user_create_data["first_name"]
    assert user.last_name == user_create_data["last_name"]
    assert user.hashed_password != user_create_data["password"]  # Should be hashed
    assert user.is_superuser is False  # Default value


@pytest.mark.asyncio
async def test_create_user_with_superuser(test_db_session: AsyncSession):
    """Test creating a superuser."""
    from app.schemas.user import SuperUserCreate

    user_create = SuperUserCreate(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
        is_superuser=True,
    )
    user = await create_user(session=test_db_session, user_create=user_create)

    assert user.is_superuser is True


@pytest.mark.asyncio
async def test_get_user_by_username_existing(
    test_db_session: AsyncSession, test_user: User
):
    """Test getting a user by username when user exists."""
    found_user = await get_user_by_username(
        session=test_db_session, username=test_user.username
    )

    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.username == test_user.username
    assert found_user.email == test_user.email


@pytest.mark.asyncio
async def test_get_user_by_username_nonexistent(test_db_session: AsyncSession):
    """Test getting a user by username when user doesn't exist."""
    found_user = await get_user_by_username(
        session=test_db_session, username="nonexistent"
    )

    assert found_user is None


@pytest.mark.asyncio
async def test_authenticate_success(
    test_db_session: AsyncSession, test_user: User
):
    """Test authentication with correct credentials."""
    authenticated_user = await authenticate(
        session=test_db_session,
        username=test_user.username,
        password="testpassword123",
    )

    assert authenticated_user is not None
    assert authenticated_user.id == test_user.id
    assert authenticated_user.username == test_user.username


@pytest.mark.asyncio
async def test_authenticate_wrong_password(
    test_db_session: AsyncSession, test_user: User
):
    """Test authentication with wrong password."""
    authenticated_user = await authenticate(
        session=test_db_session,
        username=test_user.username,
        password="wrongpassword",
    )

    assert authenticated_user is None


@pytest.mark.asyncio
async def test_authenticate_nonexistent_user(test_db_session: AsyncSession):
    """Test authentication with non-existent user."""
    authenticated_user = await authenticate(
        session=test_db_session,
        username="nonexistent",
        password="somepassword",
    )

    assert authenticated_user is None


@pytest.mark.asyncio
async def test_get_current_user_valid_token(
    test_db_session: AsyncSession, test_user: User
):
    """Test getting current user with valid token."""
    from app.core.security import create_access_token
    from datetime import timedelta

    token = create_access_token(subject=str(test_user.id), expires_delta=timedelta(hours=1))
    current_user = await get_current_user(session=test_db_session, token=token)

    assert current_user is not None
    assert current_user.id == test_user.id
    assert current_user.username == test_user.username


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(test_db_session: AsyncSession):
    """Test getting current user with invalid token."""
    current_user = await get_current_user(session=test_db_session, token="invalid_token")

    assert current_user is None


@pytest.mark.asyncio
async def test_get_current_user_expired_token(
    test_db_session: AsyncSession, test_user: User
):
    """Test getting current user with expired token."""
    from app.core.security import create_access_token
    from datetime import timedelta

    # Create an expired token (negative expiry)
    token = create_access_token(
        subject=str(test_user.id), expires_delta=timedelta(hours=-1)
    )
    current_user = await get_current_user(session=test_db_session, token=token)

    assert current_user is None


@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(test_db_session: AsyncSession):
    """Test getting current user with token for non-existent user."""
    from app.core.security import create_access_token
    from datetime import timedelta

    # Create token for user ID that doesn't exist
    token = create_access_token(subject="99999", expires_delta=timedelta(hours=1))
    current_user = await get_current_user(session=test_db_session, token=token)

    assert current_user is None

