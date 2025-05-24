from cmon2lib.taiga.taiga_user_functions import authenticate, get_authenticated_user_projects
from cmon2lib.utils.cmon_logging import clog


def cprint_project(project):
    """
    Return a styled string containing all user story statuses with their user stories as a sublist for the given project.

    Format:
        === Project: <id> | <name> ===
          [<status1>]
            • <story1>
            • <story2>
          [<status2>]
            ...
    Args:
        project: The Taiga project object.
    Returns:
        str: A formatted string with statuses and their user stories.
    """
    clog('info', f"Formatting project {project.id} - {project.name}")
    result = [f"\n=== Project: {project.id} | {project.name} ==="]
    statuses = project.list_user_story_statuses()
    user_stories = project.list_user_stories()
    # Map status id to status name
    status_map = {status.id: status.name for status in statuses}
    # Group user stories by status
    stories_by_status = {status.id: [] for status in statuses}
    for story in user_stories:
        stories_by_status.setdefault(story.status, []).append(story)
    # Build output
    for status in statuses:
        result.append(f"  [{status.name}]")
        stories = stories_by_status.get(status.id, [])
        for story in stories:
            result.append(f"    • {story.id}: {story.subject}")
        if not stories:
            clog('debug', f"No user stories for status '{status.name}' in project {project.id}")
    return "\n".join(result)

if __name__ == "__main__":
    clog('info', "Fetching authenticated user projects...")
    projects = get_authenticated_user_projects()
    for project in projects:
        print(cprint_project(project))
        clog('info', f"Printed project {project.id} - {project.name}")
