
from exchangelib import DELEGATE, Account, ServiceAccount, Configuration


class ExchangeApiClient:
    """Client for Exchange API"""

    def __init__(self, email, password, server):
        """Initialize a connection to an Exchange server"""

        credentials = ServiceAccount(username=email, password=password)
        config = Configuration(server=server, credentials=credentials)

        # Set up a target account and do an autodiscover lookup to find the
        # target EWS endpoint.
        self.account = Account(
            primary_smtp_address=email,
            credentials=credentials,
            config=config,
            autodiscover=False,
            access_type=DELEGATE
        )

    def get_events(self):
        """Get all events in a given mailbox calendar"""
        return self.account.calendar.all()
