from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Usuario, Rol
from app.extensions import db, bcrypt

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.tiene_permiso('usuarios'):
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated

@bp.route('/')
@admin_required
def index():
    usuarios = Usuario.query.all()
    return render_template('usuarios/index.html', usuarios=usuarios)

@bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo():
    roles = Rol.query.all()
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        nombre_completo = request.form.get('nombre_completo', '').strip()
        password = request.form.get('password', '')
        rol_id = request.form.get('rol_id')

        if not username or not email or not password or not rol_id:
            flash('Por favor complete todos los campos obligatorios.', 'danger')
            return render_template('usuarios/form.html', usuario=None, roles=roles)

        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'danger')
            return render_template('usuarios/form.html', usuario=None, roles=roles)

        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'danger')
            return render_template('usuarios/form.html', usuario=None, roles=roles)

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        usuario = Usuario()
        usuario.username = username
        usuario.email = email
        usuario.nombre_completo = nombre_completo
        usuario.password_hash = hashed_password
        usuario.rol_id = rol_id
        usuario.creado_por = current_user.username
        usuario.actualizado_por = current_user.username
        db.session.add(usuario)
        db.session.commit()
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template('usuarios/form.html', usuario=None, roles=roles)

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar(id):
    usuario = Usuario.query.get_or_404(id)
    roles = Rol.query.all()

    if request.method == 'POST':
        nuevo_username = request.form.get('username', '').strip()
        nuevo_email = request.form.get('email', '').strip()
        nombre_completo = request.form.get('nombre_completo', '').strip()
        password = request.form.get('password', '')
        activo = request.form.get('activo') == 'true'

        if not nuevo_username or not nuevo_email:
            flash('Username y Email son obligatorios.', 'danger')
            return render_template('usuarios/form.html', usuario=usuario, roles=roles)

        if Usuario.query.filter(Usuario.username == nuevo_username, Usuario.id != id).first():
            flash('El nombre de usuario ya está en uso por otra persona.', 'danger')
            return render_template('usuarios/form.html', usuario=usuario, roles=roles)

        if Usuario.query.filter(Usuario.email == nuevo_email, Usuario.id != id).first():
            flash('El email ya está en uso por otra persona.', 'danger')
            return render_template('usuarios/form.html', usuario=usuario, roles=roles)

        usuario.username = nuevo_username
        usuario.email = nuevo_email
        usuario.nombre_completo = nombre_completo
        usuario.actualizado_por = current_user.username

        # El usuario admin no puede cambiar de rol ni desactivarse
        if usuario.username != 'admin':
            rol_id = request.form.get('rol_id')
            if not rol_id:
                flash('El rol es obligatorio.', 'danger')
                return render_template('usuarios/form.html', usuario=usuario, roles=roles)
            usuario.rol_id = rol_id
            usuario.activo = activo

        if password:
            usuario.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template('usuarios/form.html', usuario=usuario, roles=roles)
