from typing import Any
from fastapi import FastAPI, Depends, Request, Body, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from . import models, schemas, crud, auth
from .models import UserType
from .schemas import Login
from .keycloak import keycloak_openid
from .database import SessionLocal, engine
from .auth import create_access_token, get_current_user, oauth2_scheme
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    user = crud.get_user_by_email(db, email=admin_email)
    if not user:
        admin_user = schemas.UserCreate(email=admin_email, password=admin_password, user_type=UserType.ADMIN)
        crud.create_user(db=db, user=admin_user)

@app.post("/token", response_model=schemas.TokenResponse)
def login_for_access_token(form_data: schemas.Login = Body(), db: Session = Depends(get_db)):
    print(form_data.username, form_data.password)
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    return user

@app.get("/users/", response_model=list[schemas.User])
def get_users(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(db, token)
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users = db.query(models.User).all()
    return users

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(db, token)
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(db, token)
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db, user)
    return user

@app.put("/users/{user_id}/type", response_model=schemas.User)
def update_user_type(user_id: int, new_type: models.UserType, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(db, token)
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user_type(db, user, new_type)

@app.put("/users/{user_id}/password", response_model=schemas.User)
def change_user_password(user_id: int, password_data: schemas.PasswordChange, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(db, token)
    if current_user.user_type != models.UserType.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        updated_user = crud.change_user_password(db, user, password_data.old_password, password_data.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated_user

@app.post("/tokens/", response_model=schemas.Token)
def create_token(token_data: schemas.TokenCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(db, token)
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_token = crud.create_token(db, current_user, token_data)
    return db_token

@app.get("/tokens/", response_model=list[schemas.Token])
def list_tokens(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(db, token)
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    tokens = db.query(models.Token).all()
    return tokens

@app.delete("/tokens/{token_id}", response_model=schemas.Token)
def delete_token(token_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(db, token)
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_token = crud.get_token_by_id(db, token_id)
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")
    crud.delete_token(db, db_token)
    return db_token


@app.route("/login")
def login():
    auth_url = keycloak_openid.auth_url(redirect_uri="http://localhost:8000/auth/callback")
    return RedirectResponse(auth_url)

@app.route("/auth/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    token = keycloak_openid.token(code=code, redirect_uri="http://localhost:8000/auth/callback")
    return token