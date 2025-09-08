"""
Launcher for the Cameroon Building Project Management System (CBPM)
Run this file to start the GUI application.

It ensures a default administrator account exists, then launches the app.
"""
from datetime import date

try:
    # Import from the main application module
    from CBPM import CBPMApp, DatabaseManager, SecurityManager
except Exception as e:
    raise SystemExit(f"Failed to import main application module: {e}")


def ensure_default_admin():
    """Create default administrator accounts if they do not exist yet."""
    db_manager = DatabaseManager()
    security_manager = SecurityManager()

    conn = db_manager.create_connection()
    cursor = conn.cursor()

    try:
        # Ensure there is at least one administrator; if none, create 'admin'
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'administrator'")
        count = cursor.fetchone()[0]
        if count == 0:
            admin_password = security_manager.hash_password("admin123")
            cursor.execute(
                '''
                INSERT INTO users
                (username, email, password_hash, role, full_name, phone, address, created_date, first_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    'admin',
                    'admin@cbpm.cm',
                    admin_password,
                    'administrator',
                    'System Administrator',
                    '+237 6XX XXX XXX',
                    'Yaoundé, Cameroon',
                    date.today(),
                    0
                )
            )
            conn.commit()
            print("Default admin user created: username='admin', password='admin123'")

        # Ensure the specific 'newadmin' account exists with provided hash
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ('newadmin',))
        exists = cursor.fetchone()[0]
        if exists == 0:
            provided_sha256 = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'
            cursor.execute(
                '''
                INSERT INTO users (
                    username, email, password_hash, role, full_name, phone, address,
                    created_date, is_active, first_login, failed_login_attempts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    'newadmin',
                    'newadmin@cbpm.cm',
                    provided_sha256,
                    'administrator',
                    'New Administrator',
                    '',
                    '',
                    date.today(),
                    1,
                    1,
                    0
                )
            )
            conn.commit()
            print("Admin user 'newadmin' created with provided password hash.")

        # One-time admin password reset (avoid resetting on every run via flag file)
        try:
            import os as _os, json as _json
            from datetime import datetime as _dt
            flag_dir = _os.path.join(_os.path.expanduser('~'), 'Documents', 'CBPM')
            _os.makedirs(flag_dir, exist_ok=True)
            flag_file = _os.path.join(flag_dir, 'admin_reset_done.flag')
            if not _os.path.exists(flag_file):
                try:
                    new_pwd = 'Admin@2025!Reset'
                    new_hash = security_manager.hash_password(new_pwd)
                    cur2 = conn.cursor()
                    cur2.execute("UPDATE users SET password_hash=?, first_login=1, is_active=1, failed_login_attempts=0 WHERE username IN ('admin','newadmin')", (new_hash,))
                    conn.commit()
                    with open(flag_file, 'w', encoding='utf-8') as f:
                        f.write(_json.dumps({'reset': True, 'usernames': ['admin','newadmin'], 'when': _dt.now().isoformat()}))
                    print("Admin credentials have been reset. Use username 'admin' or 'newadmin' with the new temporary password provided in instructions.")
                except Exception as _rex:
                    try:
                        print(f"[WARN] Admin reset failed: {_rex}")
                    except Exception:
                        pass
        except Exception:
            pass
    finally:
        conn.close()


def main():
    ensure_default_admin()
    app = CBPMApp()
    app.run()


if __name__ == "__main__":
    main()
