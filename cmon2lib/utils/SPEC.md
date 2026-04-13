# cmon2lib Logging Requirements

## Overview

The `clog()` function provides dual-output logging:
- **Console**: Color-coded, minimal format (message only, WARN/ERROR prefixed)
- **File**: Full metadata format with timestamp, level, module, user

## Collected Information

Each log entry captures the following data:

| Variable | Description | Source |
|----------|-------------|--------|
| `timestamp` | When the log entry was created | `datetime.now()` |
| `level` | Log severity level (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL) | User-specified |
| `module` | Python module where `clog()` was called | `__name__` of caller's module |
| `func` | Function name where `clog()` was called | `frame.f_code.co_name` |
| `line` | Line number where `clog()` was called | `frame.f_lineno` |
| `user` | Username executing the script | `USER` or `USERNAME` env var |
| `message` | The actual log message | User-specified |

## File Outputs

### 1. Archive Log (per run)
- **Purpose**: Complete record of all log messages during script execution
- **Location**: `_clog/<timestamp>_<module_name>.log`
- **Included Log Types**: All levels (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR)
- **Naming**: Timestamp at start of filename
- **Behavior**: One archive file per script run, rotation based on time

### 2. Summary Log (persistent across runs)
- **Purpose**: Quick overview of important events, persists indefinitely
- **Location**: `_clog/<module_name>_csummary.log`
- **Included Log Types**: INFO, SUCCESS, ERROR only (DEBUG/TRACE/WARNING excluded)
- **Behavior**: Appends to existing file, never rotates or cleans

### 3. Renamed Error Logs

When ERROR is logged, the archive file is renamed to draw git attention:

- **Purpose**: Flag errors for git attention (unignored via `!*_ERROR.log`)
- **Trigger**: First ERROR in a run
- **Suffix**: `_ERROR`
- **Example**: `20260413_143421_cmon_logging_clog.log` → `20260413_143421_cmon_logging_clog_ERROR.log`
- **Behavior**: Renamed archive persists forever (never auto-deleted)

## Log Content Format

The format is identical for archive and summary logs:

```
{timestamp} | {level:8} | {module}:{func}:{line} | {user} | {message}
```

**Timestamp format**: `YYYY-MM-DD HH:mm:ss` (24-hour, zero-padded)

**Example**:
```
2026-04-13 14:34:21 | INFO    | ctaiga:get_authenticated_user:33 | simon | Authenticated user ID: 123
```

## Console Output Format

| Level | Output Format (Message Pattern; Message Color) |
|-------|------------------------------------------------|
| TRACE | `{message}`; Dim gray |
| DEBUG | `{message}`; Dim gray |
| INFO | `{message}`; No color |
| SUCCESS | `{message}`; Green |
| WARNING | `WARNING: {message}`; Yellow |
| ERROR | `ERROR: {message}`; Red |
| CRITICAL | `CRITICAL: {message}`; Red |

## Specification

### Log Directory Resolution

1. By default, the log directory is derived from the call stack: the `_clog/` directory is automatically created next to the script that called `clog()`
2. Optionally, `init_clog(log_dir)` may be called to explicitly specify a custom log directory path

### Cleanup

- **Trigger**: Cleanup runs once on every `clog()` call (during `_init_clog()`)
- **Age threshold**: Archives older than 30 days
- **Protected files** (never deleted):
  - `*_ERROR.log` — renamed error archives persist forever
  - `*_csummary.log` — summary logs persist forever
- **Current run**: The active archive is never deleted even if old

### Color Handling

- **Console handler**: `colorize=True` enables ANSI escape codes for colored console output
- **File handler**: `colorize=False` prevents `<module>` tags in function names from being interpreted as color markup

### Gitignore Handling

When creating a new `_clog/` directory, `clog()` creates a `.gitignore` file with the correct rules automatically. This ensures:
1. Normal archive logs are ignored (timestamped, auto-deleted)
2. Summary logs are ignored (managed separately)
3. Error logs `*_ERROR.log` are NOT ignored (for git attention)

```gitignore
*.log
*_csummary.log
!*_ERROR.log
```

## Log Levels

| Level | Included in Archive Log | Included in Summary Log |
|-------|-------------------------|------------------------|
| TRACE | ✓ | ✗ |
| DEBUG | ✓ | ✗ |
| INFO | ✓ | ✓ |
| SUCCESS | ✓ | ✓ |
| WARNING | ✓ | ✗ |
| ERROR | ✓ | ✓ |
| CRITICAL | ✓ | ✓ |
