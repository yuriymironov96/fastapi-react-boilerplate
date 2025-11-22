import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import sessionmanager
from app.models import User
from app.schemas.user import SuperUserCreate
from app.core.config import settings
from app.crud import create_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db(session: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    result = await session.execute(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    )
    user = result.scalar_one_or_none()
    if not user:
        logger.info("Creating superuser")
        user_in = SuperUserCreate(
            username=settings.FIRST_SUPERUSER,
            first_name="Admin",
            last_name="Admin",
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = await create_user(session=session, user_create=user_in)
        logger.info("Superuser created")
    else:
        logger.info("Superuser already exists: %s", user)


async def init() -> None:
    async with sessionmanager.session() as session:
        await init_db(session)


async def main() -> None:
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
