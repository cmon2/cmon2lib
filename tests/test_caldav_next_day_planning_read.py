import pytest
from unittest.mock import patch, MagicMock
from cmon2lib.ccaldav.caldav_next_day_planning_read import digest_schedule
from datetime import datetime, timedelta

@pytest.fixture
def mock_caldav_events():
    class MockEvent:
        def __init__(self, summary, start, end=None, location=None, description=None):
            class VEvent:
                def __init__(self, summary, start, end, location, description):
                    self.summary = MagicMock(value=summary)
                    self.dtstart = MagicMock(value=start)
                    self.dtend = MagicMock(value=end)
                    self.location = MagicMock(value=location)
                    self.description = MagicMock(value=description)
            self.vobject_instance = MagicMock(vevent=VEvent(summary, start, end, location, description))
    return MockEvent

@patch('cmon2lib.ccaldav.caldav_next_day_planning_read.DAVClient')
def test_digest_schedule_tomorrow_and_following_days(mock_davclient, mock_caldav_events):
    # Setup mock calendar and events
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    day_after = now + timedelta(days=2)
    two_days_after = now + timedelta(days=3)
    MockEvent = mock_caldav_events
    # Events for each day
    events = [
        MockEvent('Event Tomorrow', tomorrow.replace(hour=10), tomorrow.replace(hour=11), 'Room 1', 'Desc 1'),
        MockEvent('Event Day After', day_after.replace(hour=12), day_after.replace(hour=13), 'Room 2', 'Desc 2'),
        MockEvent('Event Two Days After', two_days_after.replace(hour=14), two_days_after.replace(hour=15), 'Room 3', 'Desc 3'),
    ]
    mock_calendar = MagicMock()
    mock_calendar.search.return_value = events
    mock_calendar.name = 'TestCal'
    mock_principal = MagicMock()
    mock_principal.calendars.return_value = [mock_calendar]
    mock_client = MagicMock()
    mock_client.principal.return_value = mock_principal
    mock_davclient.return_value = mock_client

    result = digest_schedule('url', 'user', 'pass')
    assert 'Event Tomorrow' in result
    assert 'Room 1' in result
    assert 'Desc 1' in result
    assert 'Event Day After' in result
    assert 'Event Two Days After' in result
    assert 'No events scheduled for tomorrow.' not in result

@patch('cmon2lib.ccaldav.caldav_next_day_planning_read.DAVClient')
def test_digest_schedule_no_events(mock_davclient):
    mock_calendar = MagicMock()
    mock_calendar.search.return_value = []
    mock_calendar.name = 'TestCal'
    mock_principal = MagicMock()
    mock_principal.calendars.return_value = [mock_calendar]
    mock_client = MagicMock()
    mock_client.principal.return_value = mock_principal
    mock_davclient.return_value = mock_client

    from cmon2lib.ccaldav import caldav_next_day_planning_read
    result = caldav_next_day_planning_read.digest_schedule('url', 'user', 'pass')
    assert 'No events scheduled for tomorrow.' in result
    assert 'No events.' in result

@patch('cmon2lib.ccaldav.caldav_next_day_planning_read.DAVClient')
def test_digest_schedule_error_handling(mock_davclient):
    mock_davclient.side_effect = Exception('Connection failed')
    from cmon2lib.ccaldav import caldav_next_day_planning_read
    result = caldav_next_day_planning_read.digest_schedule('url', 'user', 'pass')
    assert 'Could not retrieve schedule.' in result
