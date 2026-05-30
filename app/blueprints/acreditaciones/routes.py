from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Asamblea, PadronAsamblea, Credencial
from app.extensions import db

bp = Blueprint('acreditaciones', __name__, url_prefix='/acreditaciones')

@bp.route('/')
@login_required
def index():
    # Mostrar asambleas recientes para seleccionar su padrón
    asambleas = Asamblea.query.order_by(Asamblea.fecha.desc()).all()
    return render_template('acreditaciones/index.html', asambleas=asambleas)

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
    elif padron_registro.situacion != 'habilitado':
        flash(f'El socio {padron_registro.socio.apellidos_nombres} no figura como habilitado.', 'danger')
    else:
        nueva_credencial = Credencial()
        nueva_credencial.padron_id = padron_id
        nueva_credencial.descripcion = "Acreditación Regular"
        nueva_credencial.creado_por = current_user.username
        nueva_credencial.actualizado_por = current_user.username
        db.session.add(nueva_credencial)
        db.session.commit()
        flash(f'Credencial generada y socio {padron_registro.socio.apellidos_nombres} acreditado.', 'success')
        
    return redirect(url_for('acreditaciones.padron', asamblea_id=padron_registro.asamblea_id))
