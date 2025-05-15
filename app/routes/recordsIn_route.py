from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from app.models.instrutor import Instructors
from app.models.equipment import Equipments
from app.models.wachiman import Wachiman
from app.models.recordsIn import RecordsIn
from app.models.user import User
from flask_login import login_required,current_user
from app import db
from datetime import datetime
import pytz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from io import BytesIO
import os



bp = Blueprint('recordsIn', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/recordsIn')
def index():
    data = RecordsIn.query.all()
    return render_template('recordsIn/index.html', data=data)

@bp.route('/recordsIn/add', methods=['GET', 'POST'])
def add():
    colombia_tz = pytz.timezone('America/Bogota')
    if request.method == 'POST':
        
        instructorId = request.form['instructorId']
        wachimanId = request.form['wachimanId']
        equipmentId = request.form['equipmentId']
        dataEntry = datetime.now(colombia_tz)
        dataExit = datetime.now(colombia_tz)
        userId = current_user.idUser
        
        
        newRecordsIn = RecordsIn(userId=userId, instructorId=instructorId, dataEntry=dataEntry, wachimanId=wachimanId, equipmentId=equipmentId, dataExit=dataExit)
        db.session.add(newRecordsIn)
        db.session.commit()
        
        return redirect(url_for('recordsIn.index'))
    
    instructor = Instructors.query.all()
    equipment = Equipments.query.all()
    wachiman = Wachiman.query.all()
    return render_template('recordsIn/add.html', instructor=instructor, equipments=equipment, wachimanes=wachiman)

@bp.route('/recordIn/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    colombia_tz = pytz.timezone('America/Bogota')
    recordsIn = RecordsIn.query.get_or_404(id)
    instructor = Instructors.query.all()
    equipment = Equipments.query.all()
    wachiman = Wachiman.query.all()
    
    if request.method == 'POST':
        try:
            # 🔹 Convertir la fecha de string a datetime
            
            recordsIn.dataEntry = datetime.now(colombia_tz)
            recordsIn.dataExit = datetime.strptime(request.form['dataExit'], "%Y-%m-%dT%H:%M")
            recordsIn.instructorId = request.form['instructorId']
            recordsIn.equipmentId = request.form['equipmentId']
            recordsIn.wachimanId = request.form['wachimanId']
            db.session.commit()
            return redirect(url_for('recordsIn.index'))
        
        except ValueError as e:
            flash(f"Error al actualizar préstamo: {str(e)}", "danger")
            return redirect(url_for('recordsIn.edit', id=id))
    

    return render_template('recordsIn/edit.html', recordsIn=recordsIn, instructor=instructor, equipment=equipment, wachiman=wachiman)

@bp.route('/delete/registro_instructor/<int:id>')
def delete(id):
    recordsIn = RecordsIn.query.get_or_404(id)
    
    db.session.delete(recordsIn)
    db.session.commit()
    
    return redirect(url_for('recordsIn.index'))

@bp.route('/salida/registro_instructor/<int:id>')
def salida(id):
    prestamo = RecordsIn.query.get_or_404(id)
    
    prestamo.dataExit = datetime.now()
    db.session.commit()
  
    return redirect(url_for('recordsIn.index'))

@bp.route('/recordsIn/get_data_by_qr', methods=['GET'])
def get_data_by_qr():
    instructor_id = request.args.get('equipmentId')
    equipment_id = request.args.get('equipmentId')
    user_id = request.args.get('current_user.idUser')
    
    recordIns = RecordsIn.query.filter_by(instructor_id=instructor_id, equipment_id=equipment_id, user_id=user_id).all()

    records_data = [{
        'idRecords': recordIns.idRecords,
        'dataEntry': recordIns.dataEntry,
        'dataExit': recordIns.dataExit,
        'instructor': {'nameInstructor': recordIns.instructor.nameInstructor},
        'user': {'username': recordIns.user.username},
        'equipment': {'codeEquipment': recordIns.equipment.codeEquipment},
        
    } for recordIns in records_data]
      

    return redirect('/addconqr')

@bp.route('/recordsIn/addqr/<int:id>', methods=['GET'])
def addconqr(id):
    equipo = Equipments.query.get_or_404(id)
    
    colombia_tz = pytz.timezone('America/Bogota')
    dataEntry = datetime.now(colombia_tz)
    dataExit = datetime.now(colombia_tz)
    instructorId = equipo.instructorId
    userId = current_user.idUser
    equipmentId = equipo.idEquipment
    

    newRecordIn = RecordsIn(dataEntry=dataEntry, dataExit=dataExit, instructorId=instructorId, userId=userId, equipmentId=equipmentId, )
    db.session.add(newRecordIn)
    db.session.commit()

    return redirect(url_for('recordsIn.index'))

@bp.route('/generar-pdf-Ins')
def generar_pdf_Ins():
    from reportlab.lib import colors
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    # Cargar el logo
    logo_path = os.path.join(current_app.root_path, 'static', 'img', 'logoSena.png')
    logo = Image(logo_path, 1.2 * inch, 1.2 * inch)

    # Crear el texto del encabezado (título + subtítulo en un solo Paragraph)
    header_text = Paragraph(
        "<b>CENTRO DE GESTIÓN AGROEMPRESARIAL DEL ORIENTE</b><br/>"
        "REGISTROS DE ENTRADA/SALIDA DE EQUIPOS",
        normal_style
    )

    # Crear la tabla con logo y texto
    table_data = [[logo, header_text]]
    table = Table(table_data, colWidths=[1.5 * inch, 5.5 * inch])

    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('LEFTPADDING', (1, 0), (1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    data = [['FECHA DE ENTRADA', 'FECHA DE SALIDA', 'INSTRUCTOR', 'CÓDIGO DE EQUIPO', 'CELADOR']]

    registros = RecordsIn.query.all()
    for r in registros:
        data.append([
            r.dataEntry.strftime("%Y-%m-%d %H:%M") if r.dataEntry else "",
            r.dataExit.strftime("%Y-%m-%d %H:%M") if r.dataExit else "",
            r.instructor.nameInstructor if r.instructor else "",
            
            r.equipment.codeEquipment if r.equipment else "",
            r.user.username if r.user else ""
        ])

    from reportlab.lib import colors

    table = Table(data, colWidths=[110, 110, 140, 120, 100])
    table.setStyle(TableStyle([
         # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2e7d32")),  # Verde oscuro
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Contenido
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),

        # Bordes y rejilla
        ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor("#43a047")),  # Borde verde medio
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#a5d6a7")),

        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # Pie de página
    footer = Paragraph(
        "Este documento fue generado automáticamente por el sistema de control de equipos 2025.",
        normal_style
    )
    story.append(footer)
    story.append(Spacer(1, 24))
    
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="registro_instructores.pdf", mimetype='application/pdf')
