from app import create_app
from app.extensions import db, bcrypt
from app.models import Usuario

app = create_app()
with app.app_context():
    user = Usuario.query.filter_by(username='admin').first()
    if user:
        user.password_hash = bcrypt.generate_password_hash('admin').decode('utf-8')
        user.activo = True
        db.session.commit()
        print(f"Password actualizado para '{user.username}' -> 'admin'")
    else:
        print("No existe usuario 'admin'. Creando...")
        from app.models import Rol
        rol = Rol.query.filter_by(nombre='admin').first()
        if not rol:
            rol = Rol(nombre='admin', descripcion='Administrador del sistema')
            db.session.add(rol)
            db.session.commit()
        admin = Usuario(
            username='admin',
            email='admin@cooperativa.com',
            password_hash=bcrypt.generate_password_hash('admin').decode('utf-8'),
            nombre_completo='Administrador Principal',
            activo=True,
            rol_id=rol.id
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuario 'admin' creado con password 'admin'")
