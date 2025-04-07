import os
from pathlib import Path
from dotenv import load_dotenv


def remove_database():
    print("Starting database reset process...")
    
    # Get the path to .env file
    backend_dir = Path(__file__).parent.parent
    env_path = backend_dir / '.env'
    
    # Load environment variables
    load_dotenv(dotenv_path=env_path)
    
    # Get database connection details from environment variables
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    
    print(f"Resetting database: {DB_NAME} on {DB_HOST}")
    
    try:
        # Command to drop and recreate the database
        drop_create_cmd = f"echo 'DROP DATABASE IF EXISTS {DB_NAME}; CREATE DATABASE {DB_NAME};' | mysql -u{DB_USER} -p{DB_PASSWORD}"
        print(f"Executing: {drop_create_cmd}")
        os.system(drop_create_cmd)
        
        # Run Alembic migrations to recreate tables
        print("Running migrations to recreate tables...")
        migration_cmd = f"cd {backend_dir} && alembic upgrade head"
        print(f"Executing: {migration_cmd}")
        os.system(migration_cmd)
        
        print("Database has been reset successfully.")
        print("To reload data, run: python -m backend.load_all_data")
        
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    remove_database()
