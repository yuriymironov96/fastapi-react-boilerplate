from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash, validate_token, verify_password
from app.models import User
from app.schemas.user import UserCreate


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    user_create_dict = user_create.model_dump()
    hashed_password = get_password_hash(user_create_dict.pop("password"))
    db_obj = User(**user_create_dict, hashed_password=hashed_password)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


# async def update_user(*, session: AsyncSession, db_user: User, user_in: UserUpdate) -> Any:
#     user_data = user_in.model_dump(exclude_unset=True)
#     extra_data = {}
#     if "password" in user_data:
#         password = user_data["password"]
#         hashed_password = get_password_hash(password)
#         extra_data["hashed_password"] = hashed_password
#     db_user.sqlmodel_update(user_data, update=extra_data)
#     session.add(db_user)
#     await session.commit()
#     await session.refresh(db_user)
#     return db_user


async def get_user_by_username(*, session: AsyncSession, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    result = await session.execute(statement)
    session_user = result.scalar_one_or_none()
    return session_user


async def authenticate(*, session: AsyncSession, username: str, password: str) -> User | None:
    db_user = await get_user_by_username(session=session, username=username)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


async def get_current_user(session: AsyncSession, token: str) -> User | None:
    sub = await validate_token(token)
    if not sub:
        return None
    return await session.get(User, int(sub))
