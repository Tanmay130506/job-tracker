from app.auth import user_register, user_login
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, ApplicationCreate, ApplicationResponse, ApplicationUpdate


app=FastAPI()


@app.post("/register")
def register(data: UserCreate, db=Depends(get_db)):
    return user_register(data, db)


@app.post("/login")
def login(data: UserLogin, db= Depends(get_db)):
    return user_login(data, db)
