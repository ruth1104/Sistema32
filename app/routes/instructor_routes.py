from flask import Blueprint, render_template, request, redirect, url_for, current_app
from app.models.instrutor import Instructors
from flask_login import login_required
from app import db


bp = Blueprint('intructor', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/instructor/index')
def index():
    data = Instructors.query.all()
    return render_template('instructor/index.html', data=data)

@bp.route('/intructor/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nameInstructor = request.form['nameInstructor']
        documentInstructor = request.form['documentInstructor']
        
        newInstructors = Instructors(nameInstructor=nameInstructor, documentInstructor=documentInstructor)
        db.session.add(newInstructors)
        db.session.commit()
        
        return redirect(url_for('intructor.index'))

    return render_template('instructor/add.html')

@bp.route('/intructor/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    intructor= Instructors.query.get_or_404(id)

    if request.method == 'POST':
        intructor.nameInstructor = request.form['nameInstructor']
        intructor.documentInstructor =request.form['documentInstructor']
        db.session.commit()        
        return redirect(url_for('intructor.index'))

    return render_template('instructor/edit.html', intructor=intructor)

@bp.route('/intructor/delete/<int:id>')
def delete(id):
   intructor = Instructors.query.get_or_404(id)
   
   db.session.delete(intructor)
   db.session.commit()
   
   return redirect(url_for('intructor.index'))