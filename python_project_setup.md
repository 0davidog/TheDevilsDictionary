# 🐍 Python Project Setup (VSCode)

A step-by-step guide for setting up Python projects with virtual environments, dependency management, and common workflows in Visual Studio Code.

---

## 📁 1. Project Initialization

```bash
mkdir my_project
cd my_project
```

---

## 🧪 2. Create a Virtual Environment

```bash
python -m venv .venv
```

- `.venv` is a convention for naming the virtual environment folder.
- Activate it:
  - **Windows (PowerShell):** `./.venv/Scripts/Activate.ps1`
  - **Windows (cmd):** `./.venv/Scripts/activate.bat`
  - **macOS/Linux:** `source .venv/bin/activate`

---

## ⚙️ 3. Configure VSCode to Use the Virtual Environment

- Open the command palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
- Select `Python: Select Interpreter`
- Choose the interpreter from `.venv`

> Tip: If `.venv` isn't detected, reload VSCode or re-open the folder.

---

## 📦 4. Install Required Packages

- To install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

- To create `requirements.txt`:

```bash
pip freeze > requirements.txt
```

---

## 🧱 5. Django-Specific Setup

### Install Django

```bash
pip install django
```

### Start a New Project

```bash
django-admin startproject mysite .
```

### Run the Development Server

```bash
python manage.py runserver
```

### Create an App

```bash
python manage.py startapp myapp
```

### Apply Migrations

```bash
python manage.py migrate
```

### Create a Superuser (for admin panel)

```bash
python manage.py createsuperuser
```

---

## 🔐 6. Manage Secrets with `.env`

Install `python-dotenv`:

```bash
pip install python-dotenv
```

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=your-db-url
```

Load it in your code (example):

```python
from dotenv import load_dotenv
load_dotenv()
import os
SECRET_KEY = os.getenv("SECRET_KEY")
```

> 🔒 **Never commit **``** to Git!** Add it to `.gitignore`.

---

## 🧾 7. Git Version Control

### Initialize Git

```bash
git init
git add .
git commit -m "Initial commit"
```

### Recommended `.gitignore`

```gitignore
.venv/
__pycache__/
*.pyc
.env
*.sqlite3
```

---

## 🚀 8. Deployment Checklist

### For Django

- Set `DEBUG = False`
- Set `ALLOWED_HOSTS = ['yourdomain.com']`
- Use a production WSGI server like Gunicorn
- Use environment variables for secrets
- Serve static files via WhiteNoise or a CDN
- Use a PostgreSQL database (e.g., via Heroku or Railway)

### Example Heroku Deployment

```bash
heroku create
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DISABLE_COLLECTSTATIC=1

git push heroku main
heroku run python manage.py migrate
heroku open
```

---

## ✅ Final Tips

- Always work inside your virtual environment
- Use `pip freeze > requirements.txt` regularly
- Use `.env` for secrets
- Keep `.venv` and `.env` out of version control
- Use meaningful commit messages in Git

---

Happy coding! 🧑‍💻

