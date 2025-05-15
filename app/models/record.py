from app import db


class Records(db.Model):
   __tablename__ = 'record'
   idRecords = db.Column(db.Integer, primary_key=True)
   dataEntry = db.Column(db.DateTime, nullable=False)
   dataExit = db.Column(db.DateTime, nullable=True)
   apprenticeId = db.Column(db.Integer, db.ForeignKey('apprentice.idApprentice'))
   wachimanId = db.Column(db.Integer, db.ForeignKey('wachiman.idWachiman'))
   equipmentId = db.Column(db.Integer, db.ForeignKey('equipment.idEquipment'))
   userId = db.Column(db.Integer, db.ForeignKey('user.idUser'))
   
   
   user = db.relationship('User', back_populates='record')
   apprentice = db.relationship("Apprentices", back_populates="record")
   equipment = db.relationship("Equipments", back_populates="record")
   wachiman = db.relationship("Wachiman", back_populates="record")
   