from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from app.models.roomLoan import RoomsLoans
from app.models.instrutor import Instructors
from app.models.room import Rooms
from app.models.wachiman import Wachiman
from flask_login import login_required, current_user
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

bp = Blueprint('roomLoan', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/roomLoan')
def index():
    roomLoan = RoomsLoans.query.all()
    instructors = Instructors.query.all()
    return render_template('roomLoan/index.html', roomLoan=roomLoan, instructors=instructors)

@bp.route('/roomLoan/add', methods=['GET', 'POST'])
def add():
    colombia_tz = pytz.timezone('America/Bogota')
    
    if request.method == 'POST':
        returnDate = request.form['datetime']
        instructorId = request.form.get('instrutorId') or None
        wachimanId = request.form.get('wachimanId') or None
        roomId = request.form['roomId']
        date = datetime.now(colombia_tz)
        userId = current_user.idUser

        return_date = datetime.strptime(returnDate, "%Y-%m-%dT%H:%M") if returnDate else None

        newLoan = RoomsLoans(
            instructorId=instructorId,
            date=date,
            wachimanId=wachimanId,
            roomId=roomId,
            returnDate=return_date,
            userId=userId
        )
        db.session.add(newLoan)
        db.session.commit()
        
        return redirect(url_for('roomLoan.index'))

    instructors = Instructors.query.all()
    wachiman = Wachiman.query.all()
    rooms = Rooms.query.all()

    return render_template(
        'roomLoan/add.html',
        instructors=instructors,
        wachiman=wachiman,
        rooms=rooms,
        user=current_user
    )

@bp.route('/roomLoan/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    roomLoan = RoomsLoans.query.get_or_404(id)
    instructor = Instructors.query.all()
    room = Rooms.query.all()
    wachiman = Wachiman.query.all()

    if request.method == 'POST':
        try:
            roomLoan.date = datetime.strptime(request.form['date'], "%Y-%m-%dT%H:%M")
            roomLoan.returnDate = datetime.strptime(request.form['returnDate'], "%Y-%m-%dT%H:%M")
            roomLoan.instructorId = request.form['instructorId']
            roomLoan.wachimanId = request.form['wachimanId']
            roomLoan.roomId = request.form['roomId']
            db.session.commit()
            return redirect(url_for('roomLoan.index'))
        
        except ValueError as e:
            flash(f"Error al actualizar préstamo: {str(e)}", "danger")
            return redirect(url_for('roomLoan.edit', id=id))

    return render_template('roomLoan/edit.html', roomLoan=roomLoan, instructors=instructor, rooms=room, wachiman=wachiman)

@bp.route('/delete/<int:id>')
def delete(id):
    roomLoan = RoomsLoans.query.get_or_404(id)
    db.session.delete(roomLoan)
    db.session.commit()
    return redirect(url_for('roomLoan.index'))

@bp.route('/devolver/<int:id>')
def devolver(id):
    prestamo = RoomsLoans.query.get_or_404(id)
    prestamo.returnDate = datetime.now()
    db.session.commit()
    return redirect(url_for('roomLoan.index'))



@bp.route('/roomloan/get_data_by_qr', methods=['GET'])
def get_data_by_qr():
    instructor_id = request.args.get('instructorId')
    wachiman_id = request.args.get('wachimanId')
    room_id = request.args.get('roomId')
    
    loans = RoomsLoans.query.filter_by(
        instructorId=instructor_id,
        wachimanId=wachiman_id,
        roomId=room_id
    ).all()

    loans_data = [{
        'idRoomLoan': loan.idRoomLoan,
        'date': loan.date,
        'returnDate': loan.returnDate,
        'user': {'username': loan.user.username},
        'room': {'nameRoom': loan.room.nameRoom}
    } for loan in loans]

    return redirect('/roomloan/addconqr')
@bp.route('/roomloan/addqr/<int:id>', methods=['GET', 'POST'])
def addconqr(id):
    room = Rooms.query.get_or_404(id)
    colombia_tz = pytz.timezone('America/Bogota')
    user_id = current_user.idUser
    date = datetime.now(colombia_tz)
    return_date = None

    # Asignar campos según el rol del usuario
    instructor_id = user_id if current_user.rol == 'instructor' else None
    wachiman_id = user_id if current_user.rol == 'celador' else None

    try:
        new_loan = RoomsLoans(
            roomId=room.idRoom,
            userId=user_id,
            date=date,
            returnDate=return_date,
            instructorId=instructor_id,
            wachimanId=wachiman_id
        )
        db.session.add(new_loan)
        db.session.commit()
        flash("Préstamo registrado exitosamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar el préstamo: {str(e)}", "danger")

    return redirect(url_for('roomLoan.index'))

@bp.route('/generar-pdf-room')
def generar_pdf_room():
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
        Paragraph("FECHA<br/>ENTREGA", header_style),
        Paragraph("FECHA<br/>DEVOLUNCION", header_style),
        Paragraph("INSTRUCTOR", header_style),
        Paragraph("NOMBRE<br/>SALÒN", header_style),
        Paragraph("CELADOR", header_style)
    ]]

    registros = RoomsLoans.query.all()
    for r in registros:
        data.append([
            r.date.strftime("%Y-%m-%d %H:%M") if r.date else "",
            r.returnDate.strftime("%Y-%m-%d %H:%M") if r.returnDate else "",
            r.instructor.nameInstructor if r.instructor else "",
            r.room.nameRoom if r.room else "",
            r.user.username if r.user else "",        
            
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
    return send_file(buffer, as_attachment=True, download_name="registro_prestamos.pdf", mimetype='application/pdf')
    
