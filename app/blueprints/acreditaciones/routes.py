from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Socio, Estado, Asamblea, PadronAsamblea, Credencial
from app.extensions import db

bp = Blueprint('acreditaciones', __name__, url_prefix='/acreditaciones')

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    socio = None
    estado_socio = None
    moras_activas = {}
    habilitado = None
    padron_registro = None
    ya_acreditado = False
    asamblea = Asamblea.query.order_by(Asamblea.fecha.desc()).first()

    if request.method == 'POST':
        busqueda = request.form.get('busqueda', '').strip()
        if busqueda:
            socio = Socio.query.filter((Socio.cedula == busqueda) | (Socio.nro_socio == busqueda)).first()
            if socio and asamblea:
                padron_registro = PadronAsamblea.query.filter_by(asamblea_id=asamblea.id, socio_id=socio.id).first()
                if not padron_registro:
                    flash(f'El socio {socio.apellidos_nombres} no se encuentra en el padrón de la asamblea actual.', 'warning')
                    socio = None
                else:
                    ya_acreditado = Credencial.query.filter_by(padron_id=padron_registro.id).first() is not None
                    estado_socio = Estado.query.filter_by(socio_id=socio.id).first()
                    if not estado_socio:
                        estado_socio = Estado(
                            socio_id=socio.id,
                            mora_cc='al_dia', mora_sol='al_dia',
                            mora_ape='al_dia', mora_credito='al_dia',
                            mora_cabal='al_dia', mora_visa='al_dia'
                        )
                        db.session.add(estado_socio)
                        db.session.commit()
                        db.session.refresh(estado_socio)
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
            elif not socio:
                flash('No se encontró ningún socio con esa cédula o número.', 'danger')
        else:
            flash('Por favor ingresa un dato para la búsqueda.', 'warning')

    asambleas = Asamblea.query.order_by(Asamblea.fecha.desc()).all()

    return render_template('acreditaciones/index.html',
                           asambleas=asambleas,
                           asamblea_actual=asamblea,
                           socio=socio,
                           estado_socio=estado_socio,
                           moras_activas=moras_activas,
                           habilitado=habilitado,
                           padron_registro=padron_registro,
                           ya_acreditado=ya_acreditado)

@bp.route('/<int:asamblea_id>/padron')
@login_required
def padron(asamblea_id):
    asamblea = Asamblea.query.get_or_404(asamblea_id)
    padron_asamblea = PadronAsamblea.query.filter_by(asamblea_id=asamblea_id).all()
    
    # Calcular contadores
    total = len(padron_asamblea)
    habilitados = sum(1 for p in padron_asamblea if p.situacion == 'habilitado')
    inhabilitados = total - habilitados
    
    # Obtener IDs de quienes ya tienen credencial para esta asamblea (acreditados)
    credenciales = Credencial.query.join(PadronAsamblea).filter(PadronAsamblea.asamblea_id == asamblea_id).all()
    acreditados_ids = {c.padron_id for c in credenciales}
    acreditados = len(acreditados_ids)
    
    return render_template('acreditaciones/padron.html', asamblea=asamblea, padron=padron_asamblea,
                           acreditados_ids=acreditados_ids,
                           stats={'total': total, 'habilitados': habilitados, 'inhabilitados': inhabilitados, 'acreditados': acreditados})

@bp.route('/acreditar/<int:padron_id>', methods=['POST'])
@login_required
def acreditar(padron_id):
    padron_registro = PadronAsamblea.query.get_or_404(padron_id)
    
    # Verificar si ya tiene credencial
    credencial = Credencial.query.filter_by(padron_id=padron_id).first()
    
    if credencial:
        flash(f'El socio {padron_registro.socio.apellidos_nombres} ya está acreditado.', 'warning')
    elif padron_registro.situacion != 'habilitado' and padron_registro.situacion != 'inhabilitado': 
        # Permitimos acreditar incluso si es inhabilitado (solo voz), pero verificamos consistencia
        flash(f'Estado de padrón no reconocido.', 'danger')
    else:
        nueva_credencial = Credencial()
        nueva_credencial.padron_id = padron_id
        nueva_credencial.descripcion = "Acreditación Regular"
        nueva_credencial.creado_por = current_user.username
        nueva_credencial.actualizado_por = current_user.username
        db.session.add(nueva_credencial)
        db.session.commit()
        flash(f'Credencial generada y socio {padron_registro.socio.apellidos_nombres} acreditado.', 'success')
        
    return redirect(request.referrer or url_for('acreditaciones.index'))


@bp.route('/tarjeta/<int:padron_id>')
@login_required
def tarjeta(padron_id):
    padron_registro = PadronAsamblea.query.get_or_404(padron_id)
    credencial = Credencial.query.filter_by(padron_id=padron_id).first_or_404()
    asamblea = padron_registro.asamblea
    socio = padron_registro.socio

    # Lógica de Voz y Voto
    # Si cumple todo (habilitado) es Voz y Voto, si no (inhabilitado) es solo Voz
    tiene_derecho = "VOZ Y VOTO" if padron_registro.situacion == 'habilitado' else "VOZ"

    # Determinar texto de asamblea para el subtítulo
    tipo = (asamblea.tipo or 'ORDINARIA').upper()
    anio = asamblea.fecha.year if asamblea.fecha else ''
    subtitulo = f"ASAMBLEA {tipo} - {anio}"

    return render_template(
        'acreditaciones/tarjeta.html',
        socio=socio,
        asamblea=asamblea,
        credencial=credencial,
        subtitulo=subtitulo,
        tiene_derecho=tiene_derecho,
        autorizado_por=credencial.creado_por or current_user.username,
    )


