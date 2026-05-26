from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Asamblea, Mocion, OpcionMocion, Voto, Socio
from app.extensions import db

bp = Blueprint('votacion', __name__, url_prefix='/votacion')

@bp.route('/asamblea/<int:id>/mociones')
@login_required
def mociones(id):
    asamblea = Asamblea.query.get_or_404(id)
    return render_template('votacion/mociones.html', asamblea=asamblea)

@bp.route('/mocion/<int:id>/votar', methods=['GET', 'POST'])
@login_required
def votar(id):
    mocion = Mocion.query.get_or_404(id)
    # En un sistema real de asamblea presencial o delegada, el operador ingresa 
    # el voto del socio que tiene en frente. 
    # Asumiremos que el operador busca al socio por cédula para registrar su voto.
    
    if request.method == 'POST':
        cedula = request.form.get('cedula')
        opcion_id = request.form.get('opcion')
        
        socio = Socio.query.filter_by(cedula=cedula).first()
        if not socio:
            flash('Socio no encontrado.', 'danger')
            return redirect(url_for('votacion.votar', id=id))
            
        # Verificar si ya votó
        voto_existente = Voto.query.filter_by(socio_id=socio.id, mocion_id=mocion.id).first()
        if voto_existente:
            flash(f'El socio {socio.nombres} {socio.apellidos} ya emitió su voto para esta moción.', 'warning')
            return redirect(url_for('votacion.votar', id=id))
            
        opcion = OpcionMocion.query.get(opcion_id)
        
        nuevo_voto = Voto(
            socio_id=socio.id,
            mocion_id=mocion.id,
            opcion_elegida=opcion.texto if opcion else 'Abstención'
        )
        db.session.add(nuevo_voto)
        
        try:
            db.session.commit()
            flash('Voto registrado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el voto.', 'danger')
            
        return redirect(url_for('votacion.votar', id=id))
        
    return render_template('votacion/votar.html', mocion=mocion)
