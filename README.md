# cmon2lib

Personal Python library for convenient personalized functionality.

## Logging

cmon2lib provides a unified logging system with cross-language compatibility (Python and Bash).

### Dual-Output Logging

cmon2lib logs to both **console (terminal)** and **file** simultaneously:

| Output | Format | When |
|--------|--------|------|
| **Console** | Just the message (colored) | Always |
| Console (WARNING/ERROR) | `WARN: message` or `ERR: message` | For WARNING/ERROR |
| **File** | Full metadata: `YYYY-MM-DD HH:mm:ss | LEVEL | module:func:line | USER | message` | Always |

**Console Colors:**
- INFO: No color (clean output)
- DEBUG/TRACE: Dim gray
- SUCCESS: Green
- WARNING: Yellow + `WARN:` prefix
- ERROR: Red + `ERR:` prefix

**File Format Example:**
```
2026-04-12 18:14:00 | INFO    | ctaiga:get_authenticated_user:33 | simon | Authenticated user ID: 123
```

**Console Output Example (same message):**
```
Authenticated user ID: 123
```

For WARNING:
```
WARN: something went wrong
```

For ERROR:
```
ERR: connection failed
```

### Python Usage

```python
from cmon2lib.utils.cmon_logging import clog

# Basic logging
clog('info', 'message')
clog('debug', 'value: {}', 42)

# With exception
try:
    raise ValueError("test error")
except ValueError as e:
    clog('error', 'Operation failed', exception=e)
# Output: Operation failed: ValueError: test error
```

### Bash Usage

```bash
source cmon_lib/cmon_logging.sh
init_clog "my_script"

clog_info "message"
clog_error "error message"
clog_warn "warning message"
clog_success "success message"
```

### Log Levels

| Level | Python | Bash | Description |
|-------|--------|------|-------------|
| TRACE | `clog('trace', ...)` | N/A | Detailed diagnostic |
| DEBUG | `clog('debug', ...)` | N/A | Debug information |
| INFO | `clog('info', ...)` | `clog_info` | General information |
| SUCCESS | `clog('success', ...)` | `clog_success` | Success messages |
| WARNING | `clog('warning', ...)` | `clog_warn` | Warnings |
| ERROR | `clog('error', ...)` | `clog_error` | Errors |
| CRITICAL | `clog('critical', ...)` | N/A | Critical errors |

### File Logging

Logs are automatically written to `_clog/` directory next to the module:

- **Archive log**: `{timestamp}_{module}.log` - all log messages
- **Summary log**: `{module}_csummary.log` - INFO, SUCCESS, ERROR only

If WARN or ERROR is logged, the archive is renamed to `*_WARN.log` or `*_ERR.log`.

### Log Cleanup

Archive logs older than 30 days are automatically deleted on initialization.

**Protected files (never deleted automatically):**
- `*_WARN.log` - renamed warning archives
- `*_ERR.log` - renamed error archives  
- `*_csummary.log` - summary logs

### Features

- Auto-init on first `clog()` call (Python)
- Executing user tracking (via `USER` or `USERNAME` env vars)
- Single-line exception formatting
- Age-based cleanup (30 days for archives)
- No external dependencies (uses loguru for Python)

## Modules

### ccaldav

Calendar integration for planning digests.

```python
from cmon2lib.ccaldav import digest_schedule

schedule = digest_schedule(url, username, password)
```

### ctaiga

Taiga project management integration.

```python
from cmon2lib.ctaiga import get_authenticated_user, get_authenticated_user_projects

user = get_authenticated_user(username, password)
projects = get_authenticated_user_projects(username, password)
```

### cowui

Open WebUI utilities for function injection.

```python
from cmon2lib.cowui import inject_string_into_system_message

inject_string_into_system_message(body, "injected text", prefix="\n")
```
