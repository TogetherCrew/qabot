from datetime import datetime, timedelta
import os
from typing import Annotated, Union
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

import siwe
from siwe import SiweMessage

load_dotenv()

router = APIRouter()
# to get a string like this run:
# openssl rand -hex 32
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
assert (
    JWT_SECRET_KEY
), "JWT_SECRET_KEY environment variable is missing from .env - look at .env.example"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class SiginETH(BaseModel):
    signature: str
    message_eip4361_str: str


class User(BaseModel):
    address: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(Authorization: str = Header(...)):
    token = Authorization.split("Bearer ")[1]
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        print(f"payload: {payload}")
        print(f"datetime.utcnow(): {datetime.utcnow()}")
        # check expiration date
        exp = payload.get("exp")
        if exp is not None:
            if datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Could not validate credentials, access token expired at {datetime.fromtimestamp(exp)}",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        address = payload.get("sub")

        if address is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    return User(address=address)


def verify_signature(signatureObj: SiginETH):
    is_valid = False
    error = None
    message = None
    try:
        message: SiweMessage = SiweMessage(message=signatureObj.message_eip4361_str)
        message.verify(signatureObj.signature)
        is_valid = True
    except ValueError as e:
        # Invalid message
        print("Authentication attempt rejected. ValueError")
        error = e
    except siwe.ExpiredMessage as e:
        print("Authentication attempt rejected. ExpiredMessage")
        error = e
    except siwe.DomainMismatch as e:
        print("Authentication attempt rejected. DomainMismatch")
        error = e
    except siwe.NonceMismatch as e:
        print("Authentication attempt rejected. NonceMismatch")
        error = e
    except siwe.MalformedSession as e:
        # e.missing_fields contains the missing information needed for validation
        print("Authentication attempt rejected. MalformedSession")
        error = e
    except siwe.InvalidSignature as e:
        print("Authentication attempt rejected. InvalidSignature")
        error = e

    print("Authentication attempt accepted.")
    return (is_valid, message, error)


@router.post("/token", response_model=Token)
async def login_for_access_token(body_json: SiginETH):
    # user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    print(body_json)
    is_valid, message, error_signature = verify_signature(body_json)
    if not is_valid and message is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect signature {error_signature}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": message.address}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
