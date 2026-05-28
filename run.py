from app import create_app
import os
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *args, **kwargs: None

try:
    from sqlalchemy import create_engine
    from sqlalchemy.exc import OperationalError
except ImportError:
    create_engine = None
    OperationalError = Exception

# Load environment variables (.env)
load_dotenv(override=True)
# Ensure the DATABASE_URL points to the correct port (5000)
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL')



def test_connection():
    """Attempt to connect to the DB using the URL defined in .env.
    Returns True if the connection succeeds, otherwise prints the error and returns False.
    """
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('DATABASE_URL no está definido en .env')
        return False
    try:
        engine = create_engine(db_url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            print('Conexión a la base de datos exitosa')
        return True
    except OperationalError as err:
        print(f'Error al conectar a la base de datos: {err}')
        return False

print('Verificando conexión a la base de datos...')
test_connection()

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)

