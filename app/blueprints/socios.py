from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Socio
from app.extensions import db

bp = Blueprint('socios', __name__, url_prefix='/socios')

@bp.route('/')
@login_required
def index():
    # Búsqueda sencilla por cédula o apellido
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

@bp.route('/<int:id>/estado')
@login_required
def estado(id):
    socio = Socio.query.get_or_404(id)
    # Lógica para determinar si está habilitado o no basado en moras
    # (Se asume que la regla es no tener moras activas en los últimos 3 meses)
    moras_activas = [m for m in socio.moras if m.estado == 'moroso']
    
    habilitado = len(moras_activas) == 0
    return render_template('socios/estado.html', socio=socio, moras=moras_activas, habilitado=habilitado)
