from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class SuperUserCreate(UserCreate):
    is_superuser: bool = True


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_superuser: bool
