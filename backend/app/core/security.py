import os
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.core.database import get_db
# models
from app.models.users import User
from app.models.claims import Claim
# utils
from app.utils.constants import UserRoles
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM='HS256'

def get_current_user(request:Request, db:Session=Depends(get_db)) -> User:
    """
    Extracts user from HTTPonly JWT cookie.
    Raises 401 if authentication fails.
    """

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id:int|None = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    
    user = db.query(User).filter(User.id==user_id, User.is_active==True).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found or inactive')
    
    return user

def require_roles(*allowed_roles):
    def role_checker(user:User=Depends(get_current_user)):
        if not user or user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permission')
        return user
    return role_checker

def assert_claim_access(claim:Claim, user:User):
    """
    Enforces ownership and role based access for claims.
    """

    if user.role == UserRoles.INSURER:
        return
    
    if claim.created_by_id != user.id:
        raise HTTPException(
            status=status.HTTP_403_FORBIDDEN, detail="You don't have access to this claim."
        )
