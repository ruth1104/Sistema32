from app import db

class Instructors(db.Model):
   __tablename__ = 'instructor'
   idInstructor = db.Column(db.Integer, primary_key=True)
   nameInstructor = db.Column(db.String(255), nullable=True)
   documentInstructor = db.Column(db.String(255), unique=True, nullable=True)
   userId = db.Column(db.Integer, db.ForeignKey('user.idUser'), unique=True)
   
   user = db.relationship("User", back_populates="instructor")
   equipment = db.relationship("Equipments", back_populates="instructor")
   roomLoan = db.relationship("RoomsLoans", back_populates="instructor")
   recordsIn = db.relationship("RecordsIn", back_populates="instructor")