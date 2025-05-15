from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required
from app import db
from app.models.user import User
from functools import wraps
from flask_login import current_user

bp = Blueprint('auth', __name__)

@bp.route('/indexUser')
@login_required
def index():
    users = User.query.all()
    return render_template('login/index.html', users=users)

@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("nameUser")
        password = request.form.get("passwordUser")
        

        user = User.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                login_user(user)

                if user.rol == "Aprendiz":
                    return redirect(url_for("apprentice.index", id=user.idUser))
                elif user.rol == "Celador":
                    return redirect(url_for("wachiman.index", id=user.idUser))
                elif user.rol == "Instructor":
                    return redirect(url_for("intructor.index", id=user.idUser))
                else:
                    flash("Rol no reconocido", "danger")
            else:
                flash("Contraseña incorrecta", "danger")
        else:
            flash("Usuario no encontrado", "danger")

    return render_template("login/login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/add', methods=['GET', 'POST'])    
def add():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        rol = request.form.get('rol', 'Aprendiz')  # Valor por defecto

        # Validar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El nombre de usuario ya está registrado', 'error')
            return redirect(url_for('auth.add'))

        # Crear nuevo usuario con rol incluido
        new_user = User(username=username, password=password, rol=rol)
        db.session.add(new_user)
        db.session.commit()

        # Iniciar sesión y redirigir según rol
        login_user(new_user)
        if new_user.rol == "Aprendiz":
            return redirect(url_for('apprentice.index', id=new_user.idUser))
        elif new_user.rol == "Celador":
            return redirect(url_for('wachiman.index', id=new_user.idUser))
        elif new_user.rol == "Instructor":
            return redirect(url_for('intructor.index', id=new_user.idUser))

    return render_template('login/add.html')


@bp.route('/user/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.username = request.form['username']
        
        new_password = request.form['password']
        if new_password:
            user.password = request.form['password']

        user.rol = request.form['rol']
        db.session.commit()
        
        return redirect(url_for('auth.index'))

    return render_template('login/edit.html', user=user)

@bp.route('/user/delete/<int:id>')
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('auth.index'))