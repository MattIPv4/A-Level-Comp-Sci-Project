from datetime import datetime  # Datetime
from typing import Union, Tuple  # Typing

import jinja2  # Templates
from flask import Flask, render_template  # Flask
from flask_sqlalchemy import SQLAlchemy  # DB
from sqlalchemy import create_engine  # DB Engine
from sqlalchemy.orm import sessionmaker  # DB Session
from werkzeug.exceptions import HTTPException  # Errors

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
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker()
Session.configure(bind=engine)


# Base model for other database tables to inherit
class Base_Model(db.Model):
    __abstract__ = True


def db_session():
    session = Session()
    return session


# Errors
def error_render(code: Union[int, str], extra: str = "") -> Tuple[str, int]:
    message = str(code)
    details = ""
    data = Utils.status_message(code)
    if data:
        message = data[3]
        details = data[2]
    return render_template("app/error.jinja2", error_message=message, error_details=details, error_extra=extra), code


# Import modules
from app.modules import auth
from app.modules import student
from app.modules.auth.controllers import auth as blueprint_auth
from app.modules.student.controllers import student as blueprint_student

# Register blueprint(s)
app.register_blueprint(blueprint_auth)
app.register_blueprint(blueprint_student)

# Build the database
__a = [
    auth, student
]  # Convince pycharm things are used (and stop warnings)
db.create_all()


@app.context_processor
def variables() -> dict:
    __a = [
        datetime,
        auth
    ]  # Convince pycharm things are used (and stop warnings)
    return dict(**globals())


@app.route('/error/<int:code>')
def error(code: int):
    return error_render(code)


@app.errorhandler(Exception)
def http_error_handler(error):
    code = 500
    if isinstance(error, HTTPException):
        code = error.code
    if code == 500:
        if app.debug:
            raise error
    return error_render(code)


from werkzeug.exceptions import default_exceptions # Errors

for ex in default_exceptions:
    app.register_error_handler(ex, http_error_handler)


# Index
@app.route('/')
def index():
    return render_template("index.jinja2")
