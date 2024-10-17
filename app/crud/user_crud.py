from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, UserRead, UserRegister, UserUpdate, PasswordChange
from app.auth import AuthHandler


auth_handler = AuthHandler()


async def register_user(user: UserRegister, session: AsyncSession):
    result = await session.exec(
        select(User)
    )

    users = result.all()

    if any(u.email == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")

    if any(u.username == user.username for u in users):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    user.password = auth_handler.get_password_hash(user.password)

    db_user = User.model_validate(user)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return UserRead.model_validate(db_user)


async def get_login_token(user: UserRegister, session: AsyncSession):
    result = await session.exec(
        select(User).where(User.username == user.username)
    )

    db_user = result.first()

    if not db_user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")

    if not auth_handler.verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")

    login_token = auth_handler.encode_login_token(db_user.id)

    return login_token


async def delete_user(user_id: int, session: AsyncSession):
    result = await session.exec(
        select(User).where(User.id == user_id)
    )

    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Non-existent user")

    await session.delete(db_user)
    await session.commit()


async def get_user(user_id: int, session: AsyncSession):
    result = await session.exec(
        select(User).where(User.id == user_id)
    )

    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Non-existent user")

    return UserRead.model_validate(db_user)


async def update_user(user: UserUpdate, session: AsyncSession, user_id: int):
    result = await session.exec(
        select(User).where(User.id == user_id)
    )

    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Non-existent user")

    if user.username:
        db_user.username = user.username
    if user.email:
        db_user.email = user.email

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return UserRead.model_validate(db_user)


async def change_password(
    passwords: PasswordChange,
    session: AsyncSession,
    user_id: int
) -> None:
    result = await session.exec(
        select(User).where(User.id == user_id)
    )

    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Non-existent user")

    if not auth_handler.verify_password(
        passwords.old_password,
        db_user.password
    ):
        raise HTTPException(status_code=401, detail="Incorrect password")

    db_user.password = auth_handler.get_password_hash(passwords.new_password)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)


async def reset_password(email: str, password: str, session: AsyncSession):
    result = await session.exec(
        select(User).where(User.email == email)
    )

    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Non-existent user")

    db_user.password = auth_handler.get_password_hash(password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
