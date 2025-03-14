from fastapi import APIRouter, Depends, status

from api.v1.auth.helpers import (
    create_access_token,
    create_auth_user,
    create_refresh_token,
    get_current_user_by_access_token,
    get_current_user_by_refresh_token,
    validate_auth_user,
)
from api.v1.auth.schemas import BaseUser, Token
from core.database import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login(user: User = Depends(validate_auth_user)):
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
async def sign_up(user: User = Depends(create_auth_user)):
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=BaseUser)
async def get_user_info(user: User = Depends(get_current_user_by_access_token)):
    return BaseUser.model_validate(user, from_attributes=True)


@router.post("/refresh", response_model=Token)
async def refresh(user: User = Depends(get_current_user_by_refresh_token)):
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)
    return Token(access_token=access_token, refresh_token=refresh_token)
