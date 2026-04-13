# cmon2lib Logging Requirements

## Overview

The `clog()` function provides dual-output logging:
- **Console**: Color-coded, minimal format (message only, WARN/ERR prefixed)
- **File**: Full metadata format with timestamp, level, module, user

## File Outputs

### 1. Archive Log (per run)
- **Purpose**: Complete record of all log messages during script execution
- **Location**: `_clog/<timestamp>_<module_name>.log`
- **Content**: All log levels (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR)
- **Naming**: Timestamp at start of filename (no double timestamps in content)
- **Format**:
  ```
  YYYY-MM-DD HH:mm:ss | LEVEL    | module:func:line | USER | message
  ```

### 2. Summary Log (persistent across runs)
- **Purpose**: Quick overview of important events, persists indefinitely
- **Location**: `_clog/<module_name>_csummary.log`
- **Content**: INFO, SUCCESS, ERROR levels only (DEBUG/TRACE/WARNING excluded)
- **Behavior**: Appends to existing file, never rotates or cleans

### 3. Error Rename (on ERROR only)
- **Purpose**: Flag errors for git attention (unignored via `!*_ERR.log`)
- **Trigger**: When ERROR is logged
- **Behavior**: Archive file renamed with `_ERR` suffix
- **Example**: `20260413_143421_cmon_logging_clog.log` → `20260413_143421_cmon_logging_clog_ERR.log`
- **Note**: Only happens once per run, first ERROR triggers rename
- **Persistence**: ERROR-renamed archives persist forever (never auto-deleted)

## Log Directory Resolution

1. If `init_clog(log_dir)` was called, use `log_dir/_clog/`
2. Otherwise, walk call stack to find first module outside cmon2lib
3. Place `_clog/` next to that script's directory

## Color Handling

- **Console handler**: `colorize=True` for ANSI colors
- **File handler**: `colorize=False` to avoid `<module>` tag parsing errors

## Gitignore Strategy

```gitignore
# Ignore archive logs (timestamp prefix matches 20XX for year)
*.log

# Ignore summary (persistent, managed separately)
*_csummary.log

# Track errors (catch attention)
!*_ERR.log
```

## Cleanup

- Archives older than 30 days deleted, except:
  - `*_ERR.log` (error archives persist forever)
  - `*_csummary.log`

## Log Levels

| Level | Console Output | Archive | Summary |
|-------|---------------|---------|---------|
| TRACE | Dim message | ✓ | ✗ |
| DEBUG | Dim message | ✓ | ✗ |
| INFO | Plain message | ✓ | ✓ |
| SUCCESS | Green message | ✓ | ✓ |
| WARNING | `WARN:` prefix | ✓ | ✗ |
| ERROR | `ERR:` prefix | ✓ | ✓ (triggers ERR rename) |
| CRITICAL | `CRIT:` prefix | ✓ | ✓ |