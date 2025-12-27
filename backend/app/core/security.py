import os
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.core.database import get_db
from app.models.users import User
from dotenv import load_dotenv
load_dotenv()

oauth2scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM='HS256'

def get_current_user(request:Request, db:Session=Depends(get_db)) -> User:
    try:
        token = request.cookies.get("access_token")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id:int = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail='Invalid token')
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    
    user = db.query(User).filter(User.id==user_id, User.is_active==True).first()

    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    
    return user