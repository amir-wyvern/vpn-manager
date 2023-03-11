from sqlalchemy.orm.session import Session
from sqlalchemy import or_
from schemas import (
    UserRegisterForDataBase,
)
from db.models import DbUser


def create_user(request: UserRegisterForDataBase, db: Session):

    user = DbUser(
        user_id= request.user_id,
        balance= 0
    )
    db.add(user)

    db.commit()
    db.refresh(user)
    return user


def get_all_users(db:Session):
    return db.query(DbUser).all()


def get_user(user_id, db:Session):
    return db.query(DbUser).filter(DbUser.user_id == user_id ).first()

def delete_user(user_id, db:Session):
    user = get_user(user_id, db)
    db.delete(user)
    db.commit()
    return True

def update_balance(user_id, new_balance, db:Session):

    user = db.query(DbUser).filter(DbUser.user_id == user_id)
    user.update({
        DbUser.balance: round(new_balance, 6),
    })
    db.commit()

    return True

def increase_balance(user_id, amount, db:Session, commit=True):

    user = db.query(DbUser).filter(DbUser.user_id == user_id)
    user.update({
        DbUser.balance: round(float(user.first().balance) + amount, 6),
    })
    if commit:
        db.commit()
        return True

def decrease_balance(user_id, amount, db:Session, commit=True):

    user = db.query(DbUser).filter(DbUser.user_id == user_id)
    user.update({
        DbUser.balance: round(float(user.first().balance) - amount, 6),
    })

    if commit:
        db.commit()
        return True