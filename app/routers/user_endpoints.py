from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import select, Session

from app.database import get_session
from app.auth import AuthHandler, LoginToken, AccessToken
from app.models import UserRead, UserLogin, UserRegister, UserUpdate, PasswordChange
from app import crud


user_router = APIRouter(
    prefix="/user",
    tags=["Users"],
    responses={404: {"description": "Not found"},
               },
)
auth_handler = AuthHandler()


@user_router.post("/register", response_model=UserRead, status_code=201, responses={
    400: {"description": "Email or username already registered"},
    201: {"description": "User created successfully"}})
async def register_user(user: UserRegister, session: Session = Depends(get_session)) -> UserRead:
    user = crud.register_user(
        user=user,
        session=session
    )
    return user


@user_router.post("/login", response_model=LoginToken)
async def login_user(user: UserLogin, session: Session = Depends(get_session)) -> LoginToken:
    login_token = crud.get_login_token(
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
async def delete_user(session: Session = Depends(get_session), user_id=Depends(auth_handler.auth_access_wrapper)) -> dict:
    crud.delete_user(
        user_id=user_id,
        session=session
    )
    return JSONResponse(status_code=204, content={"detail": "User has been deleted"})


@user_router.get("/profile", response_model=UserRead)
async def get_user(user_id=Depends(auth_handler.auth_access_wrapper), session: Session = Depends(get_session)) -> UserRead:
    return crud.get_user(
        user_id=user_id,
        session=session
    )


@user_router.put("/profile", response_model=UserRead)
async def update_user(user: UserUpdate, session: Session = Depends(get_session), user_id=Depends(auth_handler.auth_access_wrapper)) -> UserRead:
    return crud.update_user(
        user=user,
        session=session,
        user_id=user_id
    )


@user_router.post("/change_password")
async def change_password(passwords: PasswordChange, session: Session = Depends(get_session), user_id=Depends(auth_handler.auth_access_wrapper)) -> dict:
    crud.change_password(passwords=passwords, session=session, user_id=user_id)
    return JSONResponse(status_code=204, content={"detail": "Password has been changed"})
