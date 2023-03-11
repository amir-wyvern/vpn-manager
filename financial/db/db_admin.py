from sqlalchemy.orm.session import Session
from schemas import (
    AdminRegisterForDataBase,
)
from db.models import DbAdmin


def create_admin(request: AdminRegisterForDataBase, db: Session):

    user = DbAdmin(
        username= request.username,
        password= request.password
    )
    db.add(user)

    db.commit()
    db.refresh(user)
    return user

def get_all_admins(db:Session):
    return db.query(DbAdmin).all()

def get_admin(admin_id, db:Session):
    return db.query(DbAdmin).filter(DbAdmin.admin_id == admin_id ).first()

def get_admin_by_username(username, db:Session):
    return db.query(DbAdmin).filter(DbAdmin.username == username ).first()

def delete_admin(admin_id, db:Session):
    user = get_admin(admin_id, db)
    db.delete(user)
    db.commit()
    return True

