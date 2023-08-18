from datetime import datetime, timedelta
import os
from typing import Annotated, Union
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
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
    request_id: str | None

    # async def stake_balance(self):
    #     return await staked_balance_for(self.address)
    #
    # async def charge(self, amount):
    #     return await charge_stake(self.address, amount)


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


async def get_current_user(request: Request, Authorization: str = Header(...)):
    request_id = request.headers['x-request-id']
    token = Authorization.split("Bearer ")[1]
    print(f"token: {token}")
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
            exp_datetime = datetime.utcfromtimestamp(exp)
            print(f"exp_datetime: {exp_datetime}")
            if datetime.utcnow() > exp_datetime:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Could not validate credentials, access token expired at {exp_datetime}",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        address = payload.get("sub")

        if address is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    return User(address=address, request_id=request_id)


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
        error = "Invalid message"
    except siwe.ExpiredMessage as e:
        print("Authentication attempt rejected. ExpiredMessage")
        error = "Signature expired"
    except siwe.DomainMismatch as e:
        print("Authentication attempt rejected. DomainMismatch")
        error = "Domain mismatch"
    except siwe.NonceMismatch as e:
        print("Authentication attempt rejected. NonceMismatch")
        error = "Nonce mismatch"
    except siwe.MalformedSession as e:
        # e.missing_fields contains the missing information needed for validation
        print("Authentication attempt rejected. MalformedSession")
        error = "Malformed session"
    except siwe.InvalidSignature as e:
        print("Authentication attempt rejected. InvalidSignature")
        error = "Invalid signature"

    print("Authentication attempt accepted.")
    return (is_valid, message, error)


@router.post("/token", response_model=Token)
async def login_for_access_token(request: Request, body_json: SiginETH):
    print(f'{request.client.host}:{request.client.port}')
    # user = authent    icate_user(fake_users_db, form_data.username, form_data.password)
    print(body_json)
    is_valid, message, error_signature = verify_signature(body_json)
    print(f"is_valid: {is_valid}")
    print(f"message: {message}")
    print(f"error_signature: {error_signature}")
    if not is_valid and error_signature is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect signature, error detail: {error_signature}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": message.address}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/dev_token", response_model=Token)
async def login_for_access_token(request: Request ):
    print(f'{request.client.host}:{request.client.port}')
    # user = authent    icate_user(fake_users_db, form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES * 2 * 24 * 7)
    access_token = create_access_token(
        data={"sub": "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
