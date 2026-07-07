import os
import sqlalchemy as sa
from app import create_app
from app.extensions import db, bcrypt
from app.models import Rol, Usuario, Socio, Estado, Asamblea, PadronAsamblea

app = create_app()

def seed_db():
    with app.app_context():
        # Crear todas las tablas
        db.create_all()

        # Migración: agregar columnas faltantes en producción
        try:
            inspector = sa.inspect(db.engine)
            cols_roles = [c['name'] for c in inspector.get_columns('roles')]
            if 'permisos' not in cols_roles:
                tipo = 'JSON' if 'postgresql' in str(db.engine.url) else 'TEXT'
                db.session.execute(sa.text(f"ALTER TABLE roles ADD COLUMN permisos {tipo} DEFAULT '[]'"))
                db.session.commit()
                print('Migración: columna permisos agregada a roles')
        except Exception as e:
            db.session.rollback()
            print(f'Migración (roles): {e}')
        try:
            inspector = sa.inspect(db.engine)
            cols_usuarios = [c['name'] for c in inspector.get_columns('usuarios')]
            if 'permisos_extra' not in cols_usuarios:
                tipo = 'JSON' if 'postgresql' in str(db.engine.url) else 'TEXT'
                db.session.execute(sa.text(f"ALTER TABLE usuarios ADD COLUMN permisos_extra {tipo} DEFAULT '[]'"))
                db.session.commit()
                print('Migración: columna permisos_extra agregada a usuarios')
        except Exception as e:
            db.session.rollback()
            print(f'Migración (usuarios): {e}')

        # Asignar permisos por defecto a roles existentes que no tengan
        for r in Rol.query.all():
            if not r.permisos:
                nombre_lower = r.nombre.lower().strip()
                if nombre_lower in ('admin', 'administrador'):
                    r.permisos = ['dashboard', 'socios', 'asambleas', 'estados', 'acreditaciones', 'reportes', 'votacion', 'roles', 'usuarios']
                elif nombre_lower in ('socio', 'operador', 'operador_lectura'):
                    r.permisos = ['dashboard', 'asambleas', 'acreditaciones', 'reportes', 'estados']
                else:
                    r.permisos = ['dashboard']
                print(f'Permisos asignados a rol {r.nombre}: {r.permisos}')
        db.session.commit()
        
        # Verificar si ya hay roles
        if not Rol.query.first():
            print("Creando roles...")
            modulos_todos = ['dashboard', 'socios', 'asambleas', 'estados', 'acreditaciones', 'reportes', 'votacion', 'roles', 'usuarios']
            r_admin = Rol(nombre='Administrador', descripcion='Administrador del sistema', permisos=modulos_todos)
            r_operador = Rol(nombre='Socio', descripcion='Socio de la cooperativa', permisos=['dashboard', 'asambleas', 'acreditaciones', 'reportes', 'estados'])
            db.session.add_all([r_admin, r_operador])
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
            
            print("Creando 15 clientes de ejemplo...")
            nombres = ['Carlos', 'Ana', 'Luis', 'Marta', 'Pedro', 'Laura', 'Diego', 'Sofía', 'Miguel', 'Lucía', 'Jorge', 'Elena', 'Raúl', 'Carmen', 'José']
            apellidos = ['López', 'Martínez', 'García', 'Fernández', 'Rodríguez', 'González', 'Pérez', 'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Díaz', 'Gómez', 'Cruz', 'Ruiz']
            import random
            
            for i in range(15):
                nuevo_socio = Socio(
                    cedula=str(2000000 + i),
                    nro_socio=f'{100 + i:04d}',
                    nombres=nombres[i],
                    apellidos=apellidos[i],
                    trabajo='Varios',
                    agencia='Central',
                    situacion='activo'
                )
                db.session.add(nuevo_socio)
                db.session.flush() # Para obtener el ID del socio
                
                estado = Estado(
                    socio_id=nuevo_socio.id,
                    mora_cc='al_dia' if random.choice([True, False]) else 'moroso',
                    mora_sol='al_dia',
                    mora_ape='al_dia',
                    mora_credito='al_dia',
                    mora_cabal='al_dia',
                    mora_visa='al_dia'
                )
                db.session.add(estado)
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
            db.session.refresh(asamblea)
            
            # Generar padrón automáticamente para la asamblea de prueba
            print("Generando padrón para la asamblea de prueba...")
            socios_activos = Socio.query.filter_by(situacion='activo').all()
            for socio in socios_activos:
                estado_socio = Estado.query.filter_by(socio_id=socio.id).first()
                if estado_socio:
                    moras_activas = [
                        f for f in ['mora_cc', 'mora_sol', 'mora_ape', 'mora_credito', 'mora_cabal', 'mora_visa']
                        if getattr(estado_socio, f, 'al_dia').lower().strip() == 'moroso'
                    ]
                else:
                    moras_activas = []
                situacion = 'habilitado' if len(moras_activas) == 0 else 'inhabilitado'
                motivo = 'Posee mora en ' + ', '.join(moras_activas) if moras_activas else None
                db.session.add(PadronAsamblea(
                    socio_id=socio.id,
                    asamblea_id=asamblea.id,
                    situacion=situacion,
                    motivo_inhabilitacion=motivo
                ))
            db.session.commit()
            print(f"Padrón generado con {len(socios_activos)} socios.")
            
            print("Base de datos inicializada correctamente.")
        else:
            print("La base de datos ya contiene información inicial.")

if __name__ == '__main__':
    seed_db()

