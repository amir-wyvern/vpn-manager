from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from schemas import (
    HTTPError,
    AdminAuthResponse
)
from db import db_admin
from db.database import get_db 
from auth.oauth2 import ( 
    create_access_token
)

from db.hash import Hash

router = APIRouter(prefix='/auth')


@router.post('/login', response_model=AdminAuthResponse, responses={401:{'model':HTTPError}}, tags=["Admin-Login"])
def admin_login(request: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)):

    username = request.username
    data = db_admin.get_admin_by_username(username, db)
    if data is None :
        raise HTTPException(status_code=401, detail={'internal_code':1009, 'message':'The username or password is incorrect'})

    if Hash.verify(data.password, request.password) == False:
        raise HTTPException(status_code=401, detail={'internal_code':1009, 'message':'The username or password is incorrect'})

    access_token = create_access_token(data={'admin_id': data.admin_id})

    resp = {
        'access_token': access_token,
        'type_token': 'bearer',
    }

    return AdminAuthResponse(**resp)

