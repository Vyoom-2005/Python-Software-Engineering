from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .security import decode_token
bearer=HTTPBearer(auto_error=False)
def current_user(c:HTTPAuthorizationCredentials|None=Depends(bearer),db:Session=Depends(get_db)):
    if not c or c.scheme.lower()!='bearer': raise HTTPException(status_code=401,detail='Bearer token required',headers={'WWW-Authenticate':'Bearer'})
    u=db.get(User,decode_token(c.credentials))
    if not u: raise HTTPException(status_code=401,detail='User no longer exists')
    return u
