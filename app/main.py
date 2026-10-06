from app.auth import user_register, user_login, get_current_user
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.crud import create_application, update_application, get_applications, delete_application
from app.tasks import task
from app.analytics import get_status_counts, get_applications_per_week, get_response_rate, company_count, average_days_to_response
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from google_auth_oauthlib.flow import Flow
from app.models import GmailToken
from fastapi.responses import RedirectResponse
import json
import os
import tempfile


app=FastAPI()


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

credentials_json = os.environ.get("GOOGLE_CREDENTIALS")
if credentials_json:
    creds_dict = json.loads(credentials_json)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(creds_dict, f)
        CREDENTIALS_FILE = f.name
else:
    CREDENTIALS_FILE = "credentials.json"


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://job-tracker-2.netlify.app"
    ],
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


@app.get("/auth/gmail")
def gmail_auth(token: str, db=Depends(get_db)):
    from app.auth import decode_token
    payload = decode_token(token)
    user_id = payload["id"]
    
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri="https://job-tracker-api-production-0b2e.up.railway.app/auth/gmail/callback"
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=str(user_id)
    )
    return RedirectResponse(auth_url)


@app.get("/auth/gmail/callback")
def gmail_callback(code: str, state: str, db=Depends(get_db)):
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri="https://job-tracker-api-production-0b2e.up.railway.app/auth/gmail/callback",
        state=state
    )
    flow.fetch_token(code=code)
    
    credentials = flow.credentials
    token_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes)
    }
    
    user_id = int(state)
    
    # Check if token already exists for this user
    existing = db.query(GmailToken).filter(GmailToken.user_id == user_id).first()
    if existing:
        existing.token_data = json.dumps(token_data)
    else:
        gmail_token = GmailToken(
            user_id=user_id,
            token_data=json.dumps(token_data)
        )
        db.add(gmail_token)
    
    db.commit()
    
    # Redirect back to frontend after successful connection
    return RedirectResponse("https://job-tracker-2.netlify.app/dashboard.html?gmail=connected")