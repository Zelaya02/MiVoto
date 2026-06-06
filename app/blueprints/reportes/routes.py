from flask import render_template
from flask_login import login_required
from app.blueprints.reportes import bp
from app.models import Socio, Asamblea, PadronAsamblea, Credencial, Mocion, Voto, LoginLog
from app.extensions import db
from sqlalchemy import func
from datetime import datetime, timezone


@bp.route('/')
@login_required
def index():
    # ── KPIs generales ──────────────────────────────────────────
    total_socios = Socio.query.count()
    socios_activos = Socio.query.filter_by(situacion='activo').count()
    total_asambleas = Asamblea.query.count()
    total_credenciales = Credencial.query.count()
    total_mociones = Mocion.query.count()
    total_votos = Voto.query.count()

    # ── Asambleas con stats de padrón/acreditación ───────────────
    asambleas = Asamblea.query.order_by(Asamblea.fecha.desc()).all()
    asambleas_stats = []
    for a in asambleas:
        padron = PadronAsamblea.query.filter_by(asamblea_id=a.id).all()
        total_padron = len(padron)
        habilitados = sum(1 for p in padron if p.situacion == 'habilitado')
        inhabilitados = total_padron - habilitados

        creds = (Credencial.query
                 .join(PadronAsamblea)
                 .filter(PadronAsamblea.asamblea_id == a.id)
                 .count())

        pct_habilitados = round((habilitados / total_padron * 100) if total_padron > 0 else 0)
        pct_acreditados = round((creds / habilitados * 100) if habilitados > 0 else 0)

        asambleas_stats.append({
            'asamblea': a,
            'total_padron': total_padron,
            'habilitados': habilitados,
            'inhabilitados': inhabilitados,
            'acreditados': creds,
            'pendientes': habilitados - creds,
            'pct_habilitados': pct_habilitados,
            'pct_acreditados': pct_acreditados,
        })

    # ── Distribución de socios por situación ─────────────────────
    situaciones_q = (db.session.query(Socio.situacion, func.count(Socio.id))
                     .group_by(Socio.situacion).all())
    situaciones = [{'nombre': s, 'total': c} for s, c in situaciones_q]

    # ── Distribución de socios por agencia ───────────────────────
    agencias_q = (db.session.query(
                      func.coalesce(Socio.agencia, 'Sin agencia'),
                      func.count(Socio.id))
                  .group_by(func.coalesce(Socio.agencia, 'Sin agencia'))
                  .order_by(func.count(Socio.id).desc())
                  .all())
    agencias = [{'nombre': a, 'total': c} for a, c in agencias_q]

    # ── Distribución de socios por sexo ──────────────────────────
    sexo_q = (db.session.query(
                  func.coalesce(Socio.sexo, 'No especificado'),
                  func.count(Socio.id))
              .group_by(func.coalesce(Socio.sexo, 'No especificado'))
              .all())
    sexos = [{'nombre': s, 'total': c} for s, c in sexo_q]

    return render_template(
        'reportes/index.html',
        title='Reportes',
        total_socios=total_socios,
        socios_activos=socios_activos,
        total_asambleas=total_asambleas,
        total_credenciales=total_credenciales,
        total_mociones=total_mociones,
        total_votos=total_votos,
        asambleas_stats=asambleas_stats,
        situaciones=situaciones,
        agencias=agencias,
        sexos=sexos,
    )


@bp.route('/logs')
@login_required
def logs():
    logs_list = LoginLog.query.order_by(LoginLog.login_at.desc()).limit(200).all()
    return render_template('reportes/logs.html', logs=logs_list)
