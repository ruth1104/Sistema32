from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, current_app, send_file
from app.models.apprentice import Apprentices
from app.models.equipment import Equipments
from app.models.wachiman import Wachiman
from app.models.record import Records
from app.models.user import User
from app import db
from flask_login import login_required, current_user
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

bp = Blueprint('record', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/record')
def index():
    data = Records.query.all()
    return render_template('record/index.html', data=data)

@bp.route('/record/add', methods=['GET', 'POST'])
def add():
    colombia_tz = pytz.timezone('America/Bogota')
    if request.method == 'POST':
        
        apprenticeId = request.form['apprenticeId']
        wachimanId = request.form['wachimanId']
        equipmentId = request.form['equipmentId']
        dataEntry = datetime.now(colombia_tz)
        dataExit = datetime.now(colombia_tz)
        userId = current_user.idUser
        
        
        newRecords = Records(apprenticeId=apprenticeId, dataEntry=dataEntry, wachimanId=wachimanId, equipmentId=equipmentId, dataExit=dataExit, userId= userId)
        db.session.add(newRecords)
        db.session.commit()
        
        return redirect(url_for('record.index'))
    
    apprentice = Apprentices.query.all()
    equipment = Equipments.query.all()
    wachiman = Wachiman.query.all()
    return render_template('record/add.html', apprentices=apprentice, equipments=equipment, wachimanes=wachiman)
    

@bp.route('/record/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    colombia_tz = pytz.timezone('America/Bogota')
    record = Records.query.get_or_404(id)
    apprentice = Apprentices.query.all()
    equipment = Equipments.query.all()
    wachiman = Wachiman.query.all()
    
    if request.method == 'POST':
        try:
            # 🔹 Convertir la fecha de string a datetime
            
            record.dataEntry = datetime.now(colombia_tz)
            record.dataExit = datetime.strptime(request.form['dataExit'], "%Y-%m-%dT%H:%M")
            record.apprenticeId = request.form['apprenticeId']
            record.equipmentId = request.form['equipmentId']
            record.wachimanId = request.form['wachimanId']
            db.session.commit()
            return redirect(url_for('record.index'))
        
        except ValueError as e:
            flash(f"Error al actualizar préstamo: {str(e)}", "danger")
            return redirect(url_for('record.edit', id=id))
    

    return render_template('record/edit.html', record=record, apprentice=apprentice, equipment=equipment, wachiman=wachiman)

@bp.route('/recorsd/delete/<int:id>')
def delete(id):
    record = Records.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    
    return redirect(url_for('record.index'))

@bp.route('/salida/<int:id>')
def salida(id):
    prestamo = Records.query.get_or_404(id)
    
    prestamo.dataExit = datetime.now()
    db.session.commit()
  
    return redirect(url_for('record.index'))



@bp.route('/record/get_data_by_qr', methods=['GET'])
def get_data_by_qr():
    apprentice_id = request.args.get('apprenticeId')
    equipment_id = request.args.get('equipmentId')
    user_id = request.args.get('current_user.idUser')
    
    record = Records.query.filter_by(apprentice_id=apprentice_id, equipment_id=equipment_id,user_id=user_id).all()

    records_data = [{
        'idRecords': record.idRecords,
        'dataEntry': record.dataEntry,
        'dataExit': record.dataExit,
        'apprentice': {'nameApprentice': record.apprentice.nameApprentice},
        'equipment': {'codeEquipment': record.equipment.codeEquipment},
        'user': {'username': record.user.username}
    } for record in records_data]
      

    return redirect('/addconqr')

@bp.route('/record/addqr/<int:id>', methods=['GET'])
def addconqr(id):
    equipo = Equipments.query.get_or_404(id)
    colombia_tz = pytz.timezone('America/Bogota')

    apprenticeId = equipo.apprenticeId
    userId = current_user.idUser
    equipmentId = equipo.idEquipment
    dataEntry = datetime.now(colombia_tz)
    dataExit = datetime.now(colombia_tz)

    newRecord = Records(
        apprenticeId=apprenticeId,
        userId=userId,
        equipmentId=equipmentId,
        dataEntry=dataEntry,
        dataExit=dataExit
    )
    db.session.add(newRecord)
    db.session.commit()

    return redirect(url_for('record.index'))

@bp.route('/generar-pdf-apr')
def generar_pdf_apr():
    from reportlab.lib import colors
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    # Cargar el logo
    logo_path = os.path.join(current_app.root_path, 'static', 'img', 'logoSena.png')
    logo = Image(logo_path, 0.8 * inch, 0.8 * inch)

    # Crear el texto del encabezado (título + subtítulo en un solo Paragraph)
    header_text = Paragraph(
        "<b>CENTRO DE GESTIÓN AGROEMPRESARIAL DEL ORIENTE</b><br/>"
        "REGISTROS DE ENTRADA/SALIDA DE EQUIPOS",
        normal_style
    )

    # Crear la tabla con logo y texto
    table_data = [[logo, header_text]]
    table = Table(table_data, colWidths=[1.0 * inch, 5.5 * inch])

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

    
    styles = getSampleStyleSheet()
    header_style = styles['Normal']
    header_style.fontSize = 10
    header_style.alignment = 1  # Centrado

    data = [[
        Paragraph("FECHA<br/>ENTRADA", header_style),
        Paragraph("FECHA<br/>SALIDA", header_style),
        Paragraph("APRENDIZ", header_style),
        Paragraph("CÓDIGO<br/>EQUIPO", header_style),
        Paragraph("CELADOR", header_style)
    ]]

    registros = Records.query.all()
    for r in registros:
        data.append([
            r.dataEntry.strftime("%Y-%m-%d %H:%M") if r.dataEntry else "",
            r.dataExit.strftime("%Y-%m-%d %H:%M") if r.dataExit else "",
            r.apprentice.nameApprentice if r.apprentice else "",
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
    return send_file(buffer, as_attachment=True, download_name="registro_Aprendices.pdf", mimetype='application/pdf')
    
