from app.auth import user_register, user_login, get_current_user
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.crud import create_application, update_application, get_applications, delete_application


app=FastAPI()


@app.post("/register")
def register(data: UserCreate, db=Depends(get_db)):
    return user_register(data, db)


@app.post("/login")
def login(data: UserLogin, db= Depends(get_db)):
    return user_login(data, db)


@app.post("/applications")
def create(data: ApplicationCreate, db= Depends(get_db), user=Depends(get_current_user)):
    return create_application(data, db, user)


@app.get("/applications")
def get(user= Depends(get_current_user), db= Depends(get_db)):
    return get_applications(user, db)


@app.put("/applications/{application_id}")
def update(data:ApplicationUpdate, application_id: int, db= Depends(get_db), user= Depends(get_current_user)):
    return update_application(data, application_id, db, user)


@app.delete("/applications/{application_id}")
def delete(application_id:int, db= Depends(get_db), user= Depends(get_current_user)):
    delete_application(application_id, db, user)
    return {"message": "application deleted successfully"}
