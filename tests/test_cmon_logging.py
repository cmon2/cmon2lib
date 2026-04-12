import pytest
from cmon2lib.utils.cmon_logging import clog


def test_clog_info_logs_message(capsys):
    """Test that clog('info', ...) produces output containing the message."""
    clog("info", "test info message")
    captured = capsys.readouterr()
    # Loguru outputs to stderr
    assert "test info message" in captured.err


def test_clog_warning_logs_message(capsys):
    """Test that clog('warning', ...) produces output containing the message."""
    clog("warning", "test warning message")
    captured = capsys.readouterr()
    assert "test warning message" in captured.err


def test_clog_invalid_level_warns_and_logs(capsys):
    """Test that invalid log level defaults to WARNING with notification."""
    clog("notalevel", "should warn about invalid level")
    captured = capsys.readouterr()
    assert "Invalid log level" in captured.err
    assert "should warn about invalid level" in captured.err


def test_clog_args_and_kwargs(capsys):
    """Test that clog supports format arguments."""
    clog("info", "value: {}", 42)
    captured = capsys.readouterr()
    assert "value: 42" in captured.err


def test_clog_with_exception(capsys):
    """Test that clog with exception includes exception type and message."""
    try:
        raise ValueError("test error")
    except ValueError as e:
        clog("error", "Operation failed", exception=e)
    captured = capsys.readouterr()
    assert "Operation failed" in captured.err
    assert "ValueError" in captured.err
    assert "test error" in captured.err


def test_clog_format_with_args(capsys):
    """Test that clog supports multiple format arguments."""
    clog("info", "User {} logged in from {}", "alice", "192.168.1.1")
    captured = capsys.readouterr()
    assert "User alice logged in from 192.168.1.1" in captured.err


def test_clog_includes_user(capsys):
    """Test that clog output includes the user field."""
    import os

    expected_user = os.getenv("USER") or os.getenv("USERNAME") or "unknown"
    clog("info", "simple message")
    captured = capsys.readouterr()
    assert expected_user in captured.err
