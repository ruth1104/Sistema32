from flask import Blueprint, render_template, request, redirect, url_for
from app.models.apprentice import Apprentices
from flask_login import login_required
from flask_login import current_user
from app import db

bp = Blueprint('apprentice', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/apprentice')
def index():
    data = Apprentices.query.all()   
    return render_template('apprentice/index.html', data=data)

@bp.route('/apprentice/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nameApprentice = request.form['nameApprentice']
        documentApprentice = request.form['documentApprentice']
        
        
        newApprentice = Apprentices(nameApprentice=nameApprentice, documentApprentice=documentApprentice)
        db.session.add(newApprentice)
        db.session.commit()
        
        return redirect(url_for('apprentice.index'))

    return render_template('apprentice/add.html')

@bp.route('/apprentice/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    apprentice= Apprentices.query.get_or_404(id)

    if request.method == 'POST':
        apprentice.nameApprentice = request.form['nameApprentice']
        apprentice.documentApprentice =request.form['documentApprentice']
        
        db.session.commit()        
        return redirect(url_for('apprentice.index'))

    return render_template('apprentice/edit.html', apprentice=apprentice)

@bp.route('/apprentice/delete/<int:id>')
def delete(id):
   apprentice = Apprentices.query.get_or_404(id)
   
   db.session.delete(apprentice)
   db.session.commit()
   
   return redirect(url_for('apprentice.index'))

