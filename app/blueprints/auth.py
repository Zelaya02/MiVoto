import secrets
import string
import threading
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Usuario, LoginLog
from app.extensions import bcrypt, db
from app.mail_helper import enviar_email

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Usuario.query.filter_by(username=username).first()

        if user and user.activo and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            log = LoginLog(
                username=user.username,
                nombre_completo=user.nombre_completo,
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()

            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos, o cuenta inactiva.', 'danger')

    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/olvide-contrasena', methods=['GET', 'POST'])
def olvide_contrasena():
    # Si ya está logueado, cerrar sesión para que tenga que re-ingresar con la nueva pass
    if current_user.is_authenticated:
        logout_user()

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if not email:
            flash('Por favor ingresa tu correo electrónico.', 'danger')
            return render_template('auth/olvide_contrasena.html')

        user = Usuario.query.filter_by(email=email).first()

        if not user:
            flash('No existe una cuenta con ese correo electrónico.', 'danger')
            return render_template('auth/olvide_contrasena.html')

        nueva_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        user.password_hash = bcrypt.generate_password_hash(nueva_pass).decode('utf-8')
        db.session.commit()

        current_app.logger.info(f'NUEVA PASSWORD para {user.username}: {nueva_pass}')
        print(f'*** NUEVA PASSWORD para {user.username}: {nueva_pass} ***')

        asunto = 'Mi Voto - Nueva contraseña'
        cuerpo = f'''
        <h2>Recuperación de contraseña</h2>
        <p>Hola <strong>{user.nombre_completo or user.username}</strong>,</p>
        <p>Se ha generado una nueva contraseña para tu cuenta:</p>
        <p style="font-size:18px; background:#f0f0f0; padding:12px; border-radius:8px; text-align:center;">
            <strong>{nueva_pass}</strong>
        </p>
        <p>Te recomendamos cambiarla después de iniciar sesión.</p>
        <p>Si no solicitaste este cambio, contacta al administrador del sistema.</p>
        <hr><p style="color:#888;font-size:12px;">Mi Voto 2.0</p>
        '''

        # Enviar email en segundo plano — la respuesta web es inmediata
        def _enviar(app):
            with app.app_context():
                enviar_email(email, asunto, cuerpo)
        hilo = threading.Thread(target=_enviar, args=(current_app._get_current_object(),))
        hilo.start()

        flash(f'Se ha enviado una nueva contraseña a {email}. Revisa tu bandeja de entrada.', 'success')
        flash(f'Tu nueva contraseña es: {nueva_pass}', 'warning')
        return redirect(url_for('auth.login'))

    return render_template('auth/olvide_contrasena.html')
