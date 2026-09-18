from app.auth import user_register, user_login, get_current_user
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.crud import create_application, update_application, get_applications, delete_application
from app.tasks import task
from app.analytics import get_status_counts, get_applications_per_week, get_response_rate, company_count, average_days_to_response
from fastapi.middleware.cors import CORSMiddleware
from typing import List


app=FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
def register(data: UserCreate, db=Depends(get_db)):
    return user_register(data, db)


@app.post("/login")
def login(data: UserLogin, db= Depends(get_db)):
    return user_login(data, db)


@app.post("/applications")
def create(data: ApplicationCreate, db= Depends(get_db), user=Depends(get_current_user)):
    return create_application(data, db, user)


@app.get("/applications", response_model=List[ApplicationResponse])
def get(user= Depends(get_current_user), db= Depends(get_db)):
    return get_applications(user, db)


@app.put("/applications/{application_id}")
def update(data:ApplicationUpdate, application_id: int, db= Depends(get_db), user= Depends(get_current_user)):
    return update_application(data, application_id, db, user)


@app.delete("/applications/{application_id}")
def delete(application_id:int, db= Depends(get_db), user= Depends(get_current_user)):
    delete_application(application_id, db, user)
    return {"message": "application deleted successfully"}


@app.post("/scan-emails")
def scan_emails(user= Depends(get_current_user)):
    task.delay(user.user_id)
    return {"message": "email scan started"}


@app.get("/analytics/status-counts")
def status_counts(user= Depends(get_current_user), db= Depends(get_db)):
    return get_status_counts(user.user_id, db)


@app.get("/analytics/applications-per-week")
def applications_per_week(user= Depends(get_current_user), db= Depends(get_db)):
    return get_applications_per_week(user.user_id, db)


@app.get("/analytics/response-rate")
def response_rate(user= Depends(get_current_user), db= Depends(get_db)):
    return get_response_rate(user.user_id, db)


@app.get("/analytics/company-breakdown")
def company_breakdown(user= Depends(get_current_user), db= Depends(get_db)):
    return company_count(user.user_id, db)


@app.get("/analytics/average-response-days")
def average_response_days(user= Depends(get_current_user), db= Depends(get_db)):
    return average_days_to_response(user.user_id, db)