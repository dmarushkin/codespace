from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from .auth import create_access_token
from datetime import datetime

ACCESS_TOKEN_EXPIRE_DAYS = 365

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, user_type=user.user_type)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_type(db: Session, user: models.User, new_type: models.UserType):
    user.type = new_type
    db.commit()
    db.refresh(user)
    return user

def change_user_password(db: Session, user: models.User, old_password: str, new_password: str):
    if not pwd_context.verify(old_password, user.hashed_password):
        raise ValueError("Old password is incorrect")
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: models.User):
    db.delete(user)
    db.commit()

def create_token(db: Session, user: models.User, token_data: schemas.TokenCreate):

    expires_at = datetime.now() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    token_str = create_access_token(data={"sub": user.email}, expires_at = expires_at)

    db_token = models.Token(owner_id=user.id, token_name=token_data.token_name, token = token_str, expires_at = expires_at)

    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_token_by_id(db: Session, token_id: int):
    return db.query(models.Token).filter(models.Token.id == token_id).first()

def delete_token(db: Session, token: models.Token):
    db.delete(token)
    db.commit()

