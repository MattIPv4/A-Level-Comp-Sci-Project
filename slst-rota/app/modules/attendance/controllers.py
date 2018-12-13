import calendar  # Calendar

from flask import Blueprint, redirect, url_for, render_template  # Flask

from app import error_render, Utils  # DB, Errors, Utils
from app.modules import auth  # Auth
from app.modules.auth.models import User  # User
from app.modules.student.models import Assignment  # Rota Sessions

# Blueprint
__a = [

]  # Convince pycharm things are used (and stop warnings)
attendance = Blueprint('attendance', __name__, url_prefix='/attendance')


# Standard check for all routes
def auth_check(student_page_id: int = None):
    user = auth.current_user()
    error = None

    # If no session exists
    if not error and not user:
        error = redirect(url_for('auth.login'))

    # If not staff
    if not error and user.auth_level != 2:
        # Allow student to view own page
        if not student_page_id or user.id != student_page_id:
            error = error_render("Staff access only",
                                 "This page is only accessible to users with the staff authentication level")

    return user, error


# Assignment report
class AssignmentReport:

    def __init__(self, assignment_data):
        self.assignment = assignment_data

        # Get all attendance records for assignment
        self.attendance = [f for f in self.assignment.attendance if not f[1] or (f[1] and not f[1].current)]
        self.total = len(self.attendance)
        self.present = sum(1 for f in self.attendance if f[1])
        self.absent = self.total - self.present

        # Get how late in for each attendance record
        self.in_diff = [f[1].in_diff for f in self.attendance if f[1]]
        self.in_diff_avg = (sum(self.in_diff) / len(self.in_diff)) if self.in_diff else 0
        self.in_on_time = sum(1 for f in self.attendance if f[1] and f[1].in_diff < 1)

        # Get how early out for each attendance record
        self.out_diff = [f[1].out_diff for f in self.attendance if f[1]]
        self.out_diff_avg = (sum(self.out_diff) / len(self.out_diff)) if self.out_diff else 0
        self.out_on_time = sum(1 for f in self.attendance if f[1] and (not f[1].out_time or f[1].out_diff > -1))

    @property
    def table(self):
        return [
            False,  # Highlight
            [  # Columns
                self.assignment.session.start_time_frmt,
                self.assignment.session.end_time_frmt,
                "{:.2f}% ({:,}/{:,})".format(
                    (self.present / self.total) * 100, self.present, self.total
                ) if self.total else "No attendance records",
                "In: {:,.0f} minute{} {} / Out: {:,.0f} minute{} {}"
                "<br/>In on time: {:.2f}% / Out on time: {:.2f}%".format(
                    abs(self.in_diff_avg),
                    Utils.unit_s(abs(self.in_diff_avg)),
                    "late" if self.in_diff_avg >= 0 else "early",

                    abs(self.out_diff_avg),
                    Utils.unit_s(abs(self.out_diff_avg)),
                    "late" if self.out_diff_avg > 0 else "early",

                    (self.in_on_time / self.total) * 100,
                    (self.out_on_time / self.total) * 100,
                ) if self.total else "No attendance records"
            ]
        ]


# The student report class
class StudentReport:

    def __init__(self, student_id: int):
        # Fetch all assignment data for the student
        self.__assignments = [f for f in Assignment.query.filter_by(user_id=student_id).all() if not f.session.archived]
        self.breakdown = []

        # Totals data
        self.__attendance_total = 0
        self.__attendance_present = 0
        self.__attendance_absent = 0
        self.__attendance_in_diff = []
        self.__attendance_in_on_time = 0
        self.__attendance_out_diff = []
        self.__attendance_out_on_time = 0
        self.__attendance_table = []
        self.__current_day = None

        # Compile assignment attendance data
        for assignment in self.__assignments:
            # Get report
            data = AssignmentReport(assignment)
            self.breakdown.append(data)

            # Update totals data
            self.__attendance_total += data.total
            self.__attendance_present += data.present
            self.__attendance_absent += data.absent
            self.__attendance_in_diff.extend(data.in_diff)
            self.__attendance_in_on_time += data.in_on_time
            self.__attendance_out_diff.extend(data.out_diff)
            self.__attendance_out_on_time += data.out_on_time

            # Table: Day subheadings
            if assignment.session.day != self.__current_day:
                self.__attendance_table.append([False, [list(calendar.day_name)[assignment.session.day], "", "", ""]])
                self.__current_day = assignment.session.day

            # Table: Assignment
            self.__attendance_table.append(data.table)

        # Calculate overall tardiness
        self.__attendance_in_diff_avg = (sum(self.__attendance_in_diff) / len(self.__attendance_in_diff)) \
            if self.__attendance_in_diff else 0
        self.__attendance_out_diff_avg = (sum(self.__attendance_out_diff) / len(self.__attendance_out_diff)) \
            if self.__attendance_out_diff else 0

        # Default word-y stats
        self.__attendance_stat = "No attendance records found for your user."
        self.__punctuality_stat = "No attendance records found for your user."

        # Proper word-y stats if has attendance
        if self.__attendance_total != 0:
            # Attendance stats
            self.__attendance_stat = "<b>{:.2f}%</b> - {:,}/{:,} assigned sessions attended.".format(
                (self.__attendance_present / self.__attendance_total) * 100, self.__attendance_present,
                self.__attendance_total)

            # Punctuality stats
            self.__punctuality_stat = "<b>{:,.0f} minute{} {} sign in avg.</b> - Signed out {:,.0f} minute{} {} avg." \
                                      "<br/><b>In on time (or early) {:.2f}%</b> - Out on time {:.2f}%".format(
                abs(self.__attendance_in_diff_avg),
                Utils.unit_s(abs(self.__attendance_in_diff_avg)),
                "late" if self.__attendance_in_diff_avg >= 0 else "early",

                abs(self.__attendance_out_diff_avg),
                Utils.unit_s(abs(self.__attendance_out_diff_avg)),
                "late" if self.__attendance_out_diff_avg > 0 else "early",

                (self.__attendance_in_on_time / self.__attendance_total) * 100,
                (self.__attendance_out_on_time / self.__attendance_total) * 100,
            )

        # Present/Absence percentages
        self.__attendance_present = (self.__attendance_present / self.__attendance_total) * 100 \
            if self.__attendance_total else 0
        self.__attendance_absent = (self.__attendance_absent / self.__attendance_total) * 100 \
            if self.__attendance_total else 0

        # Attendance bar
        self.__attendance_bar = "<div class=\"stat-bar\">" \
                                "<span class=\"success\" style=\"width: {}%;\"></span>" \
                                "<span class=\"danger\" style=\"width: {}%;\"></span>" \
                                "</div>".format(self.__attendance_present,
                                                self.__attendance_absent if self.__attendance_total else 0)

        # Store into class
        self.attendance = self.__attendance_stat
        self.punctuality = self.__punctuality_stat
        self.present = self.__attendance_present
        self.absent = self.__attendance_absent
        self.table = self.__attendance_table
        self.attendance_bar = self.__attendance_bar


# Attendance Home
@attendance.route('/', methods=['GET'])
def home():
    user, error = auth_check()
    if error:
        return error

    table = []
    session_data = {}
    students = User.query.filter_by(auth_level=1, disabled=0).all()
    for this_student in students:
        report = StudentReport(this_student.id)
        # Generate table
        table.append([
            (report.present < 75),
            [
                this_student.username,
                report.attendance_bar + "\n" + report.attendance,
                report.punctuality,
                "<a href=\"{}\" class=\"button primary\">View full report</a>".format(
                    url_for("attendance.student", student_id=this_student.id))
            ]
        ])
        # Compile session data
        for assignment in report.breakdown:
            # Get raw assignment
            assignment_raw = assignment.assignment
            # Added to session_data if not there
            if assignment_raw.session.id not in session_data:
                session_data[assignment_raw.session.id] = [assignment_raw.session, 0, 0]  # session, present, total
            # Update with present and total from this assignment
            session_data[assignment_raw.session.id][1] += assignment.present
            session_data[assignment_raw.session.id][2] += assignment.total

    return render_template("attendance/home.jinja2", attendance_table=table)


# Student overview
@attendance.route('/student/<int:student_id>', methods=['GET'])
def student(student_id: int):
    this_student = User.query.filter_by(auth_level=1, id=student_id).first()
    if not this_student:
        return
        # return redirect(url_for('attendance.home'))

    user, error = auth_check(this_student.id)
    if error:
        return error

    report = StudentReport(this_student.id)
    return render_template("attendance/student.jinja2", student=this_student, report=report)
