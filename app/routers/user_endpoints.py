import random
import string

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.auth import AuthHandler, LoginToken
from app.models import UserRead, UserLogin, UserRegister, UserUpdate, PasswordChange, PasswordResetEmail, PasswordResetConfirm
from app import crud
from app.config import redis_client
from app.utils.email_notifications import send_registration_notification, send_password_reset_notification


user_router = APIRouter(
    prefix="/user",
    tags=["Users"],
    responses={404: {"description": "Not found"},
               },
)
auth_handler = AuthHandler()


def generate_reset_code(length: int = 6):
    return ''.join(random.choices(string.digits, k=length))


@user_router.post("/register", response_model=UserRead, status_code=201, responses={
    400: {"description": "Email or username already registered"},
    201: {"description": "User created successfully"}})
async def register_user(user: UserRegister, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)) -> UserRead:
    user = await crud.register_user(
        user=user,
        session=session
    )
    background_tasks.add_task(send_registration_notification, user.email)
    return user


@user_router.post("/login", response_model=LoginToken)
async def login_user(user: UserLogin, session: AsyncSession = Depends(get_session)) -> LoginToken:
    login_token = await crud.get_login_token(
        user=user,
        session=session
    )
    return login_token


@user_router.post("/update_token", response_model=LoginToken)
async def update_token(user_id=Depends(auth_handler.auth_refresh_wrapper)) -> LoginToken:
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    access_token = auth_handler.encode_login_token(user_id)
    return access_token


@user_router.post("/delete")
async def delete_user(session: AsyncSession = Depends(get_session), user_id=Depends(auth_handler.auth_access_wrapper)) -> dict:
    await crud.delete_user(
        user_id=user_id,
        session=session
    )
    return JSONResponse(status_code=204, content={"detail": "User has been deleted"})


@user_router.get("/profile", response_model=UserRead)
async def get_user(user_id=Depends(auth_handler.auth_access_wrapper), session: AsyncSession = Depends(get_session)) -> UserRead:
    return await crud.get_user(
        user_id=user_id,
        session=session
    )


@user_router.put("/profile", response_model=UserRead)
async def update_user(user: UserUpdate, session: AsyncSession = Depends(get_session), user_id=Depends(auth_handler.auth_access_wrapper)) -> UserRead:
    return await crud.update_user(
        user=user,
        session=session,
        user_id=user_id
    )


@user_router.post("/change-password")
async def change_password(passwords: PasswordChange, session: AsyncSession = Depends(get_session), user_id=Depends(auth_handler.auth_access_wrapper)) -> dict:
    await crud.change_password(passwords=passwords, session=session, user_id=user_id)
    return JSONResponse(status_code=200, content={"detail": "Password has been changed"})


@user_router.post("/reset-password-request")
async def reset_password_request(password_reset: PasswordResetEmail, background_tasks: BackgroundTasks):
    reset_code = generate_reset_code()
    redis_client.setex(reset_code, 600, password_reset.email)
    background_tasks.add_task(
        send_password_reset_notification, password_reset.email, reset_code)
    return JSONResponse(status_code=200, content={"detail": "Reset code has been sent"})


@user_router.post("/reset-password-confirm")
async def reset_password_confirm(password_reset: PasswordResetConfirm, session: AsyncSession = Depends(get_session)):
    email = redis_client.getdel(password_reset.reset_code)

    if email is None:
        raise HTTPException(status_code=404, detail="Reset code not found")

    await crud.reset_password(
        email=email.decode("utf-8"),
        password=password_reset.new_password,
        session=session
    )
    return JSONResponse(status_code=200, content={"detail": "Password has been changed"})
