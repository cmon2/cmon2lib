"""
cCalDav.cal_utils

This module will expose functions to interact with a CalDav calendar.
"""

from caldav import DAVClient
from cmon2lib.utils.cmon_logging import clog

def list_calendars_for_user(url, username, password):
    """
    List all calendars for a user using the CalDav server URL and credentials.

    Args:
        url (str): The CalDav server URL.
        username (str): The username for authentication.
        password (str): The password for authentication.

    Returns:
        list: A list of calendar objects for the user.
    """
    clog('info', f"Connecting to CalDav server at {url} as {username}")
    client = DAVClient(url, username=username, password=password)
    principal = client.principal()
    calendars = principal.calendars()
    clog('info', f"Found {len(calendars)} calendars for user {username}")
    return calendars

def list_events_next_10_days(calendar):
    """
    List all events in the next 10 days for a given calendar.

    Args:
        calendar: A caldav Calendar object.

    Returns:
        list: A list of event objects occurring in the next 10 days.
    """
    from datetime import datetime, timedelta, date
    try:
        now = datetime.now()
        ten_days_later = now + timedelta(days=10)
        try:
            events_fetched = calendar.search(
                start=now,
                end=ten_days_later,
                event=True,
                expand=True,
            )
            clog('info', f"Found {len(events_fetched)} events in the next 10 days for calendar {getattr(calendar, 'name', repr(calendar))}")
            return events_fetched
        except Exception as e:
            if 'VCARD and VCALENDAR' in str(e):
                clog('warning', f"Skipping non-calendar resource: {getattr(calendar, 'name', repr(calendar))} (not a VCALENDAR)")
            else:
                clog('error', f"Error fetching events for next 10 days: {e}")
            return []
    except Exception as e:
        clog('error', f"Unexpected error in list_events_next_10_days: {e}")
        return []

if __name__ == "__main__":
    import os
    CALDAV_URL = os.environ.get("CALDAV_URL")
    CALDAV_USERNAME = os.environ.get("CALDAV_USERNAME")
    CALDAV_PASSWORD = os.environ.get("CALDAV_PASSWORD")
    if not (CALDAV_URL and CALDAV_USERNAME and CALDAV_PASSWORD):
        clog('error', "Please set CALDAV_URL, CALDAV_USERNAME, and CALDAV_PASSWORD environment variables.")
    else:
        try:
            calendars = list_calendars_for_user(CALDAV_URL, CALDAV_USERNAME, CALDAV_PASSWORD)
            for cal in calendars:
                clog('info', f"Calendar: {getattr(cal, 'name', repr(cal))}")
                events = list_events_next_10_days(cal)
                for event in events:
                    try:
                        vevent = event.vobject_instance.vevent
                        summary = getattr(vevent, 'summary', None)
                        start = getattr(vevent, 'dtstart', None)
                        clog('info', f"Event: {summary.value if summary else 'No summary'} at {start.value if start else 'No start'}")
                    except Exception as e:
                        clog('warning', f'Could not parse event details: {e}')
        except Exception as e:
            clog('error', f"Error listing calendars or events: {e}")
