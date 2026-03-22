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

def test_clog_invalid_level_warns_and_logs(capsys):
    logger.remove()
    logger.add(lambda msg: print(msg, end=""))
    clog('notalevel', 'should warn about invalid level')
    captured = capsys.readouterr()
    assert 'Invalid log level' in captured.out
    assert 'should warn about invalid level' in captured.out

def test_clog_args_and_kwargs(capsys):
    logger.remove()
    logger.add(lambda msg: print(msg, end=""))
    clog('info', 'value: {}', 42)
    captured = capsys.readouterr()
    assert 'value: 42' in captured.out
