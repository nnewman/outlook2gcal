# Outlook2GCal

A tool for syncing an Exchange-based calendar into a Google-based calendar.

## Requirements

* Google service account credentials (with Calendar API enabled)
* An Exchange or Office 365 Business/Enterprise account
* A Google account with calendar
* Your Google service accound address added to the Google calendar's 
  sharing list, with full access permission

## Usage

```bash
$ cp secrets.dist.py secrets.py
```

Fill in `secrets.py` with your Google service account credentials, and 
Exchange credentials and Google calendar ID.

```bash
$ python sync.py
````


