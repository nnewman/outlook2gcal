from time import sleep

from outlook2gcal.sync_component import SyncRunner

import secrets


if __name__ == '__main__':
    """
    Main runner. For each Exchange account, process events every 20 minutes
    """
    while True:
        for exchange_acct in secrets.EXCHANGE_ACCOUNTS:
            SyncRunner.sync(
                secrets.GOOGLE_SERVICE_ACCOUNT_FILE,
                exchange_acct['emailAddress'],
                exchange_acct['password'],
                exchange_acct['server'],
                exchange_acct['googleCalendarId']
            )
        sleep(1800)

