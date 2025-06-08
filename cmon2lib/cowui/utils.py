# cowu/utils.py
"""
Utility functions for open webui function implementation.
"""

from cmon2lib.utils.cmon_logging import clog

def inject_string_into_system_message(body, s, prefix=""):
    """
    Injects the given string into the first system message in body['messages'], with an optional prefix.
    Performs a generic check that 'body' is a dict with a 'messages' key containing a list of dicts.
    If the structure is not as expected, logs a warning.
    Args:
        body (dict): The dictionary expected to contain a 'messages' key.
        s (str): The string to inject into the system message.
        prefix (str): A string to prepend before s when injecting.
    """
    if not isinstance(body, dict):
        clog("warning", "body is not a dict")
        return
    messages = body.get("messages")
    if not isinstance(messages, list):
        clog("warning", "body['messages'] is not a list")
        return
    found_system = False
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        if msg.get("role") == "system":
            msg["content"] = f"{msg.get('content', '')}{prefix}{s}"
            found_system = True
            break
    if not found_system:
        # Add a new system message if none exists
        messages.insert(0, {"role": "system", "content": f"{prefix}{s}"})
