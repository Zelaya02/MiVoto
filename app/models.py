from datetime import datetime, timezone
from flask_login import UserMixin
from app.extensions import db

class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    password_venc = db.Column(db.DateTime(timezone=True))
    nombre_completo = db.Column(db.String(150))
    activo = db.Column(db.Boolean, default=True)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Socio(db.Model):
    __tablename__ = 'socios'
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nro_socio = db.Column(db.String(20), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    fecha_ingreso = db.Column(db.Date)
    sexo = db.Column(db.String(15))
    trabajo = db.Column(db.String(100))
    agencia = db.Column(db.String(100))
    situacion = db.Column(db.String(50), default='activo')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    moras = db.relationship('Mora', backref='socio', lazy=True, cascade='all, delete-orphan')
    padrones = db.relationship('PadronAsamblea', backref='socio', lazy=True, cascade='all, delete-orphan')
    votos = db.relationship('Voto', backref='socio', lazy=True, cascade='all, delete-orphan')

class Mora(db.Model):
    __tablename__ = 'moras'
    __table_args__ = (db.UniqueConstraint('socio_id', 'producto', 'fecha_consulta', name='uq_mora_socio_producto_fecha'),)
    id = db.Column(db.Integer, primary_key=True)
    socio_id = db.Column(db.Integer, db.ForeignKey('socios.id', ondelete='CASCADE'), nullable=False)
    producto = db.Column(db.String(30), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    fecha_consulta = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Asamblea(db.Model):
    __tablename__ = 'asambleas'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(30), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time)
    lugar = db.Column(db.String(200))
    quorum_minimo = db.Column(db.Integer)
    estado = db.Column(db.String(30), default='programada')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    padrones = db.relationship('PadronAsamblea', backref='asamblea', lazy=True, cascade='all, delete-orphan')
    mociones = db.relationship('Mocion', backref='asamblea', lazy=True, cascade='all, delete-orphan')

class PadronAsamblea(db.Model):
    __tablename__ = 'padron_asamblea'
    __table_args__ = (db.UniqueConstraint('socio_id', 'asamblea_id', name='uq_padron_socio_asamblea'),)
    id = db.Column(db.Integer, primary_key=True)
    socio_id = db.Column(db.Integer, db.ForeignKey('socios.id', ondelete='CASCADE'), nullable=False)
    asamblea_id = db.Column(db.Integer, db.ForeignKey('asambleas.id', ondelete='CASCADE'), nullable=False)
    situacion = db.Column(db.String(30), nullable=False, default='pendiente')
    motivo_inhabilitacion = db.Column(db.String(200))
    fecha_acreditacion = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    credenciales = db.relationship('Credencial', backref='padron', lazy=True, cascade='all, delete-orphan')

class Credencial(db.Model):
    __tablename__ = 'credenciales'
    id = db.Column(db.Integer, primary_key=True)
    padron_id = db.Column(db.Integer, db.ForeignKey('padron_asamblea.id', ondelete='CASCADE'), nullable=False)
    descripcion = db.Column(db.String(200))
    reimpresion = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Mocion(db.Model):
    __tablename__ = 'mociones'
    id = db.Column(db.Integer, primary_key=True)
    asamblea_id = db.Column(db.Integer, db.ForeignKey('asambleas.id', ondelete='CASCADE'), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    tipo_votacion = db.Column(db.String(20), default='si_no')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    opciones = db.relationship('OpcionMocion', backref='mocion', lazy=True, cascade='all, delete-orphan')
    votos = db.relationship('Voto', backref='mocion', lazy=True, cascade='all, delete-orphan')

class OpcionMocion(db.Model):
    __tablename__ = 'opciones_mocion'
    id = db.Column(db.Integer, primary_key=True)
    mocion_id = db.Column(db.Integer, db.ForeignKey('mociones.id', ondelete='CASCADE'), nullable=False)
    texto = db.Column(db.String(200), nullable=False)

class Voto(db.Model):
    __tablename__ = 'votos'
    __table_args__ = (db.UniqueConstraint('socio_id', 'mocion_id', name='uq_voto_socio_mocion'),)
    id = db.Column(db.Integer, primary_key=True)
    socio_id = db.Column(db.Integer, db.ForeignKey('socios.id', ondelete='CASCADE'), nullable=False)
    mocion_id = db.Column(db.Integer, db.ForeignKey('mociones.id', ondelete='CASCADE'), nullable=False)
    opcion_elegida = db.Column(db.String(100))
    timestamp_voto = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
