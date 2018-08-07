from gerridae.models import Meter


def init_app(app):
    default_meters = app.config["DEFAULT_METERS"]

    for meter_id in default_meters:
        default_meter = default_meters[meter_id]
        meter = Meter(id=meter_id)
        if default_meter:
            meter.email = default_meter["email"]
            meter.owner = default_meter["owner"]
        meter.put()
