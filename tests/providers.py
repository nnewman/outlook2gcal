import arrow
from faker import Faker


faker = Faker()


class Event:
    def __init__(self, id, subject, location, text_body, start, end, changekey,
                 mime_content):
        self.id = id
        self.subject = subject
        self.location = location
        self.text_body = text_body
        self.start = start
        self.end = end
        self.changekey = changekey
        self.mime_content = mime_content


def random_exchange_event():
    start_date = arrow.get(faker.future_datetime(end_date='+30d'))
    end_date = arrow.get(start_date.isoformat()).replace(hour=+1)

    if faker.pybool():
        mime_content = b"""
            RRULE\r\nRDATE\r\nEXDATE;TZID=Eastern Standard Time:12345
        """
    else:
        mime_content = b""

    return Event(
        id=faker.pystr(min_chars=None, max_chars=20),
        subject=faker.catch_phrase(),
        location=faker.address(),
        text_body=faker.sentence(),
        start=start_date,
        end=end_date,
        changekey=faker.pystr(min_chars=None, max_chars=20),
        mime_content=mime_content
    )


def random_gcal_event(ewsId, ewsChangeKey):
    event = {
        'id': faker.pystr(min_chars=None, max_chars=20),
    }

    if ewsId and ewsChangeKey:
        event['extendedProperties'] = {
            'private': {
                'ewsId': ewsId,
                'ewsChangeKey': ewsChangeKey
            }
        }

    return event
