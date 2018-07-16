from flask import Flask, render_template  # Flask
from flask.ext.sqlalchemy import SQLAlchemy  # DB

# App
app = Flask(__name__)

# Config
app.config.from_object('config')

# Db
db = SQLAlchemy(app)


# Errors
@app.errorhandler(404)
def not_found(error):
    return render_template('error.jinja2', error=error), 404


# Import modules
from app.m_auth.controllers import m_auth

# Register blueprint(s)
app.register_blueprint(m_auth)

# Build the database
db.create_all()
