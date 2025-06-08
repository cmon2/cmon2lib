import pytest
from cmon2lib.utils.cmon_logging import clog
from loguru import logger


def test_clog_info_logs_message(capsys):
    logger.remove()
    logger.add(lambda msg: print(msg, end=""))
    clog('info', 'test info message')
    captured = capsys.readouterr()
    assert 'test info message' in captured.out

def test_clog_warning_logs_message(capsys):
    logger.remove()
    logger.add(lambda msg: print(msg, end=""))
    clog('warning', 'test warning message')
    captured = capsys.readouterr()
    assert 'test warning message' in captured.out

def test_clog_invalid_level_defaults_to_info(capsys):
    logger.remove()
    logger.add(lambda msg: print(msg, end=""))
    clog('notalevel', 'should default to info')
    captured = capsys.readouterr()
    assert 'should default to info' in captured.out

def test_clog_args_and_kwargs(capsys):
    logger.remove()
    logger.add(lambda msg: print(msg, end=""))
    clog('info', 'value: {}', 42)
    captured = capsys.readouterr()
    assert 'value: 42' in captured.out
