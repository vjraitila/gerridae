from datetime import datetime

from flask import render_template, abort, request

from gerridae.reading import bp
from gerridae.models import MeterReading


@bp.route("/<reading_hash>", methods=["GET", "POST"])
def index(reading_hash):
    reading = MeterReading.get_by_hash(reading_hash)
    if not reading:
        abort(404)

    if request.method == "POST":
        meter_value = int(request.form.get("meter_value"))
        reading.mark_as_read(meter_value)

    readings = MeterReading.find_by_period(reading.period_id)

    return render_template("reading/index.html", reading=reading, readings=readings)
