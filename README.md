# Django Task Manager

A Django web app for managing personal to-do tasks. Users can create an account, sign in, create and edit tasks, assign a priority and status, filter their task list, and delete tasks. Each task is associated with its owner.

## Features

- Account registration, login, and logout
- Personal task lists backed by SQLite
- Create, update, and delete tasks
- Task priority: high, medium, or low
- Task status: pending, in progress, or completed
- Filter tasks by priority or status
- Per-user task access checks and CSRF-protected form/AJAX writes
- Phone number saved on the user profile during registration

## Project layout

The Django project is inside `TODO_PROJECT/`:

- `TODO_PROJECT/manage.py` — Django management entry point
- `TODO_PROJECT/TODO_PROJECT/` — project settings and URL configuration
- `TODO_PROJECT/ToDoApplication/` — task model, views, templates, static JavaScript, and tests
- `TODO_PROJECT/db.sqlite3` — SQLite database file included in the repository
- `TODO_PROJECT/requirements.txt` — pinned Python dependencies

## Requirements

- Python 3.10 or newer recommended
- pip

## Run locally

From the repository root, create and activate a virtual environment, then install dependencies:

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r TODO_PROJECT/requirements.txt
cd TODO_PROJECT
python manage.py migrate
python manage.py runserver
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r TODO_PROJECT/requirements.txt
cd TODO_PROJECT
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and register an account. Django's development server is for local development only.

## Configuration and deployment

Settings can be configured with environment variables:

- `DJANGO_SECRET_KEY` — secret key; the fallback in settings is only for local development
- `DJANGO_DEBUG` — defaults to `true`; set to `false` in deployment
- `DJANGO_ALLOWED_HOSTS` — comma-separated hostnames; defaults to local development hosts

For example, in PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = "replace-with-a-long-random-secret"
$env:DJANGO_DEBUG = "false"
$env:DJANGO_ALLOWED_HOSTS = "example.com,www.example.com"
```

Before deploying, configure a strong secret key and allowed hosts, use a production-ready database and web server, and review Django's deployment checklist. The checked-in SQLite database is provided as a development artifact; do not rely on it as production storage.

## Tests

The repository currently has no implemented automated tests; `ToDoApplication/tests.py` is a Django test scaffold. Add tests for registration, authentication, task ownership, and task validation before relying on the app.

## Notes

- Static JavaScript and styles use jQuery and Bootstrap from public CDNs, so those assets require an internet connection in the browser.
- Registration currently validates the phone format in the browser. Server-side phone format validation should also be added before using this app in a public deployment.
- This is a learning project, not a hardened production service. Review configuration, input validation, privacy, and operational needs before exposing it to the internet.
