from cmon2lib.taiga.taiga_user_functions import authenticate, get_authenticated_user_projects
from cmon2lib.utils.cmon_logging import clog


def list_epic_statuses_for_project(project):
    """List all EpicStatus objects for the given project object."""
    return project.list_user_story_statuses()

def list_user_stories_for_project(project):
    """List all user stories for the given project object."""
    return project.list_user_stories()

if __name__ == "__main__":
    projects = get_authenticated_user_projects()
    for project in projects:
        print(f"Project: {project.id} | {project.name}")
        statuses = list_epic_statuses_for_project(project)
        print("Epic Statuses:")
        for status in statuses:
            print(f"{status.id}: {status.name}")
        user_stories = list_user_stories_for_project(project)
        print("User Stories:")
        for story in user_stories:
            print(f"{story.id}: {story.subject} {story.status}")
        print()
