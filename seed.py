import os
from app import create_app
from app.extensions import db, bcrypt
from app.models import Rol, Usuario, Socio, Mora, Asamblea

app = create_app()

def seed_db():
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Verificar si ya hay roles
        if not Rol.query.first():
            print("Creando roles...")
            r_admin = Rol(nombre='admin', descripcion='Administrador del sistema')
            r_operador = Rol(nombre='operador', descripcion='Operador de asamblea')
            r_consulta = Rol(nombre='consulta', descripcion='Solo lectura')
            db.session.add_all([r_admin, r_operador, r_consulta])
            db.session.commit()
            
            print("Creando usuario administrador...")
            admin_user = Usuario(
                username='admin',
                email='admin@cooperativa.com',
                password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                nombre_completo='Administrador Principal',
                rol_id=r_admin.id
            )
            db.session.add(admin_user)
            db.session.commit()
            
            print("Creando socio de prueba...")
            socio = Socio(
                cedula='1234567',
                nro_socio='0001',
                nombres='Juan',
                apellidos='Pérez',
                situacion='activo'
            )
            db.session.add(socio)
            db.session.commit()
            
            print("Base de datos inicializada correctamente.")
        else:
            print("La base de datos ya contiene información inicial.")

if __name__ == '__main__':
    seed_db()
