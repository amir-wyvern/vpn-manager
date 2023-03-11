from db.database import Base
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    ForeignKey,
    VARCHAR,
    Float,
    DateTime,
    Enum
    )
from schemas import (
    DepositHistoryStatus,
    TransferHistoryStatus
)

class DbAdmin(Base):

    __tablename__ = 'admin'

    admin_id = Column(Integer, index=True, primary_key=True, autoincrement= True)
    username = Column(VARCHAR(100), index=True, unique=True, nullable=False)
    password = Column(VARCHAR(200), index=True, nullable=False) # CheckConstraint('balance >= 0')


class DbUser(Base):

    __tablename__ = 'user'

    user_id = Column(Integer, index=True, primary_key=True)
    balance = Column(Float(15,6), nullable=False, default=0.0 ) # CheckConstraint('balance >= 0')


class DbMainAccounts(Base):
    __tablename__ = 'main_accounts'

    index = Column(Integer, primary_key=True, autoincrement=True)
    deposit_address = Column(VARCHAR(42), nullable=False)
    withdraw_address = Column(VARCHAR(42), nullable=False)
    p_withdraw = Column(VARCHAR(2000), nullable=False)


class DbConfig(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    index = Column(Integer, default=1, unique=True)
    withdraw_lock = Column(Boolean, nullable=False, default=False) 
    deposit_lock = Column(Boolean, nullable=False, default=False)
    transfer_lock = Column(Boolean, nullable=False, default=False)
    transfer_fee_percentage = Column(Float(9,6), nullable=False, default=0.001) # CheckConstraint('transfer_fee_percentage >= 0')
    withdraw_fee_percentage = Column(Float(9,6), nullable=False, default=1.0) # CheckConstraint('withdraw_fee_percentage >= 0')
    min_user_balance = Column(Float(15,6), nullable=False, default=0.0) # CheckConstraint(min_user_balance >= 0)
    referal_bonus_percentage = Column(Float(9,6), nullable=False, default=0.1) # CheckConstraint(referal_bonus_percentage >= 0)


class DbTransferHistory(Base):
    __tablename__ = 'transfer_history'

    request_id = Column(VARCHAR(100), primary_key=True, unique=True, index=True)
    from_user = Column(Integer, ForeignKey('user.user_id'), index=True, nullable=False)
    to_user = Column(Integer, ForeignKey('user.user_id'), index=True, nullable=False)
    error_message = Column(VARCHAR(2000), nullable=True)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    status = Column(Enum(TransferHistoryStatus), index=True, nullable=False) # CheckConstraint('value > 0')
    transfer_fee_percentage = Column(Float(9,6), nullable=False) # CheckConstraint('transfer_fee_percentage > 0')
    transfer_fee_value = Column(Float(15,6), nullable=True) # CheckConstraint('withdraw_fee_value > 0')
    request_time = Column(DateTime, index=True, nullable=False)
    processingـcompletionـtime = Column(DateTime, index=True, nullable=True)


class DbDepositHistory(Base):
    __tablename__ = 'deposit_history'

    request_id = Column(VARCHAR(100), primary_key=True, unique=True, index=True)
    tx_hash = Column(VARCHAR(100), unique=True, index=True, nullable=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), index=True, nullable=False)
    from_address = Column(VARCHAR(42), index=True, nullable=True)
    to_address = Column(VARCHAR(42), index=True, nullable=False)
    error_message = Column(VARCHAR(2000), nullable=True)
    status = Column(Enum(DepositHistoryStatus), index=True, nullable=False)
    value = Column(Float(15,6), index=True, nullable=False) # CheckConstraint('value > 0')
    request_time = Column(DateTime, index=True, nullable=False)
    processingـcompletionـtime = Column(DateTime, index=True, nullable=True)
