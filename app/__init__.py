from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager, bcrypt, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    # Registrar blueprints
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.dashboard import bp as dashboard_bp
    from app.blueprints.socios import bp as socios_bp
    from app.blueprints.asambleas import bp as asambleas_bp
    from app.blueprints.votacion import bp as votacion_bp
    from app.blueprints.roles import bp as roles_bp
    from app.blueprints.usuarios import bp as usuarios_bp
    from app.blueprints.estados import bp as estados_bp
    from app.blueprints.acreditaciones import bp as acreditaciones_bp
    from app.blueprints.reportes import bp as reportes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(socios_bp)
    app.register_blueprint(asambleas_bp)
    app.register_blueprint(votacion_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(estados_bp)
    app.register_blueprint(acreditaciones_bp)
    app.register_blueprint(reportes_bp)

    return app
