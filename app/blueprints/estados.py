from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from app.models import Socio, Estado
from app.extensions import db

bp = Blueprint('estados', __name__, url_prefix='/estados')

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    socio = None
    estado_socio = None
    moras_activas = {}
    habilitado = None

    if request.method == 'POST':
        busqueda = request.form.get('busqueda', '').strip()
        if busqueda:
            socio = Socio.query.filter(
                (Socio.cedula == busqueda) |
                (Socio.nro_socio == busqueda) |
                (Socio.cedula.ilike(f'%{busqueda}%'))
            ).first()

            if socio:
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
            else:
                flash('No se encontró ningún socio con ese dato.', 'danger')
        else:
            flash('Por favor ingresa un dato para la búsqueda.', 'warning')

    return render_template('estados/index.html', socio=socio, estado_socio=estado_socio, moras_activas=moras_activas, habilitado=habilitado)
