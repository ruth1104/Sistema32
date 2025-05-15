from app import db
from app.models.record import Records

class Apprentices(db.Model):
   __tablename__ = 'apprentice'
   idApprentice = db.Column(db.Integer, primary_key=True)
   nameApprentice = db.Column(db.String(255), nullable=False)
   documentApprentice = db.Column(db.String(255), unique=True, nullable=True)
   userId = db.Column(db.Integer, db.ForeignKey('user.idUser'), unique=True)
   
   user = db.relationship("User", back_populates="apprentice")
   equipment = db.relationship("Equipments", back_populates="apprentice")
   record = db.relationship("Records", back_populates="apprentice")
   