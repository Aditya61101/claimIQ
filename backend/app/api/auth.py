import os
from fastapi import APIRouter, Depends, HTTPException, status, Response

from sqlalchemy.orm import Session
# core utilities
from app.core.database import get_db
from app.core.security_utils import verify_password
from app.core.jwt import create_access_token
from app.core.security import require_roles
# models
from app.models.users import User
# schemas
from app.schemas.auth import LoginRequest, CurrentUser
from app.schemas.api_response import APIResponse

INSTANCE = os.getenv("INSTANCE")

router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post("/login", response_model = APIResponse[None])
def login(
    payload:LoginRequest,
    response:Response,
    db:Session = Depends(get_db)
):
    user = (db.query(User).filter(User.email==payload.email, User.is_active==True).first())

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')
    
    access_token = create_access_token(subject=user.id)

    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=True if INSTANCE=='DEV' else False,
        samesite='lax',
        max_age=60*60
    )

    return APIResponse(
        status=True,
        message='Login successful',
        data=None
    )

@router.post("/logout", response_model = APIResponse[None])
def logout(response:Response):
    response.delete_cookie(
        key='access_token',
        httponly=True,
        secure=True if INSTANCE=='DEV' else False,
        samesite='lax',
        max_age=60*60
    )
    return APIResponse(
        status=True,
        message='Logout successful',
        data=None
    )

@router.get("/me", response_model = APIResponse[CurrentUser])
def get_current_user_FE(
    current_user:User = Depends(require_roles("POLICY_HOLDER", "HOSPITAL", "INSURER"))
):
    return APIResponse(
        status=True,
        message='User fetched successfully',
        data=current_user
    )