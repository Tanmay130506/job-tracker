from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.models import User, Application, ApplicationHistory
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request


def create_application(data: ApplicationCreate, db, user):
    if not data.company_name.strip():
        raise HTTPException(400, "Company name cannot be empty")
    if not data.role.strip():
        raise HTTPException(400, "Enter role you applied for")
    if not data.status.strip():
        data.status="applied"
    if data.applied_through_email is None:
        data.applied_through_email=False

    application=Application(
        user_id=user.user_id,
        company_name=data.company_name,
        role=data.role,
        status=data.status,
        date=data.date,
        applied_through_email=data.applied_through_email,
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


def get_applications(user, db):
    applications=db.query(Application).filter(Application.user_id==user.user_id).all()
    return applications


def update_application(data:ApplicationUpdate, application_id: int, db, user):

    if not data.status.strip():
        raise HTTPException(400, "Status field can not be empty")
    application=db.query(Application).filter(Application.application_id==application_id).first()
    if not application:
        raise HTTPException(404, "Application does not exist")
    if user.user_id != application.user_id:
        raise HTTPException(401, "Unauthorized access")
    
    old_status=application.status
    new_status=data.status

    application.status=new_status

    history=ApplicationHistory(
        application_id=application_id,
        old_status=old_status,
        new_status=new_status,
        date=datetime.now(timezone.utc),
        changed_through_email=False,
        email=None
    )

    db.add(history)
    db.commit()
    db.refresh(application)

    return application


def delete_application(application_id:int, db, user):
    application=db.query(Application).filter(Application.application_id==application_id).first()

    if not application:
        raise HTTPException(404, "Application does not exist")
    if user.user_id != application.user_id:
        raise HTTPException(401, "Unauthorized access")

    db.delete(application)
    db.commit()