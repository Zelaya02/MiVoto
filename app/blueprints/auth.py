from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Usuario, LoginLog
from app.extensions import bcrypt, db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"DEBUG LOGIN - Username: '{username}', Password: '{password}'")
        
        user = Usuario.query.filter_by(username=username).first()
        
        # Ojo: Aquí estamos asumiendo que el password_hash en la BD es válido con bcrypt.
        # Si usas contraseñas en texto plano para desarrollo, debes cambiarlas a hash.
        if user and user.activo and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            log = LoginLog(
                username=user.username,
                nombre_completo=user.nombre_completo,
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            flash('Inicio de sesión exitoso.', 'success')
            
            # Redirigir a la URL solicitada originalmente, si existe
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos, o cuenta inactiva.', 'danger')
            
    # HTMX request support (si es una petición HTMX de error, re-renderizamos el form)
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))
