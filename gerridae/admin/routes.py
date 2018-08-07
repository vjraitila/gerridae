from datetime import datetime

from flask import render_template, request, abort, redirect, url_for
from google.appengine.api import users

from gerridae.admin import bp
from gerridae.email import send_reminder
from gerridae.models import MeterReading, ReportPeriod


@bp.before_request
def restrict_bp_to_admins():
    if not users.is_current_user_admin():
        return redirect(users.create_login_url(request.url))


@bp.route("/readings")
def get_readings():
    period_id = request.args.get("p")
    if not period_id:
        period = ReportPeriod.get_current()
    else:
        period = ReportPeriod.get_by_id(period_id)

    readings = MeterReading.find_by_period(period.id)

    return render_template("admin/readings.html", period=period, readings=readings)


@bp.route("/readings/init", methods=["POST"])
def init_readings():
    period_id = request.form.get("p")

    if not period_id:
        abort(400)

    MeterReading.init(period_id)

    return redirect(url_for(".get_readings", p=period_id))


@bp.route("/readings/remind", methods=["POST"])
def send_reminders():
    period_id = request.form.get("p")

    if not period_id:
        abort(400)

    period = ReportPeriod.get_by_id(period_id)
    reading_hashes = request.form.getlist("reading_hashes")

    for reading_hash in reading_hashes:
        reading = MeterReading.get_by_hash(reading_hash)
        if not reading.completed:
            sent = send_reminder(period, reading)
            if sent:
                reading.mark_as_reminded()

    return redirect(url_for(".get_readings", p=period_id))
