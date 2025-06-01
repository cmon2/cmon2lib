"""
This module will expose a function that reads all events for a user relevant for
planning the next day and format it to a natural language representation that is optimised
for providing this information to an ai assistant.
"""

from caldav import DAVClient
from cmon2lib.utils.cmon_logging import clog
from datetime import datetime, timedelta

def digest_schedule(url, username, password):
    """
    Returns a natural language digest of the user's schedule:
    - All details for events on the next day (tomorrow)
    - Only summary for events on the two following days
    Args:
        url (str): CalDav server URL
        username (str): CalDav username
        password (str): CalDav password
    Returns:
        str: Natural language summary of the schedule
    """
    try:
        client = DAVClient(url, username=username, password=password)
        principal = client.principal()
        calendars = principal.calendars()
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        day_after = now + timedelta(days=2)
        two_days_after = now + timedelta(days=3)
        events_tomorrow = []
        events_day_after = []
        events_two_days_after = []
        for cal in calendars:
            try:
                # Get all events for the next 3 days
                events = cal.search(
                    start=tomorrow.replace(hour=0, minute=0, second=0, microsecond=0),
                    end=two_days_after.replace(hour=23, minute=59, second=59, microsecond=999999),
                    event=True,
                    expand=True,
                )
                for event in events:
                    try:
                        vevent = event.vobject_instance.vevent
                        summary = getattr(vevent, 'summary', None)
                        start = getattr(vevent, 'dtstart', None)
                        end = getattr(vevent, 'dtend', None)
                        location = getattr(vevent, 'location', None)
                        description = getattr(vevent, 'description', None)
                        # Normalize start date
                        event_start = start.value if start else None
                        if not event_start:
                            continue
                        # Determine which day
                        if event_start.date() == tomorrow.date():
                            events_tomorrow.append({
                                'summary': summary.value if summary else 'No summary',
                                'start': str(event_start),
                                'end': str(end.value) if end else '',
                                'location': location.value if location else '',
                                'description': description.value if description else '',
                                'calendar': getattr(cal, 'name', repr(cal)),
                            })
                        elif event_start.date() == day_after.date():
                            events_day_after.append(summary.value if summary else 'No summary')
                        elif event_start.date() == two_days_after.date():
                            events_two_days_after.append(summary.value if summary else 'No summary')
                    except Exception as e:
                        clog('warning', f'Could not parse event details: {e}')
            except Exception as e:
                if 'VCARD and VCALENDAR' in str(e):
                    clog('warning', f"Skipping non-calendar resource: {getattr(cal, 'name', repr(cal))} (not a VCALENDAR)")
                else:
                    clog('error', f"Error fetching events: {e}")
        # Format output
        lines = []
        lines.append(f"The users planned schedule for tomorrow, {tomorrow.strftime('%A, %B %d, %Y')}:\n")
        if events_tomorrow:
            for ev in events_tomorrow:
                lines.append(f"- {ev['summary']}\n  Time: {ev['start']} - {ev['end']}\n  Location: {ev['location']}\n  Description: {ev['description']}\n  Calendar: {ev['calendar']}\n")
        else:
            lines.append("No events scheduled for tomorrow.\n")
        lines.append(f"The following is supplementary information that you shall only use when it has influence on the planning for tomorrow:")
        lines.append(f"\nEvents in 2 days:")
        if events_day_after:
            for s in events_day_after:
                lines.append(f"- {s}")
        else:
            lines.append("No events.")
        lines.append(f"\nEvents in 3 days:")
        if events_two_days_after:
            for s in events_two_days_after:
                lines.append(f"- {s}")
        else:
            lines.append("No events.")
        return "\n".join(lines)
    except Exception as e:
        clog('error', f"Error in digest_schedule: {e}")
        return "Could not retrieve schedule."

if __name__ == "__main__":
    import os
    CALDAV_URL = os.environ.get("CALDAV_URL")
    CALDAV_USERNAME = os.environ.get("CALDAV_USERNAME")
    CALDAV_PASSWORD = os.environ.get("CALDAV_PASSWORD")
    if not (CALDAV_URL and CALDAV_USERNAME and CALDAV_PASSWORD):
        clog('error', "Please set CALDAV_URL, CALDAV_USERNAME, and CALDAV_PASSWORD environment variables.")
    else:
        try:
            schedule_digest = digest_schedule(CALDAV_URL, CALDAV_USERNAME, CALDAV_PASSWORD)
            clog('info', f"Schedule digest:\n{schedule_digest}")
        except Exception as e:
            clog('error', f"Error generating schedule digest: {e}")
