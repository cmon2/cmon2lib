import os
from taiga import TaigaAPI, exceptions
from cmon2lib.utils.cmon_logging import clog

# Use the base URL (no /api/v1/ at the end)
TAIGA_API_URL = os.environ.get("TAIGA_API_URL", "https://api.taiga.io/")
TAIGA_USERNAME = os.environ.get("TAIGA_USERNAME")
TAIGA_PASSWORD = os.environ.get("TAIGA_PASSWORD")
TAIGA_TOKEN = os.environ.get("TAIGA_TOKEN")

def authenticate():
    """Authenticate to Taiga and return the API object."""
    api = TaigaAPI(host=TAIGA_API_URL)
    try:
        if TAIGA_TOKEN:
            api.auth(token=TAIGA_TOKEN)
        elif TAIGA_USERNAME and TAIGA_PASSWORD:
            api.auth(username=TAIGA_USERNAME, password=TAIGA_PASSWORD)
        else:
            raise EnvironmentError("Set TAIGA_USERNAME and TAIGA_PASSWORD or TAIGA_TOKEN environment variables.")
    except exceptions.TaigaRestException as e:
        raise RuntimeError(f"Taiga authentication failed: {e}")
    return api

def get_authenticated_user():
    """
    Get the authenticated user's information and log the user ID.
    Returns:
        user: The authenticated Taiga user object.
    Raises:
        RuntimeError: If authentication fails or user cannot be fetched.
    """
    api = authenticate()
    try:
        user = api.me()
        clog('info', f"Authenticated user ID: {user.id}")
        return user
    except exceptions.TaigaRestException as e:
        clog('error', f"Failed to get authenticated user: {e}")
        raise RuntimeError(f"Failed to get authenticated user: {e}")


def get_authenticated_user_projects():
    """
    Get the authenticated user's projects using their user ID and log the project names.
    Returns:
        list: List of Taiga project objects the user is a member of.
    Raises:
        RuntimeError: If projects cannot be fetched.
    """
    api = authenticate()
    try:
        user = api.me()
        page_size = 15  # Default Taiga API page size
        projects = api.projects.list(page=1, member=user.id, page_size=page_size)
        # Check if there might be more projects than fit on one page
        if hasattr(projects, '__len__') and len(projects) == page_size:
            clog('warning', f"Project list may be truncated: found {len(projects)} projects (page size limit). There may be more projects for user {user.id}.")
        if projects:
            clog('info', f"Found {len(projects)} projects for user {user.id}.")
            for project in projects:
                clog('debug', f"Project: {project.id}: {project.name}")
        else:
            clog('warning', f"No projects found for user {user.id}.")
        return projects
    except exceptions.TaigaRestException as e:
        clog('error', f"Failed to get projects for user: {e}")
        raise RuntimeError(f"Failed to get projects for user: {e}")

if __name__ == "__main__":
    try:
        get_authenticated_user()
        get_authenticated_user_projects()
    except Exception as e:
        clog('error', f"Error: {e}")
