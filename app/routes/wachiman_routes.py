from flask import Blueprint, render_template, request, redirect, url_for
from app.models.wachiman import Wachiman
from flask_login import login_required
from app import db

bp = Blueprint('wachiman', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/wachiman')
def index():
    data = Wachiman.query.all()   
    return render_template('Wachiman/index.html', data=data)

@bp.route('/wachiman/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nameWachiman = request.form['nameWachiman']
        documentWachiman = request.form['documentWachiman']
        
        newWachiman = Wachiman(nameWachiman=nameWachiman, documentWachiman=documentWachiman)
        db.session.add(newWachiman)
        db.session.commit()
        
        return redirect(url_for('wachiman.index'))

    return render_template('Wachiman/add.html')

@bp.route('/wachiman/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    wachiman= Wachiman.query.get_or_404(id)

    if request.method == 'POST':
        wachiman.nameWachiman = request.form['nameWachiman']
        wachiman.documentWachiman =request.form['documentWachiman']
        db.session.commit()        
        return redirect(url_for('wachiman.index'))

    return render_template('wachiman/edit.html', wachiman=wachiman)

@bp.route('/wachiman/delete/<int:id>')
def delete(id):
   caretaker = Wachiman.query.get_or_404(id)
   
   db.session.delete(caretaker)
   db.session.commit()
   
   return redirect(url_for('wachiman.index'))