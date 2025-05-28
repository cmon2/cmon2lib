import os
from taiga import TaigaAPI
from taiga.exceptions import TaigaRestException
from cmon2lib.utils.cmon_logging import clog

def authenticate(username, password, api_url="https://api.taiga.io/"):
    """Authenticate to Taiga and return the API object for the given user."""
    api = TaigaAPI(host=api_url)
    try:
        if username and password:
            api.auth(username=username, password=password)
        else:
            raise EnvironmentError("Provide username and password as function arguments.")
    except TaigaRestException as e:
        raise RuntimeError(f"Taiga authentication failed: {e}")
    return api

def get_authenticated_user(username, password, api_url="https://api.taiga.io/"):
    """
    Get the authenticated user's information and log the user ID.
    Args:
        username (str): Taiga username
        password (str): Taiga password
        api_url (str): Taiga API URL (default: public Taiga)
    Returns:
        user: The authenticated Taiga user object.
    Raises:
        RuntimeError: If authentication fails or user cannot be fetched.
    """
    api = authenticate(username, password, api_url)
    try:
        user = api.me()
        clog('info', f"Authenticated user ID: {user.id}")
        return user
    except TaigaRestException as e:
        clog('error', f"Failed to get authenticated user: {e}")
        raise RuntimeError(f"Failed to get authenticated user: {e}")


def get_authenticated_user_projects(username, password, api_url="https://api.taiga.io/"):
    """
    Get the authenticated user's projects using their user ID and log the project names.
    Args:
        username (str): Taiga username
        password (str): Taiga password
        api_url (str): Taiga API URL (default: public Taiga)
    Returns:
        list: List of Taiga project objects the user is a member of.
    Raises:
        RuntimeError: If projects cannot be fetched.
    """
    api = authenticate(username, password, api_url)
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
    except TaigaRestException as e:
        clog('error', f"Failed to get projects for user: {e}")
        raise RuntimeError(f"Failed to get projects for user: {e}")

if __name__ == "__main__":
    # Example usage: get credentials from environment variables
    import os
    TAIGA_USERNAME = os.environ.get("TAIGA_USERNAME")
    TAIGA_PASSWORD = os.environ.get("TAIGA_PASSWORD")
    TAIGA_API_URL = os.environ.get("TAIGA_API_URL", "https://api.taiga.io/")

    try:
        get_authenticated_user(TAIGA_USERNAME, TAIGA_PASSWORD, TAIGA_API_URL)
        get_authenticated_user_projects(TAIGA_USERNAME, TAIGA_PASSWORD, TAIGA_API_URL)
    except Exception as e:
        clog('error', f"Error: {e}")
