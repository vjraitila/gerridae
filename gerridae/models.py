import hashlib
import uuid
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from flask import url_for

from google.appengine.ext import ndb


class ReportPeriod:
    def __init__(self, d):
        self.start = date(d.year, (d.month - 1) // 3 * 3 + 1, 1)
        self.end = self.start + relativedelta(months=3, days=-1)

    @property
    def id(self):
        return self.end.strftime("%Y%m%d")

    @property
    def key(self):
        return ndb.Key(self.__class__.__name__, self.id)

    @property
    def next(self):
        return ReportPeriod(self.end + relativedelta(days=1))

    @property
    def prev(self):
        return ReportPeriod(self.start + relativedelta(days=-1))

    @classmethod
    def get_current(cls):
        return cls(date.today())

    @classmethod
    def get_by_id(cls, period_id):
        d = datetime.strptime(period_id, "%Y%m%d").date()
        return cls(d)


class Meter(ndb.Model):
    email = ndb.StringProperty()
    owner = ndb.StringProperty()


class MeterReading(ndb.Model):
    meter_key = ndb.KeyProperty(kind=Meter)
    meter_read = ndb.DateTimeProperty(indexed=False)
    meter_value = ndb.IntegerProperty(indexed=False)
    reminded_last = ndb.DateTimeProperty(indexed=False)
    reminder_count = ndb.IntegerProperty(indexed=False, default=0)
    salt_bytes = ndb.BlobProperty(indexed=False)
    url_hash = ndb.StringProperty()

    @property
    def period_id(self):
        return self.key.parent().id()

    @property
    def completed(self):
        return self.meter_value is not None

    @property
    def meter(self):
        return self.meter_key.get()

    @property
    def meter_id(self):
        return self.meter_key.id()

    @property
    def url(self):
        return url_for("reading.index", reading_hash=self.url_hash, _external=True)

    def mark_as_reminded(self):
        self.reminder_count = self.reminder_count + 1
        self.reminded_last = datetime.now()
        self.put()

    def mark_as_read(self, meter_value):
        self.meter_value = meter_value
        self.meter_read = datetime.now()
        self.put()

    @classmethod
    def init(cls, period_id):
        period_key = ReportPeriod.get_by_id(period_id).key
        meter_keys = Meter.query().fetch(keys_only=True)
        for meter_key in meter_keys:
            key_name = period_id + "|" + meter_key.id()
            salt = uuid.uuid4()
            url_hash = hashlib.sha256(key_name + salt.hex).hexdigest()
            r = cls(
                parent=period_key,
                meter_key=meter_key,
                url_hash=url_hash,
                salt_bytes=salt.bytes,
                id=key_name,
            )
            r.put()

    @classmethod
    def find_by_period(cls, period_id):
        period_key = ReportPeriod.get_by_id(period_id).key
        query = cls.query(ancestor=period_key)  # .order(cls.meter_id)
        return query.fetch()

    @classmethod
    def get_by_hash(cls, reading_hash):
        query = cls.query(cls.url_hash == reading_hash)
        return query.get()
