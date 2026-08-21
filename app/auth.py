from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.models import User, Application, ApplicationHistory
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel


SECRET_KEY="9d78011ee8f8a158ccf09bd268d017b08eb16d65aaf20db36fe045eca612a6e9"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def add_user(db, username, email, password):
    hashed_pw=hash_password(password)
    user=User(
         username=username,
         hashed_password=hashed_pw,
         email=email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def user_register(data: UserCreate, db):
    if not data.username.strip():
        raise HTTPException(400, "Username cannot be empty")
    if not data.password.strip():
            raise HTTPException(400, "Password cannot be empty")
    if not data.email.strip():
            raise HTTPException(400, "Email cannot be empty")

    existing_user=db.query(User).filter(User.username==data.username).first()
    existing_email=db.query(User).filter(User.email==data.email).first()

    if existing_user:
        raise HTTPException(400, "Username already exists")
    if existing_email:
        raise HTTPException(400, "Email already exists")

    user=add_user(db, data.username, data.email, data.password)

    return user


def create_access_token(data: dict):
    to_encode= data.copy()
    expire_time=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire_time})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def user_login(data: UserLogin, db):
    if not data.email.strip():
          raise HTTPException(400, "Email cannot be empty")
    if not data.password.strip():
        raise HTTPException(400, "Password cannot be empty")

    user=db.query(User).filter(User.email==data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
         raise HTTPException(401, "Invalid Credentials!")

    token= create_access_token({
         "sub": user.username,
         "id": user.user_id,
         "email": user.email,
    })

    return token


security=HTTPBearer()


def decode_token(token:str):
    try:
         payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
         return payload
    except JWTError as e:
         raise HTTPException(401, "Invalid or Expired token")


def get_current_user(db= Depends(get_db), credentials: HTTPAuthorizationCredentials= Depends(security)):
    token= None
    if credentials:
         token= credentials.credentials
    if token is None:
         raise HTTPException(401, "Not Authenticated")
    new_token= decode_token(token)

    user=db.query(User).filter(User.user_id==new_token["id"]).first()

    if not user:
         raise HTTPException(401, "Not Authenticated")

    return user