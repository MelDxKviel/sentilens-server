from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import select, Session

from app.database import get_session
from app.auth import AuthHandler, LoginToken, AccessToken
from app.models import UserRead, UserLogin, UserRegister
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
    user = crud.register_user(user, session)
    return user


@user_router.post("/login", response_model=LoginToken)
async def login_user(user: UserLogin, session: Session = Depends(get_session)) -> LoginToken:
    login_token = crud.get_login_token(user, session)
    return login_token


@user_router.post("/update_token", response_model=AccessToken)
async def update_token(user_id=Depends(auth_handler.auth_refresh_wrapper)) -> AccessToken:
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    access_token = auth_handler.encode_login_token(user_id)
    return access_token


@user_router.post("/delete")
async def delete_user(session: Session = Depends(get_session), user_id=Depends(auth_handler.auth_access_wrapper)) -> dict:
    crud.delete_user(session, user_id)
    return JSONResponse(status_code=204, content={"detail": "User has been deleted"})
