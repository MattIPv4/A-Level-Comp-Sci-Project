import calendar  # Calendar

from flask import Blueprint, redirect, url_for, render_template  # Flask

from app import error_render, Utils, db_session  # DB, Errors, Utils
from app.modules import auth  # Auth
from app.modules.auth.models import User  # User
from app.modules.student.models import Assignment, Attendance  # Rota Sessions

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
                self.__attendance_table.append([
                    False, [list(calendar.day_name)[assignment.session.day], "", "", ""], True])
                self.__current_day = assignment.session.day

            # Table: Assignment
            self.__attendance_table.append(data.table)

        # Calculate overall tardiness
        self.__attendance_in_diff_avg = (sum(self.__attendance_in_diff) / len(self.__attendance_in_diff)) \
            if self.__attendance_in_diff else 0
        self.__attendance_out_diff_avg = (sum(self.__attendance_out_diff) / len(self.__attendance_out_diff)) \
            if self.__attendance_out_diff else 0

        # Default word-y stats
        self.__attendance_stat = "No attendance records found."
        self.__punctuality_stat = "No attendance records found."

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
        self.attendance_present = (self.__attendance_present / self.__attendance_total) * 100 \
            if self.__attendance_total else 0
        self.attendance_absent = (self.__attendance_absent / self.__attendance_total) * 100 \
            if self.__attendance_total else 0

        # Attendance bar
        self.attendance_bar = "<div class=\"stat-bar\">" \
                              "<span class=\"success\" style=\"width: {}%;\"></span>" \
                              "<span class=\"danger\" style=\"width: {}%;\"></span>" \
                              "</div>".format(self.attendance_present,
                                              self.attendance_absent if self.attendance_absent else 0)

        # Store into class
        self.attendance = self.__attendance_stat
        self.punctuality = self.__punctuality_stat
        self.punctuality_in_raw = self.__attendance_in_diff_avg
        self.present = self.__attendance_present
        self.absent = self.__attendance_absent
        self.table = self.__attendance_table


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
                [this_student.username] * 2,
                [report.attendance_bar + "\n" + report.attendance, report.attendance_present],
                [report.punctuality, report.punctuality_in_raw],
                "<a href=\"{}\" class=\"button primary\"><i class=\"fas fa-lg fa-clipboard-list\"></i> View full report"
                "</a>".format(url_for("attendance.student", student_id=this_student.id))
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

    # Generate chart
    chart = []
    for data in session_data.values():
        value = data[1] / data[2] * 100 if data[2] else 0
        chart.append({
            "label": "{0.day_frmt} {0.start_time_frmt}-{0.end_time_frmt}".format(data[0]),
            "y": value,
            "toolTipContent": "<span style='\"'color: {{color}};'\"'>{{label}}</span>: {:.2f}%".format(value)
        })

    return render_template("attendance/home.jinja2", attendance_table=table,
                           session_attendnace=[{"type": "column", "dataPoints": chart}],
                           chart_extras={"axisY": {"minimum": 0, "maximum": 100, "suffix": "%"}})


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

    # Fetch report
    report = StudentReport(this_student.id)

    # Generate graph data
    graph = [{
        "type": "scatter",
        "legendText": "Sign in difference average (minutes)",
        "showInLegend": True,
        "dataPoints": []
    }, {
        "type": "scatter",
        "legendText": "Sign out difference average (minutes)",
        "showInLegend": True,
        "dataPoints": []
    }]
    for assignment in report.breakdown:
        label = "{0.day_frmt} {0.start_time_frmt}-{0.end_time_frmt}".format(assignment.assignment.session)
        # In time diff
        graph[0]["dataPoints"].append({"label": label, "y": assignment.in_diff_avg, "markerSize": 20,
                                       "toolTipContent": "{{label}}: Signed in {:,.2f} mins {}".format(
                                           abs(assignment.in_diff_avg),
                                           "late" if assignment.in_diff_avg > 0 else "early")})
        # Out time diff
        graph[1]["dataPoints"].append({"label": label, "y": -assignment.out_diff_avg, "markerSize": 15,
                                       "toolTipContent": "{{label}}: Signed out {:,.2f} mins {}".format(
                                           abs(assignment.out_diff_avg),
                                           "late" if assignment.out_diff_avg > 0 else "early")})

    return render_template("attendance/student.jinja2", student=this_student, report=report, graph=graph,
                           graph_extra={"axisY": {"title": "Minutes difference (average)", "titleFontSize": 15}})


# Generate attendance test data based on current assignments
@attendance.route('/test', methods=['GET'])
def test():
    import random
    students = User.query.filter_by(auth_level=1, disabled=0).all()
    # Work over each student in the system
    for this_student in students:
        # Get report to find all assignments
        report = StudentReport(this_student.id)
        for assignment in report.breakdown:
            # Loop over each attendance record in assignment
            for att in assignment.attendance:
                # If has attendance already ignore
                if not att[1]:
                    # Decide if should have attended (2/3)
                    if random.randint(0, 2) != 0:
                        # Create attendance from session
                        session = db_session()
                        att_entry = Attendance.from_session(this_student.id, assignment.assignment.session)

                        # Override today's date with attendance date
                        att_entry.date = att[0]

                        # Set the in_time, make early/late for 1/4
                        in_offset = 0
                        if random.randint(0, 3) == 0:
                            in_offset = random.randint(-5, min(15, int(
                                assignment.assignment.session.end_time - assignment.assignment.session.start_time)))
                        in_offset += random.random() * 2 - 1  # float between -1 and 1
                        att_entry.in_time = Utils.minutes_date(att[0],
                                                               assignment.assignment.session.start_time + in_offset)
                        att_entry.in_time_org = Utils.minutes_date(att[0], assignment.assignment.session.start_time)

                        # Set the out_time, make early sign out for 1/4
                        out_offset = 0
                        if random.randint(0, 3) == 0:
                            out_offset = random.randint(-min(15, int(
                                assignment.assignment.session.end_time - assignment.assignment.session.start_time)), 0)
                        att_entry.out_time = Utils.minutes_date(att[0],
                                                                assignment.assignment.session.end_time + out_offset)
                        att_entry.out_time_org = Utils.minutes_date(att[0], assignment.assignment.session.end_time)

                        # Save
                        session.add(att_entry)
                        session.commit()

    return redirect(url_for('attendance.home'))
