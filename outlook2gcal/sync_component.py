from time import sleep

import arrow
from exchangelib import UTC_NOW, UTC, EWSDateTime
from tzlocal.windows_tz import win_tz

from .exchange_api import ExchangeApiClient
from .google_api import GoogleCalendarApiClient


class SyncRunner:
    """Class for tying together code related to synchronization"""

    def __init__(self, gcal_creds, email, password, server, calendar_id):
        """
        Initialize the synchronization class.

        Args:
            gcal_creds (str): Path to Google service account credentials file
            email (str): Email address of the Microsoft Exchange account from
                which the events will be synchronized
            password (str): Password for the Microsoft Exchange account
            server (str): Server for the Microsoft Exchange account
            calendar_id (str): Google Calendar ID for the calendar to which
                the events will be synchronized
        """
        self.exchange = ExchangeApiClient(email, password, server)
        self.google = GoogleCalendarApiClient(
            gcal_creds,
            scopes='https://www.googleapis.com/auth/calendar'
        )
        self.calendar_id = calendar_id

    def _get_exchange_events(self, sync_all=False):
        """
        Getter for events from the Exchange mailbox. Filters for events
        after the current time.
        """
        start = UTC_NOW()
        if sync_all:
            start = EWSDateTime(day=1, month=1, year=1970, tzinfo=UTC)

        return self.exchange.get_events().filter(
            start__gte=start
        ).order_by('start')

    def _get_google_events(self):
        """
        Getter for events from the Google calendar. This is for comparing
        existing events in Google in order to compare and deduplicate
        """
        return self.google.get_events(self.calendar_id)

    @staticmethod
    def _event_is_ews_event(event):
        """
        Helper function to determine if an event from the Google Calendar is
        from Exchange based on whether a private extended property is set for
        EWS attributed, i.e. ID and Change Key

        Args:
            event (dict): Google Calendar event

        Returns:
            bool: Whether a private extended property is set for the EWS ID
        """
        return bool(
            event.get('extendedProperties', {}).get('private', {}).get('ewsId')
        )

    @staticmethod
    def _get_recurrence(event):
        """
        Format recurrence from an Exchange calendar event based on it's iCal
        object.

        The event doesn't give back the recurrence in a standard RFC5545
        format. This function inspects the MIME content from the event and
        crudely parses our the recurrence rules. It also translates the
        timezones from the EXDATE objects from Windows-based timezones to
        UNIX-compatible timezones.

        Args:
            event (exchangelib.CalendarItem): Exchange event

        Returns:
            list[str]: List of RFC5545-compliant recurrence rules for the event
        """
        recurrence = [
            _ for _ in filter(
                lambda x: 'RRULE' in x or 'RDATE' in x or 'EXDATE' in x,
                event.mime_content.decode('utf-8').split('\r\n')
            )
        ]

        idxs_to_pop = []
        for idx, rec in enumerate(recurrence):
            if rec.startswith('EXDATE;TZID='):
                rec = rec.split(',')[0]
                tz_string = rec.replace('EXDATE;TZID=', '').split(':')[0]
                try:
                    new_tz_string = win_tz[tz_string]
                    recurrence[idx] = rec.replace(tz_string, new_tz_string)
                except KeyError:
                    # @TODO: Make better handling for this case
                    idxs_to_pop.append(idx)
        for _ in idxs_to_pop:
            recurrence.pop(_)

        return recurrence

    def get_event_attrs(self, events):
        """
        Produces a simple data structure to use in:
          * Comparisons of EWS Change Keys with existing change keys
          * Lookups of whether or not Exchange events exist in Google Calendar
              as referenced by EWS ID
          * Lookups of Google event IDs so that existing events that need
              updates perform the update on the existing event

        Args:
            events (list[dict]): List of Google Calendar events

        Returns:
            dict: Data structure for event property comparisons and lookups
        """
        event_dict = {}
        for event in events:
            if self._event_is_ews_event(event):
                event_dict[event['extendedProperties']['private']['ewsId']] = {
                    'ewsId': event['extendedProperties']['private']['ewsId'],
                    'ewsChangeKey': (
                        event['extendedProperties']['private']['ewsChangeKey']
                    ),
                    'googleEventId': event['id']
                }
        return event_dict

    def _format_event_props(self, event):
        """
        Helper function to extract important attributes from an Exchange event

        Args:
            event (exchangelib.CalendarItem): Exchange event

        Returns:
            dict: Set of attributes from the event as they would be applied to
                `GoogleCalendarApiClient` functions `create_event` and
                `update_event`
        """
        return {
            'name': event.subject,
            'location': event.location,
            'body': event.text_body,
            'start': arrow.get(event.start, tzinfo='UTC'),
            'end': arrow.get(event.end, tzinfo='UTC'),
            'ews_id': event.id,
            'change_key': event.changekey,
            'recurrence': self._get_recurrence(event),
        }

    def sync_events(self):
        """
        Perform synchronization of the Exchange events to the Google Calendar
        """
        events = self._get_exchange_events()
        event_attrs = self.get_event_attrs(self._get_google_events())

        for event in events:
            if event.id not in event_attrs:
                self.google.create_event(
                    self.calendar_id,
                    **self._format_event_props(event)
                )
            elif event.changekey != event_attrs[event.id]['ewsChangeKey']:
                self.google.update_event(
                    event_attrs[event.id]['googleEventId'],
                    self.calendar_id,
                    **self._format_event_props(event)
                )
            sleep(0.1)

    @classmethod
    def sync(cls, gcal_creds, email, password, server, calendar_id):
        """
        Class method for initiating a synchronization of an Exchange calendar
        to a Google Calendar

        Args:
            gcal_creds (str): Path to Google service account credentials file
            email (str): Email address of the Microsoft Exchange account from
                which the events will be synchronized
            password (str): Password for the Microsoft Exchange account
            server (str): Server for the Microsoft Exchange account
            calendar_id (str): Google Calendar ID for the calendar to which
                the events will be synchronized
        """
        klass = cls(gcal_creds, email, password, server, calendar_id)
        klass.sync_events()
