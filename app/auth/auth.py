from datetime import datetime, UTC, timedelta

from fastapi import Security, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
import jwt
from pydantic import BaseModel

from app.config import global_settings


class LoginToken(BaseModel):
    refresh_token: str
    access_token: str
    expires_at: datetime


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = global_settings.auth_key
    algorithm = "HS256"

    def get_password_hash(self, plain_password: str) -> str:
        return self.pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id: int, token_type: str) -> tuple[str, datetime]:
        payload = dict(
            sub=token_type,
            iss=user_id
        )
        to_encode = payload.copy()
        if token_type == "access_token":
            to_encode.update(
                {"exp": datetime.now(UTC) + timedelta(hours=24)})
        else:
            to_encode.update({"exp": datetime.now(UTC) + timedelta(hours=720)})

        return jwt.encode(to_encode, self.secret, algorithm='HS256'), to_encode["exp"]

    def encode_login_token(self, user_id: int) -> LoginToken:
        access_token, exp = self.encode_token(user_id, "access_token")
        refresh_token, _ = self.encode_token(user_id, "refresh_token")

        login_token = LoginToken(
            refresh_token=refresh_token,
            access_token=access_token,
            expires_at=exp
        )

        return login_token

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret,
                                 algorithms=[self.algorithm])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail="Signature has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def decode_access_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload['sub'] != "access_token":
                raise HTTPException(status_code=401, detail='Invalid token')
            return payload['iss']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail='Invalid token')

    def decode_refresh_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload['sub'] != "refresh_token":
                raise HTTPException(status_code=401, detail='Invalid token')
            return payload['iss']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail='Invalid token')

    def auth_access_wrapper(self,
                            auth: HTTPAuthorizationCredentials = Security(security, scopes=["access_token"])) -> str:
        return self.decode_access_token(auth.credentials)

    def auth_refresh_wrapper(self,
                             auth: HTTPAuthorizationCredentials = Security(security, scopes=["refresh_token"])) -> str:
        return self.decode_refresh_token(auth.credentials)
