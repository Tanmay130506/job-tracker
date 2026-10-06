from app.database import SessionLocal
from app.gmail import fetch_emails, get_email_content, parse_email, get_gmail_service
from app.models import User, Application, ApplicationHistory
from app.celery_app import celery_app

@celery_app.task
def task(user_id):
    from app.gmail import fetch_emails, get_email_content, parse_email, get_gmail_service_from_db
    db=SessionLocal()

    try:

        service = get_gmail_service_from_db(user_id, db)
        messages = fetch_emails(service)  # pass service as parameter

        for message in messages:
            message_id= message["id"]
            subject, body, sender, date= get_email_content(service, message_id)
            status, company_name= parse_email(subject, body, sender)

            if status is None:
                continue

            application= db.query(Application).filter(Application.company_name==company_name,
                                                    Application.user_id==user_id).first()

            if application:
                old_status= application.status
                application.status= status

                history= ApplicationHistory(
                    application_id= application.application_id,
                    old_status= old_status,
                    new_status= status,
                    date=date,
                    changed_through_email= True,
                    email= sender
                )
                db.add(history)

            else:
                application= Application(
                    user_id= user_id,
                    company_name= company_name,
                    role= "Unknown",
                    status= status,
                    date= date,
                    applied_through_email= True
                )
                db.add(application)

        db.commit()
    finally:
        db.close()
