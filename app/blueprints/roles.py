from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Rol
from app.extensions import db

bp = Blueprint('roles', __name__, url_prefix='/roles')

@bp.route('/')
@login_required
def index():
    roles = Rol.query.all()
    return render_template('roles/index.html', roles=roles)

@bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if not nombre:
            flash('El campo Nombre es obligatorio.', 'danger')
            return render_template('roles/form.html', rol=None)

        if Rol.query.filter_by(nombre=nombre).first():
            flash('Ya existe un rol con ese nombre.', 'danger')
            return render_template('roles/form.html', rol=None)

        rol = Rol(
            nombre=nombre,
            descripcion=descripcion,
            creado_por=current_user.username,
            actualizado_por=current_user.username
        )
        db.session.add(rol)
        db.session.commit()
        flash('Rol creado exitosamente.', 'success')
        return redirect(url_for('roles.index'))

    return render_template('roles/form.html', rol=None)

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    rol = Rol.query.get_or_404(id)

    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre', '').strip()
        nueva_descripcion = request.form.get('descripcion', '').strip()

        if not nuevo_nombre:
            flash('El campo Nombre es obligatorio.', 'danger')
            return render_template('roles/form.html', rol=rol)

        duplicado = Rol.query.filter(Rol.nombre == nuevo_nombre, Rol.id != id).first()
        if duplicado:
            flash('Ya existe otro rol con ese nombre.', 'danger')
            return render_template('roles/form.html', rol=rol)

        rol.nombre = nuevo_nombre
        rol.descripcion = nueva_descripcion
        rol.actualizado_por = current_user.username
        
        db.session.commit()
        flash('Rol actualizado correctamente.', 'success')
        return redirect(url_for('roles.index'))

    return render_template('roles/form.html', rol=rol)
