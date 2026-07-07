from app import create_app
from app.extensions import db, bcrypt
from app.models import Usuario, Rol

app = create_app()
with app.app_context():
    r_admin = Rol.query.filter_by(nombre='admin').first()
    if not r_admin:
        print("Admin role not found, creating...")
        r_admin = Rol(nombre='admin', descripcion='Administrador del sistema')
        db.session.add(r_admin)
        db.session.commit()

    u = Usuario.query.filter_by(username='admin').first()
    if u:
        u.password_hash = bcrypt.generate_password_hash('admin').decode('utf-8')
        db.session.commit()
        print("Admin user password updated to 'admin'.")
    else:
        print("Admin user not found, creating...")
        u = Usuario(
            username='admin', 
            email='admin@cooperativa.com',
            password_hash=bcrypt.generate_password_hash('admin').decode('utf-8'), 
            rol_id=r_admin.id, 
            activo=True
        )
        db.session.add(u)
        db.session.commit()
        print("Admin user created with password 'admin'.")
