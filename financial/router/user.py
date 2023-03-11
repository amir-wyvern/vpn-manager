from sqlalchemy.orm.session import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from schemas import (
    UserDisplay,
    HTTPError,
)
from db import db_user
from db.database import get_db
from auth.oauth2 import ( 
    get_current_admin
)

router = APIRouter(prefix='/user', tags=['User'])


@router.get('/info', response_model=UserDisplay, responses={404:{'model':HTTPError}})
def user_info(user_id: int, admin_id: int=Depends(get_current_admin), db: Session=Depends(get_db)):
    
    return db_user.get_user(user_id, db)
