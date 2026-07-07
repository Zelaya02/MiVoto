from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Socio, Estado, AuditLog
from app.extensions import db

bp = Blueprint('socios', __name__, url_prefix='/socios')

@bp.route('/')
@login_required
def index():
    if not current_user.tiene_permiso('socios'):
        flash('No tienes permisos para acceder a esta secci&oacute;n.', 'danger')
        return redirect(url_for('dashboard.index'))
    q = request.args.get('q', '')
    if q:
        socios = Socio.query.filter(
            (Socio.cedula.ilike(f'%{q}%')) | 
            (Socio.apellidos.ilike(f'%{q}%')) |
            (Socio.nombres.ilike(f'%{q}%'))
        ).limit(50).all()
    else:
        socios = Socio.query.limit(50).all()
        
    return render_template('socios/index.html', socios=socios, q=q)


@bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        cedula        = request.form.get('cedula', '').strip()
        nombres       = request.form.get('nombres', '').strip()
        apellidos     = request.form.get('apellidos', '').strip()
        fecha_nac     = request.form.get('fecha_nacimiento') or None
        fecha_ing     = request.form.get('fecha_ingreso') or None
        sexo          = request.form.get('sexo', '').strip()
        trabajo       = request.form.get('trabajo', '').strip()
        agencia       = request.form.get('agencia', '').strip()
        situacion     = request.form.get('situacion', 'activo').strip()

        if not cedula or not nombres or not apellidos:
            flash('Los campos Cédula, Nombres y Apellidos son obligatorios.', 'danger')
            return render_template('socios/form.html', socio=None)

        if Socio.query.filter_by(cedula=cedula).first():
            flash('Ya existe un socio con esa cédula.', 'danger')
            return render_template('socios/form.html', socio=None)

        # Generar nro_socio auto-incremental
        ultimo = Socio.query.order_by(Socio.nro_socio.desc()).first()
        if ultimo and ultimo.nro_socio and ultimo.nro_socio.isdigit():
            nuevo_nro = str(int(ultimo.nro_socio) + 1).zfill(len(ultimo.nro_socio))
        else:
            nuevo_nro = '0001'

        socio = Socio()
        socio.nro_socio = nuevo_nro
        socio.cedula = cedula
        socio.nombres = nombres
        socio.apellidos = apellidos
        socio.fecha_nacimiento = fecha_nac
        socio.fecha_ingreso = fecha_ing
        socio.sexo = sexo
        socio.trabajo = trabajo
        socio.agencia = agencia
        socio.situacion = situacion
        socio.creado_por = current_user.username
        socio.actualizado_por = current_user.username
        db.session.add(socio)
        db.session.commit()
        db.session.add(AuditLog(usuario=current_user.username, accion='crear', tipo_objeto='Socio', objeto_id=socio.nro_socio, detalle=f'{socio.apellidos}, {socio.nombres}'))
        db.session.commit()
        flash('Socio creado exitosamente.', 'success')
        return redirect(url_for('socios.index'))

    return render_template('socios/form.html', socio=None)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    socio = Socio.query.get_or_404(id)

    if request.method == 'POST':
        nueva_cedula    = request.form.get('cedula', '').strip()
        nombres         = request.form.get('nombres', '').strip()
        apellidos       = request.form.get('apellidos', '').strip()
        fecha_nac       = request.form.get('fecha_nacimiento') or None
        fecha_ing       = request.form.get('fecha_ingreso') or None
        sexo            = request.form.get('sexo', '').strip()
        trabajo         = request.form.get('trabajo', '').strip()
        agencia         = request.form.get('agencia', '').strip()
        situacion       = request.form.get('situacion', 'activo').strip()

        if not nueva_cedula or not nombres or not apellidos:
            flash('Los campos Cédula, Nombres y Apellidos son obligatorios.', 'danger')
            return render_template('socios/form.html', socio=socio)

        duplicado_cedula = Socio.query.filter(Socio.cedula == nueva_cedula, Socio.id != id).first()
        if duplicado_cedula:
            flash('Ya existe otro socio con esa cédula.', 'danger')
            return render_template('socios/form.html', socio=socio)

        socio.cedula           = nueva_cedula
        socio.nombres          = nombres
        socio.apellidos        = apellidos
        socio.fecha_nacimiento = fecha_nac
        socio.fecha_ingreso    = fecha_ing
        socio.sexo             = sexo
        socio.trabajo          = trabajo
        socio.agencia          = agencia
        socio.situacion        = situacion
        socio.actualizado_por  = current_user.username
        db.session.commit()
        db.session.add(AuditLog(usuario=current_user.username, accion='editar', tipo_objeto='Socio', objeto_id=socio.nro_socio, detalle=f'{socio.apellidos}, {socio.nombres}'))
        db.session.commit()
        flash('Socio actualizado correctamente.', 'success')
        return redirect(url_for('socios.index'))

    return render_template('socios/form.html', socio=socio)


@bp.route('/<int:id>/estado')
@login_required
def estado(id):
    socio = Socio.query.get_or_404(id)
    estado_socio = Estado.query.filter_by(socio_id=socio.id).first()
    if not estado_socio:
        estado_socio = Estado()
        estado_socio.socio_id = socio.id
        estado_socio.mora_cc = 'al_dia'
        estado_socio.mora_sol = 'al_dia'
        estado_socio.mora_ape = 'al_dia'
        estado_socio.mora_credito = 'al_dia'
        estado_socio.mora_cabal = 'al_dia'
        estado_socio.mora_visa = 'al_dia'
        db.session.add(estado_socio)
        db.session.commit()
        
    moras = {
        'Caja de Ahorro / CC': estado_socio.mora_cc,
        'Solidaridad': estado_socio.mora_sol,
        'Aporte': estado_socio.mora_ape,
        'Créditos': estado_socio.mora_credito,
        'Tarjeta Cabal': estado_socio.mora_cabal,
        'Tarjeta Visa': estado_socio.mora_visa
    }
    
    moras_activas = {prod: est for prod, est in moras.items() if est.lower().strip() == 'moroso'}
    habilitado = len(moras_activas) == 0
    
    return render_template('socios/estado.html', socio=socio, estado_socio=estado_socio, moras_activas=moras_activas, habilitado=habilitado)
