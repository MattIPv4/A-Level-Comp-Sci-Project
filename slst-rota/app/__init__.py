from flask import Flask, render_template, session  # Flask
from flask_sqlalchemy import SQLAlchemy  # DB
from typing import Tuple  # Typing
import jinja2, os  # Templates
from datetime import datetime  # Datetime

from .sasswatcher import SassWatcher  # SASS
from .utils import Utils  # Utils

# App
app = Flask("SLST Rota")
loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader(Utils.absolute_path('templates')),
])
app.jinja_loader = loader

# Styles
app.debug = True
watcher = SassWatcher("app/assets/scss", "app/static/css")
watcher.run()

# Config
app.config.from_object('config')

# Static
app.static_url_path = "/static"
app.static_folder = Utils.absolute_path('static')

# Db
db = SQLAlchemy(app)

# Import modules
from app.modules import auth
from app.modules.auth.controllers import auth as blueprint_auth

# Register blueprint(s)
app.register_blueprint(blueprint_auth)

# Build the database
db.create_all()


@app.context_processor
def variables() -> dict:
    a = [
        datetime,
        auth
    ]  # Convince pycharm its used (and stop warnings)
    return dict(**globals())


# Errors
def error_render(code: int, extra: str = "") -> Tuple[str, int]:
    message = str(code)
    details = ""
    data = Utils.status_message(code)
    if data:
        message = data[3]
        details = data[2]
    return render_template("app/error.jinja2", error_message=message, error_details=details, error_extra=extra), code


@app.route('/error/<int:code>')
def error(code: int):
    return error_render(code)


@app.errorhandler(404)
def not_found(error):
    return error_render(404)


# Index
@app.route('/')
def index():
    return render_template("index.jinja2")
