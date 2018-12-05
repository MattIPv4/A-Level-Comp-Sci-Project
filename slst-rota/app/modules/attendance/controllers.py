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


# Student overview
@attendance.route('/student/<int:student_id>', methods=['GET'])
def student(student_id: int):
    student = User.query.filter_by(id=student_id).first()
    if not student:
        return
        # return redirect(url_for('attendance.home'))

    user, error = auth_check(student.id)
    if error:
        return error

    data = [f for f in Assignment.query.filter_by(user_id=student.id).all() if not f.session.archived]
    breakdown = []

    # Totals data
    attendance_total = 0
    attendance_present = 0
    attendance_absent = 0
    attendance_in_diff = []
    attendance_in_on_time = 0
    attendance_out_diff = []
    attendance_out_on_time = 0
    attendance_table = []
    current_day = None

    # Compile assignment attendance data
    for assignment in data:
        this_attendance = [f for f in assignment.attendance if not f[1] or (f[1] and not f[1].current)]
        this_total = len(this_attendance)
        this_present = sum(1 for f in this_attendance if f[1])
        this_absent = this_total - this_present

        this_in_diff = [f[1].in_diff for f in this_attendance if f[1]]
        this_in_diff_avg = (sum(this_in_diff) / len(this_in_diff)) if this_in_diff else 0
        this_in_on_time = sum(1 for f in this_attendance if f[1] and f[1].in_diff < 1)

        this_out_diff = [f[1].out_diff for f in this_attendance if f[1]]
        this_out_diff_avg = (sum(this_out_diff) / len(this_out_diff)) if this_out_diff else 0
        this_out_on_time = sum(1 for f in this_attendance if f[1] and (not f[1].out_time or f[1].out_diff > -1))

        # Totals data
        attendance_total += this_total
        attendance_present += this_present
        attendance_absent += this_absent
        attendance_in_diff.extend(this_in_diff)
        attendance_in_on_time += this_in_on_time
        attendance_out_diff.extend(this_out_diff)
        attendance_out_on_time += this_out_on_time

        # Individual assignment data
        this = [this_total, this_present, this_absent,
                this_in_diff, this_in_diff_avg, this_in_on_time,
                this_out_diff, this_out_diff_avg, this_out_on_time]
        breakdown.append(this)

        # Day subheadings
        if assignment.session.day != current_day:
            attendance_table.append([False, [list(calendar.day_name)[assignment.session.day], "", "", ""]])
            current_day = assignment.session.day

        # Table breakdown
        attendance_table.append([
            False,
            [
                assignment.session.start_time_frmt,
                assignment.session.end_time_frmt,
                "{:.2f}% ({:,}/{:,})".format(
                    (this_present / this_total) * 100, this_present, this_total
                ) if this_total else "No attendance records",
                "In: {:,.0f} minute{} {} / Out: {:,.0f} minute{} {}"
                "<br/>In on time: {:.2f}% / Out on time: {:.2f}%".format(
                    abs(this_in_diff_avg),
                    Utils.unit_s(abs(this_in_diff_avg)),
                    "late" if this_in_diff_avg >= 0 else "early",

                    abs(this_out_diff_avg),
                    Utils.unit_s(abs(this_out_diff_avg)),
                    "late" if this_out_diff_avg > 0 else "early",

                    (this_in_on_time / this_total) * 100,
                    (this_out_on_time / this_total) * 100,
                ) if this_total else "No attendance records"
            ]
        ])

    attendance_in_diff_avg = (sum(attendance_in_diff) / len(attendance_in_diff)) if attendance_in_diff else 0
    attendance_out_diff_avg = (sum(attendance_out_diff) / len(attendance_out_diff)) if attendance_out_diff else 0

    attendance_stat = "No attendance records found for your user."
    punctuality_stat = "No attendance records found for your user."
    if attendance_total != 0:
        attendance_stat = "<b>{:.2f}%</b> - {:,}/{:,} assigned sessions attended ({:,} absent).".format(
            (attendance_present / attendance_total) * 100,
            attendance_present, attendance_total, attendance_absent
        )
        punctuality_stat = "<b>{:,.0f} minute{} {} sign in avg.</b> - Signed out {:,.0f} minute{} {} avg." \
                           "<br/><b>In on time (or early) {:.2f}%</b> - Out on time {:.2f}%".format(
            abs(attendance_in_diff_avg),
            Utils.unit_s(abs(attendance_in_diff_avg)),
            "late" if attendance_in_diff_avg >= 0 else "early",

            abs(attendance_out_diff_avg),
            Utils.unit_s(abs(attendance_out_diff_avg)),
            "late" if attendance_out_diff_avg > 0 else "early",

            (attendance_in_on_time / attendance_total) * 100,
            (attendance_out_on_time / attendance_total) * 100,
        )

    attendance_present = (attendance_present / attendance_total) * 100 if attendance_total else 0
    attendance_absent = (attendance_absent / attendance_total) * 100 if attendance_total else 0

    return render_template("attendance/student.jinja2", student=student, attendance_stat=attendance_stat,
                           punctuality_stat=punctuality_stat, attendance_table=attendance_table,
                           attendance_present=attendance_present, attendance_absent=attendance_absent)
