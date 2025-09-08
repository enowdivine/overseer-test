# Cameroon Building Project Management System (CBPM)

A comprehensive role-based system for managing building projects in Cameroon.

This project targets Windows and uses SQLite as its primary datastore. It provides a Tkinter-based desktop UI along with utility scripts.

Android note: Tkinter is not supported on Android. Running CBPM.py on Android will now gracefully inform you and point to docs\\android.md for the mobile approach (Kivy front-end + API backend).

## Getting started (Windows)

1. Create and activate a virtual environment (optional but recommended)

```powershell
# From the project root
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
# If there is no requirements.txt, dependencies are typically standard library + tkinter + sqlite3 + pandas, and optional:
# matplotlib, cryptography, smtplib (standard library)
```

3. Run the application

```powershell
py .\CBPM.py
```

If Matplotlib or Cryptography are not available, the application should still start with reduced functionality.

## Utilities

- SQLite CLI helper:

```powershell
py .\sqlite_cli.py --help
```

## Contribution guidelines

Please follow the repository guidelines in `.junie\guidelines.md`.

Key points:

- PEP 8/257; use type hints on new/modified function signatures.
- Google-style docstrings with Args/Returns/Raises.
- Use `logging` instead of `print`; avoid bare `except:`.
- Windows-style paths in docs/examples and UTF-8 + LF newlines.

## Improvement plan and tasks

- Plan: see `docs\plan.md`.
- Task list: see and update `docs\tasks.md`. When you complete a task, change its checkbox from `[ ]` to `[x]`.

## License

Proprietary or as defined by the repository owner.

## Smoke check

Run the smoke script to verify the database layer can be initialized:

```powershell
py .\scripts\smoke_check.py
```

Exit code 0 indicates success; any non-zero indicates failure.
