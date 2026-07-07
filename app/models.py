from datetime import datetime, timezone
from flask_login import UserMixin
from app.extensions import db

MODULOS = [
    'dashboard', 'socios', 'asambleas', 'estados',
    'acreditaciones', 'reportes', 'votacion'
]

class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    permisos = db.Column(db.JSON, default=list)
    row_version = db.Column(db.Integer, default=1)
    creado_por = db.Column(db.String(100), default='sistema')
    creado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_por = db.Column(db.String(100), default='sistema')
    actualizado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def tiene_permiso(self, modulo):
        return self.nombre.lower().strip() in ('admin', 'administrador') or modulo in (self.permisos or [])

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
    permisos_extra = db.Column(db.JSON, default=list)
    row_version = db.Column(db.Integer, default=1)
    creado_por = db.Column(db.String(100), default='sistema')
    creado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_por = db.Column(db.String(100), default='sistema')
    actualizado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def tiene_permiso(self, modulo):
        if self.rol:
            if self.rol.nombre.lower().strip() in ('admin', 'administrador'):
                return True
            if self.rol.tiene_permiso(modulo):
                return True
        return modulo in (self.permisos_extra or [])

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
    row_version = db.Column(db.Integer, default=1)
    creado_por = db.Column(db.String(100), default='sistema')
    creado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_por = db.Column(db.String(100), default='sistema')
    actualizado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    estados = db.relationship('Estado', backref='socio', lazy=True, cascade='all, delete-orphan')
    moras = db.relationship('Mora', backref='socio', lazy=True, cascade='all, delete-orphan')
    padrones = db.relationship('PadronAsamblea', backref='socio', lazy=True, cascade='all, delete-orphan')
    votos = db.relationship('Voto', backref='socio', lazy=True, cascade='all, delete-orphan')

    @property
    def apellidos_nombres(self):
        return f"{self.apellidos}, {self.nombres}"

class Estado(db.Model):
    __tablename__ = 'estados'
    id = db.Column(db.Integer, primary_key=True)
    socio_id = db.Column(db.Integer, db.ForeignKey('socios.id', ondelete='CASCADE'), nullable=False)
    mora_cc = db.Column(db.String(20), nullable=False, default='al_dia')
    mora_sol = db.Column(db.String(20), nullable=False, default='al_dia')
    mora_ape = db.Column(db.String(20), nullable=False, default='al_dia')
    mora_credito = db.Column(db.String(20), nullable=False, default='al_dia')
    mora_cabal = db.Column(db.String(20), nullable=False, default='al_dia')
    mora_visa = db.Column(db.String(20), nullable=False, default='al_dia')
    row_version = db.Column(db.Integer, default=1)
    creado_por = db.Column(db.String(100), default='sistema')
    creado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_por = db.Column(db.String(100), default='sistema')
    actualizado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

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
    row_version = db.Column(db.Integer, default=1)
    creado_por = db.Column(db.String(100), default='sistema')
    creado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_por = db.Column(db.String(100), default='sistema')
    actualizado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    credenciales = db.relationship('Credencial', backref='padron', lazy=True, cascade='all, delete-orphan')

class Credencial(db.Model):
    __tablename__ = 'credenciales'
    id = db.Column(db.Integer, primary_key=True)
    padron_id = db.Column(db.Integer, db.ForeignKey('padron_asamblea.id', ondelete='CASCADE'), nullable=False)
    descripcion = db.Column(db.String(200))
    reimpresion = db.Column(db.String(10), default='NO')
    row_version = db.Column(db.Integer, default=1)
    creado_por = db.Column(db.String(100), default='sistema')
    creado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_por = db.Column(db.String(100), default='sistema')
    actualizado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

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

class LoginLog(db.Model):
    __tablename__ = 'login_logs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    nombre_completo = db.Column(db.String(150))
    ip_address = db.Column(db.String(45))
    login_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.String(20), nullable=False)
    tipo_objeto = db.Column(db.String(30), nullable=False)
    objeto_id = db.Column(db.String(20))
    detalle = db.Column(db.Text)
    creado_el = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

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
