from app import db, Base_Model  # DB


# Define a User model
class User(Base_Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    auth_level = db.Column(db.SmallInteger, nullable=False)
    disabled = db.Column(db.SmallInteger, nullable=False, default=0)

    # New instance instantiation procedure
    def __init__(self, username: str, password: str, auth_level: int):
        self.username = username
        self.password = password
        self.auth_level = auth_level

    def __repr__(self):
        return '<User %r>' % (self.username)
