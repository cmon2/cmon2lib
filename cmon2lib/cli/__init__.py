"""CLI - Command-line interface for cmon2lib."""

import sys
from ..utils.check_script_status import check_script_status, LogStatus


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: cmon check_status <script_path> <trace_id>", file=sys.stderr)
        sys.exit(3)

    command = sys.argv[1]
    if command != "check_status":
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(3)

    script_path = sys.argv[2]
    trace_id = sys.argv[3]

    try:
        status = check_script_status(script_path, trace_id)
        print(status.value)
        if status == LogStatus.SUCCESS:
            sys.exit(0)
        elif status == LogStatus.WARNING:
            sys.exit(1)
        else:
            sys.exit(2)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
