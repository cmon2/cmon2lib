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
    """Get the authenticated user's information and print it to the log."""
    api = authenticate()
    try:
        user = api.me()
        print(user.id)
        return user
    except exceptions.TaigaRestException as e:
        print(f"Failed to get authenticated user: {e}")
        raise RuntimeError(f"Failed to get authenticated user: {e}")

def get_authenticated_user_projects():
    """Get the authenticated user's projects using their user ID and print their names."""
    api = authenticate()
    try:
        user = api.me()
        # Fetch projects for this user
        projects = api.projects.list(page=1,member=user.id)
        if projects:
            clog(level="INFO", msg="Projects owned by the authenticated user:")
            for project in projects:
                print(f"{project.id}: {project.name}")
        else:
            print("No projects found for this user.")
        return projects
    except exceptions.TaigaRestException as e:
        print(f"Failed to get projects for user: {e}")
        raise RuntimeError(f"Failed to get projects for user: {e}")

if __name__ == "__main__":
    try:
        get_authenticated_user()
        get_authenticated_user_projects()
    except Exception as e:
        print(f"Error: {e}")
