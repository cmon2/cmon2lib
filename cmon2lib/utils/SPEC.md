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
| `cmon_trace` | Trace ID for correlating logs across scripts | `cmon-trace` env var (auto-generated ULID if not set) |
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
{timestamp} | {level:8} | {name}:{line} | {user} | {message} | cmon_trace={cmon_trace}
```

**Timestamp format**: `YYYY-MM-DD HH:mm:ss` (24-hour, zero-padded)

**Example**:
```
2026-04-13 14:34:21 | INFO    | __main__:33 | simon | Authenticated user ID: 123 | cmon_trace=01ARZ3NDEKTSV4RRFFQ69G5FA
```

**Note**: The trace_id (`cmon_trace`) appears only in file logs, not console output.

**Note**: The file format uses `{name}` (module name) and `{line}` (line number). The function name is not included in the file format due to Loguru color parsing limitations with angle brackets in function names like `<module>`.

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

## Trace ID

The trace_id enables correlating log entries across multiple script executions (e.g., post-clone hooks, multi-step workflows).

### Behavior

- **Environment variable**: `cmon_trace`
- **Auto-generation**: If `cmon_trace` is not set when `clog()` is first called, a ULID is automatically generated and exported to `cmon_trace`
- **Inheritance**: Child processes inherit `cmon_trace` via environment, enabling end-to-end trace correlation
- **Format**: ULID (time-ordered, sortable) with fallback to UUID if ULID is unavailable
- **Scope**: File logs only (console output does not include trace_id)

### Implementation Notes

- Trace_id is managed internally; no public `get_trace_id()` function is exposed
- The `_ensure_trace_id()` function (private) handles generation and environment export
- All log entries within a single process share the same trace_id
- Note: Env var uses underscore (`cmon_trace`) for cross-language compatibility (Python and Bash)

## Log Status Verification

The `check_script_status()` function enables verification of script execution success via log correlation.

### API

```python
from cmon2lib.utils.check_script_status import LogStatus, check_script_status

status = check_script_status(script_path: str, trace_id: str) -> LogStatus
```

### LogStatus Enum

| Value | Description |
|-------|-------------|
| `SUCCESS` | No WARN or ERROR found with matching trace_id |
| `WARNING` | WARN found (no ERROR) |
| `ERROR` | ERROR found |

### Behavior

1. Searches for `_clog/` directory next to the script
2. Checks all `*.log` files in `_clog/` for lines matching `| cmon_trace=<trace_id>`
3. Returns highest severity found (ERROR > WARNING > SUCCESS)
4. Raises `ValueError` if no logs found with matching trace_id

### CLI

```bash
cmon check_status <script_path> <trace_id>
# Exit codes: 0=success, 1=warning, 2=error, 3=not found
```

### Use Case

Post-clone script verification in simon-distrolocs:
1. Generate trace_id before running script
2. Pass `cmon_trace=<trace_id>` env var to script
3. After script completes, call `check_script_status(script_path, trace_id)`
4. Log warning/error if verification fails
