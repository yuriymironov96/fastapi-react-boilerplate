from datetime import timedelta
from sqladmin import Admin
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from fastapi import FastAPI
from app.core.config import settings
from app.models import User
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from app.core.db import sessionmanager
from app.crud import authenticate
from app.core import security


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        async with sessionmanager.session() as session:
            authenticated_user = await authenticate(
                session=session, email=form["username"], password=form["password"]
            )
            if not authenticated_user:
                return False
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = security.create_access_token(
                authenticated_user.id, expires_delta=access_token_expires
            )
            request.session.update({"token": access_token})
            return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        async with sessionmanager.session() as session:
            current_user = await security.get_current_user(session, token)
            if not current_user:
                return False
            return True


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.username,
        User.email,
        User.first_name,
        User.last_name,
        User.is_superuser,
    ]


def get_admin(app: FastAPI):
    async_engine = create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        echo=settings.ECHO_SQL,
    )
    # Create an async sessionmaker
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,  # often helpful in async contexts
    )

    admin = Admin(
        app,
        engine=async_engine,
        session_maker=AsyncSessionLocal,
        authentication_backend=AdminAuth(secret_key=settings.SECRET_KEY),
    )

    admin.add_view(UserAdmin)

    return admin
