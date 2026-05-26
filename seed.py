import os
from app import create_app
from app.extensions import db, bcrypt
from app.models import Rol, Usuario, Socio, Estado, Asamblea

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
                password_hash=bcrypt.generate_password_hash('admin').decode('utf-8'),
                nombre_completo='Administrador Principal',
                rol_id=r_admin.id
            )
            db.session.add(admin_user)
            db.session.commit()
            
            print("Creando socio habilitado...")
            socio_ok = Socio(
                cedula='1234567',
                nro_socio='0001',
                nombres='Juan',
                apellidos='Pérez',
                trabajo='Municipalidad',
                agencia='Central',
                situacion='activo'
            )
            db.session.add(socio_ok)
            db.session.commit()
            
            estado_ok = Estado(
                socio_id=socio_ok.id,
                mora_cc='al_dia',
                mora_sol='al_dia',
                mora_ape='al_dia',
                mora_credito='al_dia',
                mora_cabal='al_dia',
                mora_visa='al_dia'
            )
            db.session.add(estado_ok)
            db.session.commit()

            print("Creando socio moroso...")
            socio_mora = Socio(
                cedula='7654321',
                nro_socio='0002',
                nombres='María',
                apellidos='Gómez',
                trabajo='Hospital Regional',
                agencia='Sucursal Norte',
                situacion='activo'
            )
            db.session.add(socio_mora)
            db.session.commit()
            
            estado_mora = Estado(
                socio_id=socio_mora.id,
                mora_cc='al_dia',
                mora_sol='moroso',
                mora_ape='al_dia',
                mora_credito='moroso',
                mora_cabal='al_dia',
                mora_visa='al_dia'
            )
            db.session.add(estado_mora)
            db.session.commit()
            
            print("Creando asamblea de prueba...")
            asamblea = Asamblea(
                tipo='ordinaria',
                fecha=db.func.current_date(),
                lugar='Salón Municipal de Zelaya',
                quorum_minimo=50,
                estado='programada'
            )
            db.session.add(asamblea)
            db.session.commit()
            
            print("Base de datos inicializada correctamente.")
        else:
            print("La base de datos ya contiene información inicial.")

if __name__ == '__main__':
    seed_db()

