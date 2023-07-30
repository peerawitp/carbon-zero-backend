from passlib.context import CryptContext
from jose import jwt
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_access_token(data: dict):
    secret = os.getenv("JWT_SECRET")
    to_encode = data.copy()
    return jwt.encode(to_encode, secret, algorithm="HS256")
