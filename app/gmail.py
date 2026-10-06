import email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import base64
from email.utils import parseaddr
from google.oauth2.credentials import Credentials
import json

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def fetch_emails(service):
    messages= service.users().messages().list(userId= "me", q= "application OR interview OR offer OR rejection OR shortlisted OR applied OR hired OR regret OR selected OR rejected", maxResults=10).execute()
    return messages.get("messages", [])


def get_body(payload):
    if "data" in payload.get("body", {}):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
    for part in payload.get("parts", []):
        result = get_body(part)
        if result:
            return result
    return ""


def get_email_content(service, message_id):

    data= service.users().messages().get(userId= "me", id= message_id, format= "full").execute()

    headers= data["payload"]["headers"]
    body= get_body(data["payload"])
    subject= next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    sender= next((h["value"] for h in headers if h["name"] == "From"), "No Sender")
    date_str= next((h["value"] for h in headers if h["name"] == "Date"), None)

    date= email.utils.parsedate_to_datetime(date_str)

    return  subject, body, sender, date


def parse_email(subject, body, sender):
    status= None
    content= (subject + " " + body).lower()

    applied_keywords = [
    "application received",
    "application has been received",
    "your application has been received",
    "we have received your application",
    "we've received your application",
    "application successfully received",
    "application successfully submitted",
    "your application was successfully submitted",
    "your application has been successfully submitted",
    "application submitted successfully",
    "your application was submitted",
    "application confirmation",
    "application confirmed",
    "application submission confirmed",
    "submission confirmed",
    "application acknowledged",
    "application has been acknowledged",
    "thank you for applying",
    "thanks for applying",
    "thank you for your application",
    "thanks for your application",
    "thank you for submitting your application",
    "thank you for submitting your resume",
    "we received your application",
    "we received your resume",
    "we received your cv",
    "your resume has been received",
    "your cv has been received",
    "application submitted",
    "application received for",
]
    
    interview_keywords = [
    "interview invitation",
    "interview invite",
    "invitation to interview",
    "invite you to interview",
    "invited to interview",
    "you are invited to interview",
    "we'd like to interview you",
    "we would like to interview you",
    "we'd like to invite you to an interview",
    "we would like to invite you to an interview",
    "schedule an interview",
    "schedule your interview",
    "schedule a time for an interview",
    "interview scheduling",
    "interview scheduled",
    "your interview is scheduled",
    "interview has been scheduled",
    "interview confirmation",
    "confirm your interview",
    "confirm interview",
    "interview request",
    "interview availability",
    "interview availability request",
    "next round interview",
    "next-round interview",
    "next round of interviews",
    "next stage interview",
    "next stage of the interview process",
    "move to the next round",
    "moving to the next round",
    "advance to the next round",
    "advancing to the next round",
    "proceed to the next round",
    "proceeding to the next round",
    "first round interview",
    "first-round interview",
    "second round interview",
    "second-round interview",
    "final round interview",
    "final-round interview",
    "phone interview",
    "telephone interview",
    "phone screen",
    "phone screening",
    "phone screen interview",
    "screening interview",
    "initial interview",
    "initial screening",
    "initial phone screen",
    "technical interview",
    "technical screening",
    "technical screen",
    "coding interview",
    "coding assessment",
    "video interview",
    "video call interview",
    "virtual interview",
    "onsite interview",
    "on-site interview",
    "in-person interview",
    "panel interview",
    "behavioral interview",
    "hr interview",
    "recruiter interview",
    "hiring manager interview",
    "interview with the hiring manager",
    "interview process",
    "interview stage",
    "interview round",
    "interview stage",
    "meet the team",
    "meet our team",
    "meeting with the hiring manager",
    "speak with the hiring manager",
    "chat with the hiring manager",
    "conversation with the hiring manager",
    "next steps in the interview process",
    "next steps for your interview",
    "prepare for your interview",
    "interview preparation",
]

    rejected_keywords = [
    "application rejected",
    "your application was rejected",
    "your application has been rejected",
    "application unsuccessful",
    "your application was unsuccessful",
    "your application has been unsuccessful",
    "not selected",
    "you were not selected",
    "you have not been selected",
    "we did not select you",
    "not moving forward",
    "we are not moving forward",
    "we're not moving forward",
    "we will not be moving forward",
    "we won't be moving forward",
    "we have decided not to move forward",
    "we've decided not to move forward",
    "we have decided not to proceed",
    "we've decided not to proceed",
    "unable to move forward",
    "unable to proceed",
    "will not proceed",
    "will not be proceeding",
    "decided not to proceed",
    "decided not to continue",
    "not proceed with your application",
    "not proceed with your candidacy",
    "not continue with your application",
    "not continue with your candidacy",
    "regret to inform you",
    "regret to let you know",
    "sorry to inform you",
    "sorry to let you know",
    "unfortunately",
    "unfortunately,",
    "we regret",
    "regretfully",
    "unable to offer you",
    "unable to offer the position",
    "cannot offer you",
    "cannot offer the position",
    "will not be considered",
    "not be considered",
    "no longer under consideration",
    "not under consideration",
    "removed from consideration",
    "application declined",
    "candidacy declined",
    "candidacy rejected",
    "position has been filled",
    "role has been filled",
    "position was filled",
    "role was filled",
    "rejected",
    "unsuccessful",
    "declined",
    "regret",
    "withdrawn",
    "closed",
]

    offered_keywords = [
    "job offer",
    "job offer letter",
    "offer letter",
    "employment offer",
    "offer of employment",
    "formal offer",
    "formal employment offer",
    "formal job offer",
    "employment agreement",
    "employment contract",
    "job offer confirmation",
    "offer confirmation",
    "offer details",
    "offer package",
    "offer documentation",
    "offer documents",
    "offer acceptance",
    "offer acceptance deadline",
    "offer acceptance required",
    "pleased to offer you",
    "we are pleased to offer you",
    "we're pleased to offer you",
    "we would like to offer you",
    "we'd like to offer you",
    "we are delighted to offer you",
    "we're delighted to offer you",
    "we are happy to offer you",
    "we're happy to offer you",
    "we are excited to offer you",
    "we're excited to offer you",
    "offer you the position",
    "offer you the role",
    "offer you a position",
    "offer you employment",
    "employment offer for",
    "offer for the position",
    "offer for the role",
    "extend an offer",
    "extending an offer",
    "offer has been extended",
    "offer has been approved",
    "appointment letter",
    "letter of appointment",
    "appointment confirmation",
    "joining letter",
    "joining confirmation",
    "employment confirmation",
    "employment confirmed",
    "joining details",
    "joining instructions",
    "joining date",
    "start date",
    "your start date",
    "new hire",
    "new hire paperwork",
    "new hire documents",
    "onboarding information",
    "onboarding instructions",
    "welcome to the team",
    "welcome aboard",
]

    if any(keyword in content for keyword in rejected_keywords):
        status= "rejected"

    elif any(keyword in content for keyword in offered_keywords):
        status= "offered"

    elif any(keyword in content for keyword in interview_keywords):
        status= "interviewing"

    elif any(keyword in content for keyword in applied_keywords):
        status= "applied"


    sender_name, email= parseaddr(sender)

    domain= email.split("@")[-1]
    company_name= domain.split(".")[0]


    return status, company_name


def get_gmail_service_from_db(user_id: int, db):
    from app.models import GmailToken
    
    token_record = db.query(GmailToken).filter(GmailToken.user_id == user_id).first()
    
    if not token_record:
        raise Exception("Gmail not connected for this user")
    
    token_data = json.loads(token_record.token_data)
    
    credentials = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"]
    )
    
    # Refresh if expired
    if credentials.expired and credentials.refresh_token:
        from google.auth.transport.requests import Request
        credentials.refresh(Request())
        # Save refreshed token back to database
        token_data["token"] = credentials.token
        token_record.token_data = json.dumps(token_data)
        db.commit()
    
    return build("gmail", "v1", credentials=credentials)