import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.user import UserCreate


@pytest.fixture
async def test_user(test_db_session: AsyncSession) -> User:
    """Create a test user in the database."""
    from app.crud import create_user

    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="User",
    )
    user = await create_user(session=test_db_session, user_create=user_create)
    return user


@pytest.fixture
async def test_superuser(test_db_session: AsyncSession) -> User:
    """Create a test superuser in the database."""
    from app.crud import create_user
    from app.schemas.user import SuperUserCreate

    user_create = SuperUserCreate(
        username="superuser",
        email="super@example.com",
        password="superpassword123",
        first_name="Super",
        last_name="User",
        is_superuser=True,
    )
    user = await create_user(session=test_db_session, user_create=user_create)
    return user


@pytest.fixture
def user_create_data() -> dict:
    """Provide test user creation data."""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123",
        "first_name": "New",
        "last_name": "User",
    }

