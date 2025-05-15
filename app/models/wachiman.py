from app import db

class Wachiman(db.Model):
   __tablename__ = 'wachiman'
   idWachiman = db.Column(db.Integer, primary_key=True)
   nameWachiman = db.Column(db.String(255), nullable=False)
   documentWachiman = db.Column(db.String(255), unique=True, nullable=False)
   userId = db.Column(db.Integer, db.ForeignKey('user.idUser'), unique=True)
   
   user = db.relationship("User", back_populates="wachiman")
   roomLoan = db.relationship("RoomsLoans", back_populates="wachiman")
   record = db.relationship("Records", back_populates="wachiman")
   recordsIn = db.relationship("RecordsIn", back_populates="wachiman")
   