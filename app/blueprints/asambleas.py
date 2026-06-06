from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Asamblea, PadronAsamblea, Socio, Estado
from app.extensions import db
from datetime import date, time

bp = Blueprint('asambleas', __name__, url_prefix='/asambleas')


def _generar_padron(asamblea):
    socios = Socio.query.filter_by(situacion='activo').all()
    nuevos_registros = []

    for socio in socios:
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

        nuevos_registros.append(PadronAsamblea(
            socio_id=socio.id,
            asamblea_id=asamblea.id,
            situacion=situacion,
            motivo_inhabilitacion=motivo
        ))

    db.session.bulk_save_objects(nuevos_registros)
    db.session.commit()
    return len(nuevos_registros)


@bp.route('/')
@login_required
def index():
    asambleas = Asamblea.query.order_by(Asamblea.fecha.desc()).all()
    return render_template('asambleas/index.html', asambleas=asambleas)


@bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if request.method == 'POST':
        tipo = request.form.get('tipo', '').strip()
        fecha_str = request.form.get('fecha', '').strip()
        hora_inicio = request.form.get('hora_inicio', '').strip()
        lugar = request.form.get('lugar', '').strip()
        quorum_minimo = request.form.get('quorum_minimo', '').strip()

        if not tipo or not fecha_str:
            flash('El tipo y la fecha son obligatorios.', 'danger')
            return render_template('asambleas/nueva.html')

        try:
            partes = fecha_str.split('-')
            fecha = date(int(partes[0]), int(partes[1]), int(partes[2]))
        except (ValueError, IndexError):
            flash('Fecha inválida.', 'danger')
            return render_template('asambleas/nueva.html')

        hora = None
        if hora_inicio:
            try:
                partes_h = hora_inicio.split(':')
                hora = time(int(partes_h[0]), int(partes_h[1]))
            except (ValueError, IndexError):
                flash('Hora inválida.', 'danger')
                return render_template('asambleas/nueva.html')

        asamblea = Asamblea(
            tipo=tipo,
            fecha=fecha,
            hora_inicio=hora,
            lugar=lugar or None,
            quorum_minimo=int(quorum_minimo) if quorum_minimo.isdigit() else None,
            estado='programada'
        )
        db.session.add(asamblea)
        db.session.commit()
        db.session.refresh(asamblea)

        total = _generar_padron(asamblea)
        flash(f'Asamblea creada y padrón generado para {total} socios.', 'success')
        return redirect(url_for('asambleas.index'))

    return render_template('asambleas/nueva.html')


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
    PadronAsamblea.query.filter_by(asamblea_id=id).delete()
    db.session.commit()

    total = _generar_padron(asamblea)
    flash(f'Padrón regenerado exitosamente para {total} socios.', 'success')
    return redirect(url_for('asambleas.padron', id=asamblea.id))

