import datetime
from urllib3.exceptions import NewConnectionError, MaxRetryError

import arrow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from requests.exceptions import ConnectionError


def format_exceptions_errors(exc):
    if hasattr(exc, 'args') and len(exc.args):
        return ';'.join([str(_) for _ in exc.args])


class _GoogleApiClient:
    """Generic base for a Google API Client using service accounts"""

    service_type = None
    service_version = None

    def __init__(self, credential_file, scopes):
        """Initialize the service and save it to the class"""
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credential_file,
            scopes=scopes
        )

        self.service = build(
            self.service_type,
            self.service_version,
            http=credentials.authorize(Http())
        )


class GoogleCalendarApiClient(_GoogleApiClient):
    """Use the Generic API client for calendar operations"""

    service_type = 'calendar'
    service_version = 'v3'

    def get_events(self, calendar_id, time_min=None, time_max=None):
        """
        Get all events for a given calendar.

        Args:
            calendar_id (str): Google Calendar ID to query
            time_min (datetime.datetime, None): Earliest event time
            time_max (datetime.datetime, None): Latest event time

        Returns:
             list[dict]: Events from the calendar
        """
        event_set = []

        current_dt = datetime.datetime.utcnow()

        if not time_min:
            time_min = current_dt.isoformat() + 'Z'

        if not time_max:
            next_month = arrow.get(time_min).shift(months=+1).naive
            time_max = next_month.isoformat() + 'Z'

        page_token = None

        while True:

            events = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=100,
                singleEvents=True,
                pageToken=page_token,
            ).execute()

            event_set += events.get('items', [])

            page_token = events.get('nextPageToken')

            if not page_token:
                break

        return event_set

    def create_event(self, calendar_id, name, location, body, start, end,
                     ews_id=None, change_key=None, recurrence=None):
        """
        Create an event on a given calendar.

        Args:
            calendar_id (str): Google Calendar ID to query
            name (str): Event name
            location (str): Location string for the event
            body (str): Text for event body
            start (arrow.arrow.Arrow): UTC date-time for event start
            end (arrow.arrow.Arrow): UTC date-time for event end
            ews_id (str|None): ID in Exchange for this event
            change_key (str|None): Unique revision ID in Exchange
            recurrence (list[str]): Recurrence strings in RFC5545 spec

        Returns:
            dict: Event as put into calendar
        """

        event = {
            'summary': name,
            'location': location,
            'description': body,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': 'UTC',
            },
            "extendedProperties": {
                "private": {
                    'ewsId': ews_id,
                    'ewsChangeKey': change_key,
                }
            }
        }

        if recurrence:
            event['recurrence'] = recurrence

        try:
            return self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
        except HttpError as exc:
            print('Google HTTP Error')
            print(exc.__class__.__name__)
            print(format_exceptions_errors(exc))
        except (MaxRetryError, NewConnectionError, ConnectionError) as exc:
            print('Request/Connection Error')
            print(exc.__class__.__name__)
            print(format_exceptions_errors(exc))

    def update_event(self, event_id, calendar_id, name, location, body, start,
                     end, ews_id=None, change_key=None, recurrence=None):
        """
        Update an event on a given calendar as specified by ID

        Args:
            event_id (str): Google ID for the event
            calendar_id (str): Google Calendar ID to query
            name (str): Event name
            location (str): Location string for the event
            body (str): Text for event body
            start (arrow.arrow.Arrow): UTC date-time for event start
            end (arrow.arrow.Arrow): UTC date-time for event end
            ews_id (str|None): ID in Exchange for this event
            change_key (str|None): Unique revision ID in Exchange
            recurrence (list[str]): Recurrence strings in RFC5545 spec

        Returns:
            dict: Event as put into calendar
        """

        event = {
            'summary': name,
            'location': location,
            'description': body,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': 'UTC',
            },
            "extendedProperties": {
                "private": {
                    'ewsId': ews_id,
                    'ewsChangeKey': change_key,
                }
            }
        }

        if recurrence:
            event['recurrence'] = recurrence

        try:
            return self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=body
            ).execute()
        except HttpError as exc:
            print('Google HTTP Error')
            print(exc.__class__.__name__)
            print(format_exceptions_errors(exc))
        except (MaxRetryError, NewConnectionError, ConnectionError) as exc:
            print('Request/Connection Error')
            print(exc.__class__.__name__)
            print(format_exceptions_errors(exc))
