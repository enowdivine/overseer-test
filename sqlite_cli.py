#!/usr/bin/env python3
"""
Lightweight SQLite CLI for Windows (and cross-platform) without needing the external `sqlite3` executable.

Usage (PowerShell examples):
  # Use default DB from config.DATABASE_NAME if available
  python sqlite_cli.py --tables

  # Specify database file
  python sqlite_cli.py cameroon_construction.db --tables
  python sqlite_cli.py cameroon_construction.db --schema users
  python sqlite_cli.py cameroon_construction.db --execute "SELECT name FROM sqlite_master WHERE type='table'"
  python sqlite_cli.py cameroon_construction.db --file schema.sql
  python sqlite_cli.py cameroon_construction.db --dump > backup.sql

  # Interactive shell
  python sqlite_cli.py cameroon_construction.db
  # Then type SQL statements ending with semicolon; use .help, .tables, .schema, .exit commands

Notes:
- This tool uses Python's built-in sqlite3 module.
- It prints results in a simple table form.
"""
import argparse
import os
import sys
import sqlite3
from typing import Optional, Sequence

DEFAULT_DB = None
try:
    # Try to use configured DB name if available
    from config import DATABASE_NAME as _DB
    DEFAULT_DB = _DB
except Exception:
    # Fallback to common names
    for name in ("cameroon_construction.db", "cbpm.db"):
        if os.path.exists(name):
            DEFAULT_DB = name
            break


def connect(db_path: str) -> sqlite3.Connection:
    if not db_path:
        raise SystemExit("No database file provided and no default found. Pass a DB filename as first argument.")
    return sqlite3.connect(db_path)


def print_rows(cursor: sqlite3.Cursor, rows: Sequence[Sequence]):
    try:
        headers = [d[0] for d in cursor.description] if cursor.description else []
    except Exception:
        headers = []
    if not rows:
        if headers:
            print(" | ".join(headers))
        print("(no rows)")
        return
    # Compute column widths
    cols = len(rows[0]) if rows else len(headers)
    col_widths = [0] * cols
    for i in range(cols):
        head_len = len(str(headers[i])) if i < len(headers) else 0
        col_widths[i] = head_len
    for r in rows:
        for i, val in enumerate(r):
            col_widths[i] = max(col_widths[i], len(str(val if val is not None else "")))
    # Print header
    if headers:
        line = " | ".join(str(headers[i]).ljust(col_widths[i]) for i in range(len(headers)))
        print(line)
        print("-+-".join("-" * w for w in col_widths))
    # Print rows
    for r in rows:
        print(" | ".join(str(("" if v is None else v)).ljust(col_widths[i]) for i, v in enumerate(r)))


def cmd_tables(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name")
    rows = cur.fetchall()
    print_rows(cur, rows)


def cmd_schema(conn: sqlite3.Connection, table: Optional[str]):
    cur = conn.cursor()
    if table:
        cur.execute("SELECT sql FROM sqlite_master WHERE name = ?", (table,))
        row = cur.fetchone()
        if not row or not row[0]:
            print(f"No schema found for table '{table}'")
        else:
            print(row[0])
    else:
        cur.execute("SELECT sql FROM sqlite_master WHERE type IN ('table','index','view') AND sql IS NOT NULL ORDER BY type, name")
        rows = cur.fetchall()
        for (sql,) in rows:
            print(f"{sql};\n")


def cmd_execute(conn: sqlite3.Connection, sql: str):
    cur = conn.cursor()
    try:
        cur.execute(sql)
        if cur.description:
            rows = cur.fetchall()
            print_rows(cur, rows)
        else:
            conn.commit()
            print("OK")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_file(conn: sqlite3.Connection, filename: str):
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        sys.exit(1)
    with open(filename, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    print("OK")


def cmd_dump(conn: sqlite3.Connection):
    for line in conn.iterdump():
        print(line)


def interactive(conn: sqlite3.Connection):
    cur = conn.cursor()
    print("SQLite interactive shell (Python-based). Type .help for help. End statements with ';'.")
    buffer: list[str] = []
    while True:
        try:
            prompt = "... " if buffer else "sqlite> "
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        line_strip = line.strip()
        # Dot-commands
        if not buffer and line_strip.startswith('.'):
            cmd = line_strip.split()
            if cmd[0] in ('.exit', '.quit', '.q'):
                break
            elif cmd[0] == '.help':
                print(
                    ".tables                 List tables/views\n"
                    ".schema [TABLE]         Show schema (all or specific table)\n"
                    ".dump                   Output full dump\n"
                    ".exit / .quit / .q      Exit shell\n"
                    "End SQL with ';' to execute."
                )
            elif cmd[0] == '.tables':
                cmd_tables(conn)
            elif cmd[0] == '.schema':
                table = cmd[1] if len(cmd) > 1 else None
                cmd_schema(conn, table)
            elif cmd[0] == '.dump':
                cmd_dump(conn)
            else:
                print(f"Unknown command: {cmd[0]}")
            continue
        # Accumulate SQL until ';'
        buffer.append(line)
        joined = "\n".join(buffer)
        if joined.strip().endswith(';'):
            try:
                cur.execute(joined)
                if cur.description:
                    rows = cur.fetchall()
                    print_rows(cur, rows)
                else:
                    conn.commit()
                    print("OK")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                buffer.clear()


def main():
    parser = argparse.ArgumentParser(description="SQLite CLI without external sqlite3.")
    parser.add_argument('db', nargs='?', default=DEFAULT_DB, help='Path to SQLite database file')
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--tables', action='store_true', help='List tables')
    g.add_argument('--schema', nargs='?', const='', metavar='TABLE', help='Show schema (all or given TABLE)')
    g.add_argument('--execute', '-e', metavar='SQL', help='Execute a single SQL statement')
    g.add_argument('--file', '-f', dest='sql_file', metavar='SQL_FILE', help='Execute SQL from file')
    g.add_argument('--dump', action='store_true', help='Dump the database to SQL (stdout)')
    args = parser.parse_args()

    conn = connect(args.db)
    try:
        if args.tables:
            cmd_tables(conn)
        elif args.schema is not None and args.schema != False:
            table = args.schema if args.schema != '' else None
            cmd_schema(conn, table)
        elif args.execute:
            cmd_execute(conn, args.execute)
        elif args.sql_file:
            cmd_file(conn, args.sql_file)
        elif args.dump:
            cmd_dump(conn)
        else:
            interactive(conn)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
