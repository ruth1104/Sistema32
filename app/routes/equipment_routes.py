from flask import Blueprint, render_template, request, redirect, url_for, send_file
from app.models.equipment import Equipments
from app.models.apprentice import Apprentices
from app.models.instrutor import Instructors
from io import BytesIO
import base64
from flask_login import login_required, current_user
from app import db

bp = Blueprint('equipment', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/equipment/index')
def index():
    print("Entra a equpo")
    data = Equipments.query.all()   
    return render_template('equipment/index.html', data=data)

@bp.route('/equipment/index1')
def index1():
    print(current_user)
    print(current_user.rol)
    print(current_user.equipment)
    print("Entra a equpo")
    if current_user.rol == "Aprendiz":
        data = current_user.equipment
        print("en el if")
        print(data)
    data = Equipments.query.all()   
    return render_template('equipment/index.html', data=data)


@bp.route('/equipment/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        brandEquipment = request.form['brandEquipment']
        codeEquipment = request.form['codeEquipment']
        accassoriesEquipment = request.form['accassoriesEquipment']
        apprenticeId = request.form['apprenticeId'] 
        instructorId = request.form['instructorId']       
        newEquipment = Equipments(brandEquipment=brandEquipment, codeEquipment=codeEquipment, accassoriesEquipment=accassoriesEquipment, apprenticeId=apprenticeId, instructorId=instructorId )
        db.session.add(newEquipment)
        db.session.commit()
        
        return redirect(url_for('equipment.index'))
    
    adata = Apprentices.query.all()
    idata = Instructors.query.all()
    return render_template('equipment/add.html', adata = adata, idata=idata)

@bp.route('/equipment/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    equipment= Equipments.query.get_or_404(id)
    apprentices = Apprentices.query.all()

    if request.method == 'POST':
        equipment.brandEquipment = request.form['brandEquipment']
        equipment.codeEquipment =request.form['codeEquipment']
        equipment.accassoriesEquipment= request.form ['accassoriesEquipment']
        equipment.apprenticeId= request.form ['apprenticeId']
        db.session.commit()        
        return redirect(url_for('equipment.index'))

    return render_template('equipment/edit.html', equipment=equipment, apprentices = apprentices)

@bp.route('/equipment/delete/<int:id>')
def delete(id):
   equipment = Equipments.query.get_or_404(id)
   db.session.delete(equipment)
   db.session.commit()
   
   return redirect(url_for('equipment.index'))

@bp.route('/qr/<int:id>')
def generate_qr(id):
    print("Entrando a la ruta de generación de QR para el usuario con ID:", id)
    equipement = Equipments.query.get_or_404(id)
    qr_code_base64 = equipement.generate_qr()
    # Decodificar la imagen del QR desde base64
    qr_code_img = base64.b64decode(qr_code_base64)
    return send_file(BytesIO(qr_code_img), mimetype='image/png')


