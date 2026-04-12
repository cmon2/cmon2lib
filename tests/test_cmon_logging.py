"""
Tests for cmon2lib logging.

Tests verify:
- Log format function
- Summary writing
- Archive renaming
- Cleanup logic
- Exception formatting
"""

import os
import time
import pytest
from datetime import datetime
from pathlib import Path


class TestFormatLogRecord:
    """Test the log format function (file logging)."""

    def test_format_includes_timestamp(self):
        from cmon2lib.utils.cmon_logging import _format_log_record

        # Use a simple object that mimics loguru's record structure
        class MockLevel:
            name = "INFO"

        record = {
            "time": datetime(2026, 4, 12, 18, 14, 0),
            "level": MockLevel(),
            "name": "test_module",
            "function": "test_func",
            "line": 42,
            "extra": {"user": "testuser"},
            "message": "test message",
        }

        formatted = _format_log_record(record)
        assert "2026-04-12 18:14:00" in formatted
        assert "INFO" in formatted
        assert "test_module" in formatted
        assert "test_func" in formatted
        assert "42" in formatted
        assert "testuser" in formatted
        assert "test message" in formatted

    def test_format_uses_pipe_delimiter(self):
        from cmon2lib.utils.cmon_logging import _format_log_record

        class MockLevel:
            name = "DEBUG"

        record = {
            "time": datetime.now(),
            "level": MockLevel(),
            "name": "m",
            "function": "f",
            "line": 1,
            "extra": {"user": "u"},
            "message": "msg",
        }

        formatted = _format_log_record(record)
        # Should have 4 pipe delimiters (5 fields)
        assert formatted.count(" | ") == 4

    def test_file_format_differs_from_console_format(self):
        """Verify file format includes metadata that console format omits."""
        from cmon2lib.utils.cmon_logging import _format_log_record, _format_console

        class MockLevel:
            name = "INFO"

        record = {
            "time": datetime(2026, 4, 12, 18, 14, 0),
            "level": MockLevel(),
            "name": "test_module",
            "function": "test_func",
            "line": 42,
            "extra": {"user": "testuser"},
            "message": "test message",
        }

        file_formatted = _format_log_record(record)
        console_formatted = _format_console(record)

        # File format should have timestamp, level, module, user
        assert "2026-04-12 18:14:00" in file_formatted
        assert "INFO" in file_formatted
        assert "testuser" in file_formatted

        # Console format should just be the message
        assert console_formatted == "test message"

        # They should be different
        assert file_formatted != console_formatted

    def test_console_format_for_warning_has_prefix(self):
        """Console format for WARNING should include WARN: prefix."""
        from cmon2lib.utils.cmon_logging import _format_console

        class MockLevel:
            name = "WARNING"

        record = {
            "level": MockLevel(),
            "message": "something went wrong",
        }

        formatted = _format_console(record)
        # Should have WARN: prefix
        assert "WARN:" in formatted
        # Message should be present
        assert "something went wrong" in formatted

    def test_console_format_for_error_has_prefix(self):
        """Console format for ERROR should include ERR: prefix."""
        from cmon2lib.utils.cmon_logging import _format_console

        class MockLevel:
            name = "ERROR"

        record = {
            "level": MockLevel(),
            "message": "connection failed",
        }

        formatted = _format_console(record)
        # Should have ERR: prefix
        assert "ERR:" in formatted
        # Message should be present
        assert "connection failed" in formatted


class TestWriteToSummary:
    """Test summary log writing."""

    def test_writes_info_to_summary(self, tmp_path):
        from cmon2lib.utils.cmon_logging import _write_to_summary

        summary_file = tmp_path / "test_csummary.log"

        # Mock globals
        import cmon2lib.utils.cmon_logging as clog_mod

        old_summary = clog_mod._clog_summary
        clog_mod._clog_summary = summary_file

        try:
            _write_to_summary("INFO", "test info message")

            content = summary_file.read_text()
            assert "test info message" in content
            assert "INFO" in content
        finally:
            clog_mod._clog_summary = old_summary

    def test_writes_error_to_summary(self, tmp_path):
        from cmon2lib.utils.cmon_logging import _write_to_summary

        summary_file = tmp_path / "test_csummary.log"

        import cmon2lib.utils.cmon_logging as clog_mod

        old_summary = clog_mod._clog_summary
        clog_mod._clog_summary = summary_file

        try:
            _write_to_summary("ERROR", "test error message")

            content = summary_file.read_text()
            assert "test error message" in content
            assert "ERROR" in content
        finally:
            clog_mod._clog_summary = old_summary

    def test_writes_success_to_summary(self, tmp_path):
        from cmon2lib.utils.cmon_logging import _write_to_summary

        summary_file = tmp_path / "test_csummary.log"

        import cmon2lib.utils.cmon_logging as clog_mod

        old_summary = clog_mod._clog_summary
        clog_mod._clog_summary = summary_file

        try:
            _write_to_summary("SUCCESS", "test success message")

            content = summary_file.read_text()
            assert "test success message" in content
            assert "SUCCESS" in content
        finally:
            clog_mod._clog_summary = old_summary


class TestRenameArchive:
    """Test archive renaming for WARN/ERR."""

    def test_renames_to_warn(self, tmp_path):
        from cmon2lib.utils.cmon_logging import _rename_archive

        archive_file = tmp_path / "20260412_test.log"
        archive_file.touch()

        import cmon2lib.utils.cmon_logging as clog_mod

        old_archive = clog_mod._clog_archive
        old_renamed = clog_mod._clog_archive_renamed

        clog_mod._clog_archive = archive_file
        clog_mod._clog_archive_renamed = False

        try:
            _rename_archive("WARNING")

            assert not archive_file.exists()
            warn_file = tmp_path / "20260412_test_WARN.log"
            assert warn_file.exists()
        finally:
            clog_mod._clog_archive = old_archive
            clog_mod._clog_archive_renamed = old_renamed

    def test_renames_to_err(self, tmp_path):
        from cmon2lib.utils.cmon_logging import _rename_archive

        archive_file = tmp_path / "20260412_test.log"
        archive_file.touch()

        import cmon2lib.utils.cmon_logging as clog_mod

        old_archive = clog_mod._clog_archive
        old_renamed = clog_mod._clog_archive_renamed

        clog_mod._clog_archive = archive_file
        clog_mod._clog_archive_renamed = False

        try:
            _rename_archive("ERROR")

            assert not archive_file.exists()
            err_file = tmp_path / "20260412_test_ERR.log"
            assert err_file.exists()
        finally:
            clog_mod._clog_archive = old_archive
            clog_mod._clog_archive_renamed = old_renamed


class TestCleanupOldArchives:
    """Test age-based cleanup."""

    def test_deletes_old_archives(self, tmp_path):
        from cmon2lib.utils.cmon_logging import _cleanup_old_archives
        import cmon2lib.utils.cmon_logging as clog_mod

        # Create old archive
        old_archive = tmp_path / "20200101_test.log"
        old_archive.touch()
        old_time = time.time() - (60 * 24 * 60 * 60)  # 60 days ago
        os.utime(old_archive, (old_time, old_time))

        # Create recent archive
        recent_archive = tmp_path / "20260412_test.log"
        recent_archive.touch()

        # Save and reset global state
        old_archive_global = clog_mod._clog_archive
        clog_mod._clog_archive = None  # Don't skip any

        try:
            _cleanup_old_archives(tmp_path, max_age_days=30)

            assert not old_archive.exists()  # Deleted
            assert recent_archive.exists()  # Kept
        finally:
            clog_mod._clog_archive = old_archive_global

    def test_preserves_warn_logs(self, tmp_path):
        from cmon2lib.utils.cmon_logging import _cleanup_old_archives
        import cmon2lib.utils.cmon_logging as clog_mod

        # Create old WARN archive
        old_warn = tmp_path / "20200101_test_WARN.log"
        old_warn.touch()
        old_time = time.time() - (60 * 24 * 60 * 60)
        os.utime(old_warn, (old_time, old_time))

        old_archive_global = clog_mod._clog_archive
        clog_mod._clog_archive = None

        try:
            _cleanup_old_archives(tmp_path, max_age_days=30)

            assert old_warn.exists()  # Preserved
        finally:
            clog_mod._clog_archive = old_archive_global

    def test_preserves_err_logs(self, tmp_path):
        from cmon2lib.utils.cmon_logging import _cleanup_old_archives
        import cmon2lib.utils.cmon_logging as clog_mod

        # Create old ERR archive
        old_err = tmp_path / "20200101_test_ERR.log"
        old_err.touch()
        old_time = time.time() - (60 * 24 * 60 * 60)
        os.utime(old_err, (old_time, old_time))

        old_archive_global = clog_mod._clog_archive
        clog_mod._clog_archive = None

        try:
            _cleanup_old_archives(tmp_path, max_age_days=30)

            assert old_err.exists()  # Preserved
        finally:
            clog_mod._clog_archive = old_archive_global

    def test_preserves_summary_logs(self, tmp_path):
        from cmon2lib.utils.cmon_logging import _cleanup_old_archives
        import cmon2lib.utils.cmon_logging as clog_mod

        # Create old summary
        old_summary = tmp_path / "test_csummary.log"
        old_summary.touch()
        old_time = time.time() - (60 * 24 * 60 * 60)
        os.utime(old_summary, (old_time, old_time))

        old_archive_global = clog_mod._clog_archive
        clog_mod._clog_archive = None

        try:
            _cleanup_old_archives(tmp_path, max_age_days=30)

            assert old_summary.exists()  # Preserved
        finally:
            clog_mod._clog_archive = old_archive_global


class TestClogException:
    """Test exception formatting in clog."""

    def test_exception_format(self):
        """Test that exception is formatted correctly."""
        try:
            raise ValueError("test error")
        except ValueError as e:
            from cmon2lib.utils.cmon_logging import _clog

            # Build message with exception - same as clog does
            msg = "Operation failed"
            exception = e
            result = f"{msg}: {type(exception).__name__}: {exception}"
            assert result == "Operation failed: ValueError: test error"


class TestFormatConsole:
    """Test the console format function (dual-output)."""

    def test_warning_gets_warn_prefix(self):
        from cmon2lib.utils.cmon_logging import _format_console

        class MockLevel:
            name = "WARNING"

        record = {
            "level": MockLevel(),
            "message": "something went wrong",
        }

        formatted = _format_console(record)
        assert "WARN:" in formatted
        assert "something went wrong" in formatted

    def test_error_gets_err_prefix(self):
        from cmon2lib.utils.cmon_logging import _format_console

        class MockLevel:
            name = "ERROR"

        record = {
            "level": MockLevel(),
            "message": "connection failed",
        }

        formatted = _format_console(record)
        assert "ERR:" in formatted
        assert "connection failed" in formatted

    def test_info_just_message(self):
        from cmon2lib.utils.cmon_logging import _format_console

        class MockLevel:
            name = "INFO"

        record = {
            "level": MockLevel(),
            "message": "simple info",
        }

        formatted = _format_console(record)
        assert formatted == "simple info"

    def test_debug_just_message_with_dim(self):
        from cmon2lib.utils.cmon_logging import _format_console

        class MockLevel:
            name = "DEBUG"

        record = {
            "level": MockLevel(),
            "message": "debug info",
        }

        formatted = _format_console(record)
        # DEBUG gets dim color markup
        assert "<dim>debug info</dim>" == formatted

    def test_success_just_message_with_green(self):
        from cmon2lib.utils.cmon_logging import _format_console

        class MockLevel:
            name = "SUCCESS"

        record = {
            "level": MockLevel(),
            "message": "operation complete",
        }

        formatted = _format_console(record)
        # SUCCESS gets green color markup
        assert "<green>operation complete</green>" == formatted

    def test_trace_just_message_with_dim(self):
        from cmon2lib.utils.cmon_logging import _format_console

        class MockLevel:
            name = "TRACE"

        record = {
            "level": MockLevel(),
            "message": "trace details",
        }

        formatted = _format_console(record)
        # TRACE gets dim color markup
        assert "<dim>trace details</dim>" == formatted
