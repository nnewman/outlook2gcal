import json

import pytest

from outlook2gcal.sync_component import SyncRunner

from .mocks import (
    MockAccount, MockConfiguration, MockServiceAccountCredentials, mock_build,
    random_gcal_event
)


@pytest.fixture
def sync_mocks(faker, mocker):
    mocker.patch('outlook2gcal.exchange_api.Configuration', MockConfiguration)
    mocker.patch('outlook2gcal.exchange_api.Account', MockAccount)
    mocker.patch(
        'outlook2gcal.google_api.ServiceAccountCredentials',
        MockServiceAccountCredentials
    )
    mocker.patch('outlook2gcal.google_api.build', mock_build)

    file_name = f'/tmp/{faker.pystr()}'
    with open(file_name, 'w') as fp:
        json.dump(
            {
                "type": "service_account",
                "project_id": "foobar",
                "private_key_id": "12345",
                "private_key": (
                    "-----BEGIN PRIVATE KEY-----\nABCDE\n-----END PRIVATE "
                    "KEY-----\n"
                ),
                "client_email": "account@foobar.iam.gserviceaccount.com",
                "client_id": "12345",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": (
                    "https://www.googleapis.com/oauth2/v1/certs"
                ),
                "client_x509_cert_url": (
                    "https://www.googleapis.com/robot/v1/metadata/x509/account"
                    "@foobar.iam.gserviceaccount.com"
                )
            },
            fp
        )
    return file_name


def test_sync_events_all_new(faker, sync_mocks):
    runner = SyncRunner(
        sync_mocks, faker.email(), faker.pystr(), 'www.example.com', '12345'
    )
    runner.sync_events()

    assert len(runner.google.service._events._events) == 3
