from calendar import day_name  # Days
from datetime import timedelta, datetime  # Times
from typing import Union, Callable, List  # Typing

from app import db, Base_Model  # DB


# Define a Session model
class Session(Base_Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)
    archived = db.Column(db.SmallInteger, nullable=False, default=0)

    assignments = db.relationship('Assignment')
    unavailabilities = db.relationship('Unavailability')

    # New instance instantiation procedure
    def __init__(self, day: int, start_time: int, end_time: int):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time

    @property
    def day_frmt(self):
        return list(day_name)[self.day]  # day name

    @property
    def start_time_frmt(self):
        return str(timedelta(minutes=self.start_time))[:-3]  # hours:minutes

    @property
    def end_time_frmt(self):
        return str(timedelta(minutes=self.end_time))[:-3]  # hours:minutes


# Define an Assignment model
class Assignment(Base_Model):
    __tablename__ = 'assignments'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    user = db.relationship('User')

    session_id = db.Column(
        db.Integer,
        db.ForeignKey('sessions.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    session = db.relationship('Session')

    # New instance instantiation procedure
    def __init__(self, user_id: int, session_id: int):
        self.user_id = user_id
        self.session_id = session_id


# Convert sessions to the view needed for the rota
def session_to_rota_view(session: Session, highlight_check: Union[Callable, None] = None) -> List[list]:
    data = [False, []]
    data[1].append(session.start_time_frmt)  # Get hours:minutes
    data[1].append(session.end_time_frmt)  # Get hours:minutes

    # Usernames
    data[1].append([])
    for assignment in session.assignments:
        data[1][-1].append(assignment.user.username)
        # Highlight
        if highlight_check is not None and highlight_check(assignment):
            data[0] = True
    data[1][-1] = ", ".join(data[1][-1]) or "<i>None</i>"

    return data


# Define an Unavailability model
class Unavailability(Base_Model):
    __tablename__ = 'unavailabilities'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    user = db.relationship('User')

    session_id = db.Column(
        db.Integer,
        db.ForeignKey('sessions.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    session = db.relationship('Session')

    reason = db.Column(db.String, nullable=False)

    # New instance instantiation procedure
    def __init__(self, user_id: int, session_id: int, reason: str):
        self.user_id = user_id
        self.session_id = session_id
        self.reason = reason


# Define an Attendance model
class Attendance(Base_Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    user = db.relationship('User')

    session_id = db.Column(
        db.Integer,
        db.ForeignKey('sessions.id', ondelete='CASCADE'),
        nullable=False,
    )
    session = db.relationship('Session')

    in_time = db.Column(db.DateTime, nullable=False)
    out_time = db.Column(db.DateTime, nullable=True, default=None)

    # New instance instantiation procedure
    def __init__(self, user_id: int, session_id: int, in_time: datetime = None, out_time: datetime = None):
        self.user_id = user_id
        self.session_id = session_id
        self.in_time = in_time if in_time else datetime.utcnow()
        self.out_time = out_time
