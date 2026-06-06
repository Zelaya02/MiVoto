from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Asamblea, PadronAsamblea, Socio, Estado
from app.extensions import db

bp = Blueprint('asambleas', __name__, url_prefix='/asambleas')

@bp.route('/')
@login_required
def index():
    asambleas = Asamblea.query.order_by(Asamblea.fecha.desc()).all()
    return render_template('asambleas/index.html', asambleas=asambleas)

@bp.route('/<int:id>/padron')
@login_required
def padron(id):
    asamblea = Asamblea.query.get_or_404(id)
    padron = PadronAsamblea.query.filter_by(asamblea_id=id).all()
    
    return render_template('asambleas/padron.html', asamblea=asamblea, padron=padron)

@bp.route('/<int:id>/generar_padron', methods=['POST'])
@login_required
def generar_padron(id):
    asamblea = Asamblea.query.get_or_404(id)
    
    # Limpiar padrón actual
    PadronAsamblea.query.filter_by(asamblea_id=id).delete()
    
    socios = Socio.query.filter_by(situacion='activo').all()
    nuevos_registros = []
    
    for socio in socios:
        estado_socio = Estado.query.filter_by(socio_id=socio.id).first()
        if not estado_socio:
            estado_socio = Estado(
                socio_id=socio.id,
                mora_cc='al_dia',
                mora_sol='al_dia',
                mora_ape='al_dia',
                mora_credito='al_dia',
                mora_cabal='al_dia',
                mora_visa='al_dia'
            )
            db.session.add(estado_socio)
            db.session.commit()
            
        moras = {
            'CC': estado_socio.mora_cc,
            'SOL': estado_socio.mora_sol,
            'APE': estado_socio.mora_ape,
            'CREDITO': estado_socio.mora_credito,
            'CABAL': estado_socio.mora_cabal,
            'VISA': estado_socio.mora_visa
        }
        
        moras_activas = [prod for prod, est in moras.items() if est.lower().strip() == 'moroso']
        
        situacion = 'habilitado' if len(moras_activas) == 0 else 'inhabilitado'
        motivo = 'Posee mora en ' + ', '.join(moras_activas) if moras_activas else None
        
        nuevo_padron = PadronAsamblea(
            socio_id=socio.id,
            asamblea_id=asamblea.id,
            situacion=situacion,
            motivo_inhabilitacion=motivo
        )
        nuevos_registros.append(nuevo_padron)
        
    db.session.bulk_save_objects(nuevos_registros)
    db.session.commit()
    
    flash(f'Padrón generado exitosamente para {len(nuevos_registros)} socios.', 'success')
    return redirect(url_for('asambleas.padron', id=asamblea.id))

