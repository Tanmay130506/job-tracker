from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import ForeignKey
import enum

class User(Base):
    __tablename__="users"

    user_id=Column(Integer, primary_key=True, index= True)
    username=Column(String, unique=True, index=True)
    hashed_password=Column(String)
    email=Column(String, unique=True)
    
    applications=relationship("Application", back_populates="user")

class Application(Base):
    __tablename__="applications"
    
    user_id=Column(Integer, ForeignKey("users.user_id"))
    application_id=Column(Integer, primary_key=True, index=True)
    company_name=Column(String)
    role=Column(String)
    status=Column(String)
    date=Column(DateTime)
    applied_through_email=Column(Boolean)

    user=relationship("User", back_populates="applications")
    history=relationship("ApplicationHistory", back_populates="applications")

class ApplicationHistory(Base):
    __tablename__= "history"

    history_id=Column(Integer, primary_key=True, index=True)
    application_id=Column(Integer, ForeignKey("applications.application_id"))
    old_status=Column(String)
    new_status=Column(String)
    date=Column(DateTime)
    changed_through_email=Column(Boolean)
    email=Column(String, nullable=True)

    applications=relationship("Application", back_populates="history")