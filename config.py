# Configuration file for Cameroon Construction Project Management System

# Database configuration
DATABASE_NAME = "cameroon_construction.db"

# Cloud database settings (for shared database)
CLOUD_DB_SETTINGS = {
    'enabled': True,  # Set to True to enable cloud database
    'provider': 'google_drive',  # Options: 'google_drive', 'dropbox', 'ftp', 'local'
    'remote_path': '',  # Remote path to database file
    'sync_interval': 30,  # Sync interval in seconds
    'backup_enabled': True,  # Enable local backups
    'google_drive_file_id': '1mtyBi86H4WPTJze8KQ4K2Ow3D-LiFrU7'  # Your Google Drive file ID
}

# Default system settings
SYSTEM_NAME = "Cameroon Construction Project Management System"
VERSION = "1.0.0"
COMPANY = "Cameroon Construction Ltd."

# User roles
USER_ROLES = {
    'administrator': {
        'name': 'Administrator',
        'permissions': ['create_users', 'manage_system', 'view_all_data', 'system_analytics']
    },
    'retail_store': {
        'name': 'Retail Store Owner',
        'permissions': ['manage_stores', 'inventory_management', 'sales', 'transfers', 'job_posting']
    },
    'contract_owner': {
        'name': 'Contract Owner',
        'permissions': ['manage_stores', 'contracts', 'payments', 'transfers', 'job_posting']
    },
    'contractor': {
        'name': 'Contractor',
        'permissions': ['view_contracts', 'sign_contracts', 'job_posting', 'material_reports']
    },
    'manager': {
        'name': 'Store Manager',
        'permissions': ['limited_store_access', 'inventory_view', 'basic_operations']
    },
    'job_seeker': {
        'name': 'Job Seeker',
        'permissions': ['browse_jobs', 'apply_jobs', 'profile_management']
    }
}

# Construction material categories specific to Cameroon
MATERIAL_CATEGORIES = [
    'Cement',
    'Blocks', 
    'Steel',
    'Timber',
    'Roofing',
    'Electrical',
    'Plumbing',
    'Finishing',
    'Tools',
    'Aggregates',
    'Doors',
    'Windows',
    'Wood Products',
    'Concrete',
    'Other'
]

# Common units of measurement
MATERIAL_UNITS = [
    'Piece',
    'Bag',
    'Meter',
    'Roll',
    'Sheet', 
    'Liter',
    'm²',
    'm³',
    'Kg',
    'Ton',
    'Set',
    'Rod'
]

# Job types
JOB_TYPES = [
    'Full-time',
    'Part-time', 
    'Contract',
    'Temporary',
    'Internship',
    'Project-based'
]

# Role constants (use centralized constants to avoid placeholder tokens)
ROLE_JOB_SEEKER = 'job_seeker'

# Transaction types
TRANSACTION_TYPES = [
    'sale',
    'transfer',
    'purchase', 
    'consumption',
    'adjustment'
]

# Store types
STORE_TYPES = [
    'retail',
    'contract_owner'
]

# Payment types
PAYMENT_TYPES = [
    'contract',
    'salary',
    'material',
    'service',
    'other'
]

# System security settings
SECURITY_SETTINGS = {
    'min_password_length': 8,
    'max_failed_login_attempts': 5,
    'session_timeout_minutes': 60,
    'require_password_change_days': 90
}

# Currency settings
CURRENCY = {
    'code': 'XAF',
    'name': 'CFA Franc',
    'symbol': 'FCFA'
}

# Regional settings for Cameroon
REGIONAL_SETTINGS = {
    'country': 'Cameroon',
    'timezone': 'Africa/Douala',
    'date_format': '%d/%m/%Y',
    'time_format': '%H:%M:%S'
}

# Scalability and database tuning settings (centralized for easy tuning)
SCALABILITY_SETTINGS = {
    'sqlite': {
        # Write-ahead logging improves concurrency
        'journal_mode': 'WAL',
        # NORMAL offers better throughput vs FULL while keeping safety in most cases
        'synchronous': 'NORMAL',
        # Enable foreign key enforcement
        'foreign_keys': 1,
        # Negative cache size means KB pages in memory; -20000 ≈ ~20MB target cache
        'cache_size': -20000,
        # Use memory for temp structures to avoid disk I/O where possible
        'temp_store': 2,
        # Busy timeout in ms to reduce "database is locked" errors
        'busy_timeout': 5000
    }
}

# Common Cameroon cities for location dropdown
CAMEROON_CITIES = [
    'Douala',
    'Yaoundé', 
    'Bamenda',
    'Bafoussam',
    'Garoua',
    'Maroua',
    'Ngaoundéré',
    'Bertoua',
    'Ebolowa',
    'Kumba',
    'Limbe',
    'Buea',
    'Kribi',
    'Dschang',
    'Foumban'
]
