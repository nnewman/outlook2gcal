from .providers import random_exchange_event, random_gcal_event


class MockCalendarFilteredEventList:

    _ordered_event_list = [
        random_exchange_event()
        for _ in range(0, 3)
    ]

    def order_by(self, filter_kwarg):
        return self._ordered_event_list


class MockCalendarEventList:

    _filtered_event_list = MockCalendarFilteredEventList()

    def filter(self, **kwargs):
        return self._filtered_event_list


class MockCalendar:

    _event_list = MockCalendarEventList()

    def all(self):
        return self._event_list


class MockAccount:

    _calendar = MockCalendar()

    def __init__(self, primary_smtp_address, credentials, config, autodiscover,
                 access_type):
        pass

    @property
    def calendar(self):
        return self._calendar


# class MockServiceAccount:
#     def __init__(self, username, password):
#         pass


class MockConfiguration:
    def __init__(self, server, credentials):
        pass


class MockServiceAccountCredentials:

    @classmethod
    def from_json_keyfile_name(cls, credential_file, scopes):
        return cls()

    def authorize(self, http):
        return


class GenericExecuteInterface:
    def __init__(self, things_to_return=None):
        self.things = things_to_return

    def execute(self):
        return {'items': self.things}


class EventInterface:

    _events = []

    def list(self, *args, **kwargs):
        return GenericExecuteInterface(self._events)

    def insert(self, calendarId, body):
        self._events.append(
            random_gcal_event(
                ewsId=body['extendedProperties']['private']['ewsId'],
                ewsChangeKey=(
                    body['extendedProperties']['private']['ewsChangeKey']
                )
            )
        )
        return GenericExecuteInterface()

    def update(self, eventId, calendarId, body):
        for idx, event in enumerate(self._events):
            if event['id'] == eventId:
                self._events[idx]['extendedProperties']['private']['ewsId'] = (
                    body['extendedProperties']['private']['ewsId']
                )
                self._events[idx]['extendedProperties']['private']['ewsChangeKey'] = (
                    body['extendedProperties']['private']['ewsChangeKey']
                )
        return GenericExecuteInterface()


class MockService:

    def __init__(self):
        self._events = EventInterface()

    def events(self):
        return self._events


def mock_build(service_type, service_version, http):
    return MockService()

