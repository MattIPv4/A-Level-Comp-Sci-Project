from calendar import day_name  # Days
from datetime import timedelta, datetime, date  # Times
from typing import Union, Callable, List, Tuple  # Typing

from app import db, Base_Model, Utils  # DB


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
        dt = Utils.minutes_today(self.start_time)
        return dt.strftime("%H:%M")

    @property
    def end_time_frmt(self):
        dt = Utils.minutes_today(self.end_time)
        return dt.strftime("%H:%M")


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

    created = db.Column(db.DateTime, nullable=False)

    # New instance instantiation procedure
    def __init__(self, user_id: int, session_id: int, created: datetime = None):
        self.user_id = user_id
        self.session_id = session_id
        self.created = created or datetime.now()

    @property
    def attendance(self) -> List[Tuple[date, Union['Attendance', None]]]:
        results = []
        delta = datetime.now().date() - self.created.date()

        for i in range(delta.days + 1):
            # Day assignment created, if assignment created after session start, ignore
            if i == 0:
                if Utils.minutes_datetime(self.created) >= self.session.start_time:
                    continue

            d = self.created.date() + timedelta(days=i)

            data = Attendance.query.filter_by(user_id=self.user_id, session_id=self.session_id, date=d).first()

            # If has not happened yet
            if d == datetime.now().date() and (self.session.start_time >= Utils.minutes_now() or (
                    Utils.minutes_now() <= self.session.end_time and ((data and not data.out_time)) or not data)):
                continue

            results.append((d, data))

        return results


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

    date = db.Column(db.Date, nullable=False)
    in_time = db.Column(db.DateTime, nullable=False)
    in_time_org = db.Column(db.DateTime, nullable=False)
    out_time = db.Column(db.DateTime, nullable=True, default=None)
    out_time_org = db.Column(db.DateTime, nullable=False)

    # New instance instantiation procedure
    def __init__(self, user_id: int, session_id: int, in_time_org: datetime, out_time_org: datetime, date: date = None,
                 in_time: datetime = None, out_time: datetime = None):
        self.user_id = user_id
        self.session_id = session_id
        self.date = date or datetime.now().date()
        self.in_time = in_time or datetime.now()
        self.in_time_org = in_time_org
        self.out_time = out_time
        self.out_time_org = out_time_org

    # New instance from a session instance to make things easier
    @classmethod
    def from_session(cls, user_id: int, session: Session) -> 'Attendance':
        return cls(user_id, session.id, Utils.minutes_today(session.start_time), Utils.minutes_today(session.end_time))

    @property
    def in_diff(self) -> float:
        # Minutes
        return (self.in_time - self.in_time_org).total_seconds() / 60

    @property
    def out_diff(self) -> float:
        # Minutes
        return ((self.out_time or self.out_time_org) - self.out_time_org).total_seconds() / 60

    @property
    def current(self) -> bool:
        if self.in_time_org < datetime.now() < self.out_time_org and not self.out_time:
            return True
        return False
