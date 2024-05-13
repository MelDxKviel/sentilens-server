from fastapi import HTTPException
from sqlmodel import select, Session

from app.models import User, UserRead, UserRegister
from app.auth import AuthHandler, LoginToken, AccessToken


auth_handler = AuthHandler()

def register_user(user: UserRegister, session: Session):
    users = session.exec(
        select(User)
    ).all()
    
    if any(u.email == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if any(u.username == user.username for u in users):
        HTTPException(
            status_code=400, detail="Username already registered")
    
    user.password = auth_handler.get_password_hash(user.password)
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return UserRead.model_validate(db_user)


def get_login_token(user: UserRegister, session: Session):
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

def delete_user(user_id: int, session: Session):
    db_user = session.exec(
        select(User).where(User.id == user_id)
    ).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Non-existent user")
    session.delete(db_user)
    session.commit()
