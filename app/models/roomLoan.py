from app import db
from datetime import datetime

class RoomsLoans(db.Model):
   __tablename__ = 'roomLoan'
   
   idRoomLoan = db.Column(db.Integer, primary_key=True)
   date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   returnDate = db.Column(db.DateTime, nullable=True)
   instructorId = db.Column(db.Integer, db.ForeignKey('instructor.idInstructor'))
   wachimanId = db.Column(db.Integer, db.ForeignKey('wachiman.idWachiman'))
   roomId = db.Column(db.Integer, db.ForeignKey('room.idRoom'))
   userId = db.Column(db.Integer, db.ForeignKey('user.idUser'))
   
   user = db.relationship('User', back_populates='roomLoan')
   instructor = db.relationship("Instructors", back_populates="roomLoan")
   room = db.relationship("Rooms", back_populates="roomLoan")
   wachiman = db.relationship("Wachiman", back_populates="roomLoan")