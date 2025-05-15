from app import db


class RecordsIn(db.Model):
   __tablename__ = 'recordsIn'
   idRecordsIn = db.Column(db.Integer, primary_key=True)
   dataEntry = db.Column(db.DateTime, nullable=False)
   dataExit = db.Column(db.DateTime, nullable=True)
   instructorId = db.Column(db.Integer, db.ForeignKey('instructor.idInstructor'))
   wachimanId = db.Column(db.Integer, db.ForeignKey('wachiman.idWachiman'))
   equipmentId = db.Column(db.Integer, db.ForeignKey('equipment.idEquipment'))
   userId = db.Column(db.Integer, db.ForeignKey('user.idUser'))
   
   
   user = db.relationship('User', back_populates='recordsIn')
   instructor = db.relationship("Instructors", back_populates="recordsIn")
   equipment = db.relationship("Equipments", back_populates="recordsIn")
   wachiman = db.relationship("Wachiman", back_populates="recordsIn")
   
   