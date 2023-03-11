from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from schemas import (
    HTTPError,
    BaseResponse,
    DepositRequest,
    DepositConfirmation,
    DepositRequestResponse,
    DepositHistoryResponse,
    DepositHistoryModelForDataBase,
    DepositHistoryStatus
)

from db import db_deposit, db_main_account, db_config
from db.database import get_db

from celery_tasks.tasks import DepositCeleryTask 
from celery_tasks.utils import create_worker_from
from sqlalchemy.orm.session import Session
from auth.oauth2 import ( 
    get_current_admin
)
from uuid import uuid4
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a console handler to show logs on terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler to save logs to a file
file_handler = logging.FileHandler('deposit_route.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

router = APIRouter(prefix='/deposit', tags=['Deposit'])

_, deposit_worker = create_worker_from(DepositCeleryTask)

@router.post('/request', response_model=DepositRequestResponse, responses={403:{'model':HTTPError}})
def deposit_request(request: DepositRequest, admin_id: int=Depends(get_current_admin), db: Session=Depends(get_db)):

    request_id = uuid4().hex[:12]
    config = db_config.get_config(db)

    if config.deposit_lock == True:
        logger.info(f'deposit has locked [request_id: {request_id} -user_id: {request.user_id}]')
        raise HTTPException(status_code=403, detail={'internal_code':1019, 'message':'deposit has locked'})

    resp_valeus = db_deposit.get_deposit_history_by_value(request.value, db, status= DepositHistoryStatus.WAITING)
    if resp_valeus == []:
        logger.info(f'The value already registered [request_id: {request_id} -user_id: {request.user_id} -value: {request.value}]')
        raise HTTPException(status_code=403, detail={'internal_code':1022, 'message':'The value already registered'})

    resp_user_id = db_deposit.get_deposit_history_by_user_id(request.user_id, db, status= DepositHistoryStatus.WAITING)
    if len(resp_user_id) > 5 :
        logger.info(f'The value already registered [request_id: {request_id} -user_id: {request.user_id} -value: {request.value}]')
        raise HTTPException(status_code=403, detail={'internal_code':1023, 'message':'The number of requests exceeds the limit'})


    deposit_address = db_main_account.get_deposit_address(db)

    request_data = {
        'request_id': request_id,
        'tx_hash': None,
        'user_id': request.user_id,
        'from_address': None,
        'to_address': deposit_address,
        'value': request.value,
        'status': DepositHistoryStatus.WAITING,
        'error_message': None,
        'request_time': datetime.now(),
        'processingـcompletionـtime': None
    }

    resp = db_deposit.get(DepositHistoryModelForDataBase(**request_data), db)

    if resp:
        return {'request_id': request_id ,'deposit_address': deposit_address}

    else:
        raise HTTPException(status_code=403, detail={'internal_code':1003, 'message':'There was a problem in registering the deposit request'})


@router.post('/confirmation', response_model=BaseResponse, responses={404:{'model':HTTPError}})
def deposit_comfirmation(request: DepositConfirmation, admin_id: int=Depends(get_current_admin), db: Session=Depends(get_db)):

    payload = {
        'user_id': request.user_id,
        'tx_hash': request.tx_hash
    }
    
    deposit_worker.apply_async(args=(payload, )) 

    return {'message':'the request is proccessing'}


@router.get('/history', response_model=DepositHistoryResponse, responses={404:{'model':HTTPError}})
def deposit_history(user_id: int ,start_time: datetime, end_time: datetime, admin_id: int=Depends(get_current_admin), db: Session=Depends(get_db)):

    history = db_deposit.get_deposit_history_by_time_and_user(user_id, start_time, end_time, db)

    return {'txs': history }

