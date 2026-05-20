from flask import Flask
from config import Config
from app.extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)

    # Aquí se registrarán los blueprints más adelante
    # from app.blueprints.dashboard import bp as dashboard_bp
    # app.register_blueprint(dashboard_bp)

    return app
