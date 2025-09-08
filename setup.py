"""
Setup script for Cameroon Construction Project Management System
This script initializes the database, creates default data, and sets up the system
"""

import sqlite3
import hashlib
import uuid
import datetime
from pathlib import Path
import os


def create_database():
    """Create and initialize the database"""

    # Create database connection
    db_path = "cameroon_construction.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")

    print("Creating database tables...")

    # Read and execute database schema
    schema_file = Path("database_setup.sql")
    if schema_file.exists():
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)
    else:
        print("Warning: database_setup.sql not found. Creating basic tables...")
        create_basic_tables(cursor)

    # Create default admin user
    create_default_admin(cursor)

    # Insert construction materials data
    insert_construction_materials(cursor)

    # Create sample data for testing
    create_sample_data(cursor)

    conn.commit()
    conn.close()

    print(f"Database created successfully: {db_path}")


def create_basic_tables(cursor):
    """Create basic tables if schema file is not available"""

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone TEXT,
        created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME,
        is_active BOOLEAN DEFAULT 1,
        first_login BOOLEAN DEFAULT 1,
        failed_login_attempts INTEGER DEFAULT 0,
        created_by TEXT,
        digital_signature TEXT
    )''')

    # Construction materials table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS construction_materials (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit TEXT NOT NULL,
        description TEXT,
        standard_price REAL DEFAULT 0,
        created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )''')

    # Stores table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stores (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        owner_id TEXT NOT NULL,
        manager_id TEXT,
        address TEXT,
        phone TEXT,
        created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (owner_id) REFERENCES users(id),
        FOREIGN KEY (manager_id) REFERENCES users(id)
    )''')

    # Store inventory table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS store_inventory (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        material_id TEXT NOT NULL,
        quantity REAL DEFAULT 0,
        price REAL DEFAULT 0,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (material_id) REFERENCES construction_materials(id)
    )''')

    # Transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        from_store_id TEXT,
        to_store_id TEXT,
        customer_id TEXT,
        material_id TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL DEFAULT 0,
        total_amount REAL DEFAULT 0,
        transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        created_by TEXT NOT NULL,
        digital_signature TEXT,
        FOREIGN KEY (from_store_id) REFERENCES stores(id),
        FOREIGN KEY (to_store_id) REFERENCES stores(id),
        FOREIGN KEY (material_id) REFERENCES construction_materials(id),
        FOREIGN KEY (created_by) REFERENCES users(id)
    )''')

    # Jobs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        employer_id TEXT NOT NULL,
        location TEXT,
        salary REAL,
        job_type TEXT,
        requirements TEXT,
        status TEXT DEFAULT 'open',
        posted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        deadline DATE,
        FOREIGN KEY (employer_id) REFERENCES users(id)
    )''')

    # Job applications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_applications (
        id TEXT PRIMARY KEY,
        job_id TEXT NOT NULL,
        applicant_id TEXT NOT NULL,
        application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        cover_letter TEXT,
        resume_path TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs(id),
        FOREIGN KEY (applicant_id) REFERENCES users(id)
    )''')


def create_default_admin(cursor):
    """Create default administrator account"""

    # Check if admin already exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'administrator'")
    if cursor.fetchone()[0] > 0:
        print("Admin user already exists")
        return

    admin_id = str(uuid.uuid4())
    password_hash = hashlib.sha256("admin123".encode()).hexdigest()

    cursor.execute('''
    INSERT INTO users (id, username, password_hash, role, first_name, last_name, 
                      email, created_date, is_active, first_login)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
    ''', (admin_id, "admin", password_hash, "administrator", "System", "Administrator", 
          "admin@construction-cm.com", datetime.datetime.now()))

    print("Default admin user created:")
    print("Username: admin")
    print("Password: admin123")
    print("Please change the password after first login!")


def insert_construction_materials(cursor):
    """Insert Cameroon construction materials"""

    # Check if materials already exist
    cursor.execute("SELECT COUNT(*) FROM construction_materials")
    if cursor.fetchone()[0] > 0:
        print("Construction materials already exist")
        return

    print("Inserting construction materials...")

    # Cameroon construction materials with local prices (in FCFA)
    materials = [
        # Cement and Concrete
        ("Ciment Portland 50kg", "Cement", "Bag", "Ciment Portland standard pour construction", 4000),
        ("Bloc béton 20cm", "Blocks", "Piece", "Bloc béton standard pour murs", 300),
        ("Bloc béton 15cm", "Blocks", "Piece", "Bloc béton pour cloisons", 250),
        ("Béton prêt", "Concrete", "m³", "Béton prémélangé pour fondations", 85000),

        # Steel and Metal
        ("Fer à béton 8mm", "Steel", "Rod", "Barre d'armature en acier 6m", 3500),
        ("Fer à béton 10mm", "Steel", "Rod", "Barre d'armature en acier 6m", 5000),
        ("Fer à béton 12mm", "Steel", "Rod", "Barre d'armature en acier 6m", 7200),
        ("Treillis soudé", "Steel", "Roll", "Treillis soudé pour armature", 25000),
        ("Tôle ondulée", "Roofing", "Sheet", "Tôle galvanisée ondulée", 8500),

        # Timber and Wood
        ("Planche Acajou 2x4", "Timber", "Piece", "Planche d'acajou travaillée 3m", 12000),
        ("Planche Iroko 2x6", "Timber", "Piece", "Planche d'iroko travaillée 3m", 18000),
        ("Contreplaqué 18mm", "Wood Products", "Sheet", "Contreplaqué marine", 15000),
        ("Encadrement porte", "Timber", "Set", "Encadrement complet pour porte", 25000),

        # Roofing Materials
        ("Tuiles d'argile", "Roofing", "Piece", "Tuiles traditionnelles en argile", 500),
        ("Tôle aluminium", "Roofing", "Sheet", "Tôle ondulée en aluminium", 12000),
        ("Charpente bois", "Timber", "Piece", "Bois de charpente prédécoupé", 35000),

        # Bricks and Blocks
        ("Brique rouge", "Blocks", "Piece", "Brique d'argile cuite", 150),
        ("Brique de sable", "Blocks", "Piece", "Brique de sable compressé", 200),
        ("Parpaing creux 20cm", "Blocks", "Piece", "Parpaing creux béton", 400),

        # Sand and Aggregates
        ("Sable de rivière", "Aggregates", "m³", "Sable fin pour construction", 15000),
        ("Sable gros", "Aggregates", "m³", "Sable grossier pour béton", 18000),
        ("Gravier 20mm", "Aggregates", "m³", "Granulats concassés", 20000),
        ("Gravillons", "Aggregates", "m³", "Éclats de granite", 22000),

        # Electrical Materials
        ("Câble électrique 2.5mm", "Electrical", "Meter", "Câble cuivre électrique", 800),
        ("Gaine PVC 20mm", "Electrical", "Meter", "Conduit PVC électrique", 300),
        ("Prise interrupteur", "Electrical", "Piece", "Prise murale standard", 2500),
        ("Disjoncteur", "Electrical", "Piece", "Disjoncteur électrique", 8000),

        # Plumbing Materials
        ("Tube PVC 4 pouces", "Plumbing", "Meter", "Tube PVC évacuation", 2500),
        ("Tube PVC 2 pouces", "Plumbing", "Meter", "Tube PVC alimentation", 1500),
        ("Réservoir 1000L", "Plumbing", "Piece", "Citerne plastique", 85000),
        ("Cuvette WC", "Plumbing", "Piece", "Cuvette WC céramique", 45000),

        # Finishing Materials
        ("Peinture murale", "Finishing", "Liter", "Peinture intérieur/extérieur", 3500),
        ("Carrelage 30x30", "Finishing", "m²", "Carrelage sol et mur", 8500),
        ("Marbre", "Finishing", "m²", "Carrelage marbre naturel", 25000),
        ("Placo plafond", "Finishing", "Sheet", "Dalle plafond gypse", 3500),

        # Doors and Windows
        ("Porte bois", "Doors", "Piece", "Porte intérieure bois", 75000),
        ("Fenêtre aluminium", "Windows", "m²", "Fenêtre cadre aluminium", 35000),
        ("Porte blindée", "Doors", "Piece", "Porte sécurité métallique", 150000),

        # Tools and Equipment
        ("Brouette", "Tools", "Piece", "Brouette construction", 45000),
        ("Pelle", "Tools", "Piece", "Pelle construction", 8000),
        ("Marteau", "Tools", "Piece", "Marteau à panne fendue", 5000),
        ("Mètre ruban", "Tools", "Piece", "Mètre ruban 30m", 12000),

        # Additional Cameroon-specific materials
        ("Bambou", "Timber", "Piece", "Bambou pour échafaudage", 2000),
        ("Pierre latérite", "Aggregates", "m³", "Pierre latérite locale", 12000),
        ("Raphia", "Roofing", "Bundle", "Feuilles de raphia traditionnelles", 5000),
        ("Argile locale", "Blocks", "m³", "Argile pour briques traditionnelles", 8000)
    ]

    for name, category, unit, description, price in materials:
        material_id = str(uuid.uuid4())
        cursor.execute('''
        INSERT INTO construction_materials (id, name, category, unit, description, 
                                          standard_price, created_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (material_id, name, category, unit, description, price, datetime.datetime.now()))

    print(f"Inserted {len(materials)} construction materials")


def create_sample_data(cursor):
    """Create sample data for testing"""

    print("Creating sample users...")

    # Create sample users
    sample_users = [
        ("retailer1", "retail123", "retail_store", "Jean", "Mballa", "jean.mballa@email.com", "237677123456"),
        ("contractor1", "contract123", "contractor", "Marie", "Nguesso", "marie.nguesso@email.com", "237699987654"),
        ("owner1", "owner123", "contract_owner", "Paul", "Biya", "paul.biya@email.com", "237655444333"),
        ("manager1", "manager123", "manager", "Alice", "Foko", "alice.foko@email.com", "237633222111"),
        ("jobseeker1", "seeker123", "job_seeker", "David", "Kamto", "david.kamto@email.com", "237611999888")
    ]

    user_ids = {}
    for username, password, role, first_name, last_name, email, phone in sample_users:
        user_id = str(uuid.uuid4())
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute('''
        INSERT INTO users (id, username, password_hash, role, first_name, last_name, 
                          email, phone, created_date, is_active, first_login)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
        ''', (user_id, username, password_hash, role, first_name, last_name, 
              email, phone, datetime.datetime.now()))

        user_ids[username] = user_id

    print("Creating sample stores...")

    # Create sample stores
    sample_stores = [
        ("Matériaux Mballa", "retail", user_ids["retailer1"], "Douala, Akwa", "237677123456"),
        ("Construction Nguesso", "retail", user_ids["contractor1"], "Yaoundé, Centre", "237699987654"),
        ("Dépôt Biya", "contract_owner", user_ids["owner1"], "Bafoussam, Ouest", "237655444333")
    ]

    store_ids = {}
    for store_name, store_type, owner_id, address, phone in sample_stores:
        store_id = str(uuid.uuid4())

        cursor.execute('''
        INSERT INTO stores (id, name, type, owner_id, address, phone, created_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (store_id, store_name, store_type, owner_id, address, phone, datetime.datetime.now()))

        store_ids[store_name] = store_id

    print("Creating sample jobs...")

    # Create sample jobs
    sample_jobs = [
        ("Maçon expérimenté", "Recherche maçon pour construction villa", 
         user_ids["owner1"], "Douala", 250000, "Full-time", 
         "5 ans d'expérience minimum, références requises"),
        ("Électricien", "Installation électrique immeuble", 
         user_ids["retailer1"], "Yaoundé", 200000, "Contract", 
         "Diplôme électricité, habilitation électrique"),
        ("Charpentier", "Travaux de charpente maison individuelle", 
         user_ids["contractor1"], "Bafoussam", 180000, "Part-time", 
         "Expérience charpente traditionnelle et moderne")
    ]

    for title, description, employer_id, location, salary, job_type, requirements in sample_jobs:
        job_id = str(uuid.uuid4())

        cursor.execute('''
        INSERT INTO jobs (id, title, description, employer_id, location, salary, 
                         job_type, requirements, posted_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open')
        ''', (job_id, title, description, employer_id, location, salary, 
              job_type, requirements, datetime.datetime.now()))

    print("Sample data created successfully!")
    print("\nSample login credentials:")
    print("- Admin: admin / admin123")
    print("- Retailer: retailer1 / retail123") 
    print("- Contractor: contractor1 / contract123")
    print("- Owner: owner1 / owner123")
    print("- Manager: manager1 / manager123")
    print("- Job Seeker: jobseeker1 / seeker123")


def create_directories():
    """Create necessary directories"""

    directories = [
        "data",
        "exports",
        "uploads",
        "logs",
        "backups"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    print(f"Created directories: {', '.join(directories)}")


def main():
    """Main setup function"""

    print("=" * 60)
    print("Cameroon Construction Project Management System Setup")
    print("=" * 60)

    try:
        # Create necessary directories
        create_directories()

        # Initialize database
        create_database()

        print("\n" + "=" * 60)
        print("Setup completed successfully!")
        print("=" * 60)
        print("\nYou can now run the application:")
        print("python CPM.py")
        print("\nDefault admin login:")
        print("Username: admin")
        print("Password: admin123")
        print("\nPlease change the default password after first login!")

    except Exception as e:
        print(f"Setup failed with error: {str(e)}")
        return False

    return True


if __name__ == "__main__":
    main()
