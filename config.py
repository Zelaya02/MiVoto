import os
from dotenv import load_dotenv

# Load .env from project root
def load_environment():
    basedir = os.path.abspath(os.path.dirname(__file__))
    env_path = os.path.join(basedir, '..', '.env')
    load_dotenv(env_path, override=False)

load_environment()

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'), override=False)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-default'
    # Usar SQLite local por defecto para desarrollo sin configurar claves complejas de Postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mivoto.db'
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración SMTP para recuperación de contraseña
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_FROM = os.environ.get('MAIL_FROM', MAIL_USERNAME)
