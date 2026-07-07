import os
from app import create_app
from app.extensions import db
from seed import seed_db
from seed_socios import seed_socios

app = create_app()

def reset_database():
    with app.app_context():
        print("ATTENTION: This will delete all data and recreate the database.")
        print("Connecting to database...")
        
        # Drop all tables
        print("Dropping all existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating all tables from models...")
        db.create_all()
        
        # Seed default roles, admin user, and initial test data
        print("Seeding database (Roles, Admin User, Assemblies)...")
        seed_db()
        
        # Seed socios
        print("Seeding database (Socios and Estados)...")
        seed_socios()
        
        print("Database successfully reset and seeded!")

if __name__ == '__main__':
    reset_database()
