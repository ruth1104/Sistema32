from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    idUser = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(300), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    rol = db.Column(db.String(300), nullable=True, default="Aprendiz") 
    
    recordsIn = db.relationship("RecordsIn", back_populates="user")
    roomLoan = db.relationship("RoomsLoans", back_populates="user")
    record = db.relationship("Records", back_populates="user")
    apprentice = db.relationship("Apprentices", back_populates="user")
    instructor = db.relationship("Instructors", back_populates="user")
    wachiman = db.relationship("Wachiman", back_populates="user")
   

    def get_id(self):
        return str(self.idUser)