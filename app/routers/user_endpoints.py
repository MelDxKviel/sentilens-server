from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

from app.database import get_session
from app.auth import AuthHandler, LoginToken, AccessToken
from app.models import User, UserRead, UserLogin, UserRegister


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
    result = session.exec(
        select(User)
    ).all()
    if any(u.email == user.email for u in result):
        raise HTTPException(status_code=400, detail="Email already registered")
    if any(u.username == user.username for u in result):
        raise HTTPException(
            status_code=400, detail="Username already registered")
    user.password = auth_handler.get_password_hash(user.password)
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserRead.model_validate(db_user)


@user_router.post("/login", response_model=LoginToken)
async def login_user(user: UserLogin, session: Session = Depends(get_session)) -> LoginToken:
    db_user = session.exec(
        select(User).where(User.username == user.username)
    ).first()
    if not db_user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")
    if not auth_handler.verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")
    login_token = auth_handler.encode_login_token(db_user.id)
    return login_token


@user_router.post("/update_token", response_model=AccessToken)
async def update_token(user_id=Depends(auth_handler.auth_refresh_wrapper)) -> AccessToken:
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    access_token = auth_handler.encode_login_token(user_id)
    return access_token


@user_router.post("/delete")
async def delete_user(session: Session = Depends(get_session), user_id=Depends(auth_handler.auth_access_wrapper)) -> dict:
    db_user = session.exec(
        select(User).where(User.id == user_id)
    ).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Non-existent user")
    session.delete(db_user)
    session.commit()

    return {"response": "User has been deleted"}
