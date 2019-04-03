# Dev
DEBUG = True

# App
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# DB
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

# Threads
THREADS_PER_PAGE = 2

# CSRF / Security
CSRF_ENABLED = True
CSRF_SESSION_KEY = "secret"
SECRET_KEY = "secret"
