import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-default'
    # Usar SQLite local por defecto para desarrollo sin configurar claves complejas de Postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mivoto.db'
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    # Si detectamos problemas de contraseña o queremos asegurar portabilidad, fallback a SQLite:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///mivoto.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
