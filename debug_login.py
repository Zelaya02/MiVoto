from app import create_app
from app.extensions import db, bcrypt
from app.models import Usuario

app = create_app()
with app.app_context():
    users = Usuario.query.all()
    print(f"Total usuarios: {len(users)}")
    for u in users:
        print(f"  username='{u.username}', activo={u.activo}, hash={u.password_hash[:30]}...")
        # Test password 'admin'
        try:
            check = bcrypt.check_password_hash(u.password_hash, 'admin')
            print(f"  -> password 'admin' verifica: {check}")
        except Exception as e:
            print(f"  -> ERROR verificando password: {e}")
