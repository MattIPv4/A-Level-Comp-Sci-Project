from app import db, Base_Model  # DB
from calendar import day_name # Days
from datetime import timedelta  # Times
from typing import Union, Callable, List  # Typing


# Define a Session model
class Session(Base_Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)
    archived = db.Column(db.SmallInteger, nullable=False, default=0)

    assignments = db.relationship('Assignment')

    day_frmt = list(day_name)[day] # day name
    start_time_frmt = str(timedelta(minutes=start_time))[:-3] # hours:minutes
    end_time_frmt = str(timedelta(minutes=end_time))[:-3] # hours:minutes

    # New instance instantiation procedure
    def __init__(self, day: int, start_time: int, end_time: int):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time


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
def session_to_view(session: Session, highlight_check: Union[Callable, None] = None) -> List[list]:
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
    data[1][-1] = ", ".join(data[1][-1])

    return data
