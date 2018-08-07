import logging

from flask import current_app, render_template
from flask_babel import gettext, format_date

from google.appengine.api import mail


def send_reminder(period, reading):
    meter_email = reading.meter.email
    if not meter_email:
        logging.warn("Email missing for meter '%s'" % reading.meter_id)
        return False

    message = mail.EmailMessage(
        sender=current_app.config["REMINDER_EMAIL_SENDER"],
        subject=current_app.config["REMINDER_SUBJECT"] + " " + format_date(period.end),
        to=meter_email,
    )

    message.body = render_template("email/reminder.txt", reading=reading)
    message.html = render_template("email/reminder.html", reading=reading)

    message.send()

    logging.info("Reminder sent to '%s'" % meter_email)
    return True
