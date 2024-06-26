from pydantic import BaseModel, EmailStr, Field
from typing import List, Union, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import re


class UpdateConfig(BaseModel):

    withdraw_lock: bool
    deposit_lock: bool
    transfer_lock: bool
    transfer_fee_percentage: float = Field(ge=0)
    withdraw_fee_percentage: float = Field(ge=0)
    min_user_balance: float = Field(ge=0)
    referal_bonus_percentage: float = Field(ge=0)


# Auth
class AuthType(str, Enum):
    phone_number = 'phone_number'
    email = 'email' 
    

class AuthPhoneNumberRequest(BaseModel):

    data: str=Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")

class AuthEmailRequest(BaseModel):

    data: EmailStr


class UserAuthDecode(BaseModel):

    data: str
    token: str

class UserAuthConfirmation(BaseModel):

    auth_code: int = Field(ge=100000, le=999999)

class UserAuthResponse(BaseModel):

    access_token: str
    type_token: str


class AdminAuthResponse(BaseModel):

    access_token: str
    type_token: str




# user Login or Register
class PhoneNumberStr(str):
    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type='string', format='phonenumber', example='+98-9151234567')

    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not re.match(r"^\+\d{1,3}-\d{6,12}$", v):
            raise ValueError("Not a valid phone number")
        return v
    
class UserRegisterForDataBase(BaseModel):

    user_id: int 

class AdminRegisterForDataBase(BaseModel):

    admin_id: int 
    username: str 
    password: str


class UserRegisterByEmail(BaseModel):

    tel_id: Optional[int] = Field(ge=0, default= None)
    email: EmailStr
    phone_number: Optional[PhoneNumberStr] = None
    password: str = Field(min_length=1, max_length=200)
    referal_link: Optional[str] = Field(min_length=1, max_length=50, default=None)
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)

class UserRegisterByPhoneNumber(BaseModel):

    tel_id: Optional[int] = Field(ge=0, default= None)
    phone_number: PhoneNumberStr 
    email: Optional[EmailStr] = None 
    password: str = Field(min_length=1, max_length=200)
    referal_link: Optional[str] = Field(min_length=1, max_length=50, default=None)
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)

class UserRegisterByPhoneNumberForDataBase(BaseModel):

    tel_id: Optional[int] = Field(ge=0, default= None)
    phone_number: int = Field(ge=0, le=999)
    email: Optional[EmailStr] = None 
    password: str = Field(min_length=1, max_length=200)
    referal_link: Optional[str] = Field(min_length=1, max_length=50, default=None)
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)




# User
class UserBase(BaseModel):

    tel_id : int

class UserUpdateProfile(BaseModel):

    phone_number:str = Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")
    email:  Union[EmailStr, None] 
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)


class UserAuth(BaseModel):

    auth_code : int

class UserLogin(BaseModel):

    phone_number: str = Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")
    password: str = Field(min_length=1, max_length=100)

class UserDisplay(BaseModel):

    balance: float

    class Config:
        orm_mode = True

class BaseResponse(BaseModel):

    message: str


class UpdatePassword(BaseModel):

    old_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=1, max_length=200)

class HTTPError(BaseModel):

    message: str 
    internal_code: str

    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException raised.", 'internal_code':1001},
        }
        


# Withdraw modeles
class WithdrawHistoryStatus(int, Enum):
    PROCESSING = 1
    SUCCESS = 2
    FAILED = 3


class WithdrawHistoryModelForDataBase(BaseModel):

    request_id: str
    tx_hash: Union[str, None]
    user_id: int
    from_address: str
    to_address: str
    value: float
    status: WithdrawHistoryStatus
    error_message: Union[str, None]
    withdraw_fee_percentage: float
    withdraw_fee_value: Union[float, None]
    request_time: datetime
    processingـcompletionـtime: Union[datetime, None]

    class Config:
        orm_mode = True


class WithdrawHistoryModelForUpdateDataBase(BaseModel):

    tx_hash: Union[str, None]
    status: Union[WithdrawHistoryStatus, None]
    withdraw_fee_value: Union[float, None]
    error_message: Union[str, None]
    processingـcompletionـtime: Union[datetime, None]

class WithdrawRequest(BaseModel):

    value: float = Field(gt=0)
    to_address: str = Field(min_length=1, max_length=100)

class WithdrawRequestResponse(BaseModel):
    
    message: str
    request_id: str

class WithdrawConfirmation(BaseModel):

    auth_code: int = Field(ge=100000,le=999999)

class WithdrawHistoryRequest(BaseModel):

    offset: int
    count: int

class WithdrawHistoryModel(BaseModel):

    address: str
    value: float
    tx_hash: str
    timestamp: datetime

class WithdrawtHistoryResponse(BaseModel):

    txs: List[WithdrawHistoryModelForDataBase]


# Transfer modeles
class TransferHistoryStatus(int, Enum):
    PROCESSING = 1
    SUCCESS = 2
    FAILED = 3
    
class TransferRequest(BaseModel):

    user_id: int
    value: float = Field(gt=0)
    to_user: int


class TransferHistoryModelForDataBase(BaseModel):

    request_id: str
    from_user: int
    to_user: int
    error_message: Union[str, None]
    value: float = Field(gt=0)
    status: TransferHistoryStatus
    transfer_fee_percentage: float 
    transfer_fee_value: Union[float, None]
    request_time: datetime
    processingـcompletionـtime: Union[datetime, None]

    class Config:
        orm_mode = True

class TransferHistoryModelForUpdateDataBase(BaseModel):

    error_message: Union[str, None]
    status: TransferHistoryStatus
    transfer_fee_value: Union[float, None]
    processingـcompletionـtime: Union[datetime, None]


class TransferRequestResponse(BaseModel):
    
    message: str
    request_id: str

class TransferHistoryResponse(BaseModel):

    txs: List[TransferHistoryModelForDataBase]

class TransferHistoryRequest(BaseModel):

    offset: int
    count: int



# Deposit
class DepositHistoryStatus(int, Enum):
    WAITING = 1
    SUCCESS = 2
    FAILED = 3


class DepositHistoryModelForDataBase(BaseModel):

    request_id: str
    tx_hash: Union[str, None]
    user_id: int
    from_address: Union[str, None] 
    to_address: str
    value: float
    status: DepositHistoryStatus
    error_message: Union[str, None]
    request_time: datetime
    processingـcompletionـtime: Union[datetime, None]

    class Config:
        orm_mode = True


class DepositHistoryModelForUpdateDataBase(BaseModel):

    tx_hash: Union[str, None]
    from_address: Union[str, None] 
    status: Union[DepositHistoryStatus, None]
    error_message: Union[str, None]
    processingـcompletionـtime: Union[datetime, None]

class DepositRequestResponse(BaseModel):

    deposit_address: str
    request_id: str

class DepositRequest(BaseModel):

    user_id: int
    value: float = Field(gt=0)

class DepositConfirmation(BaseModel):

    user_id: int
    tx_hash: str = Field(min_length=1, max_length=100)

class DepositHistoryRequest(BaseModel):

    offset: int
    count: int


class DepositHistoryResponse(BaseModel):

    txs: List[DepositHistoryModelForDataBase]

class ReceivedTx(BaseModel):

    tx_hash: str = Field(min_length=1, max_length=100)
    from_address: str = Field(min_length=1, max_length=100)
    value: float  = Field(gt= 0)
    timestamp: datetime


# Cache
class SessionScheme(BaseModel):
    
    token: str = Field(min_length=1, max_length=300)
    user_id: int = Field(ge=0)

