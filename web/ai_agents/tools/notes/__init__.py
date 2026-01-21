"""Notes tool for reconPoint AI Agents - syncs with Django TodoNote model."""

from typing import Any, Dict
from django.db import transaction
from recon_note.models import TodoNote
from startScan.models import ScanHistory, Subdomain
from dashboard.models import Project
from ..registry import ToolSchema, register_tool

@register_tool(
    name="notes",
    description="Manage persistent notes for key findings. Actions: create, read, list. Syncs with reconPoint database.",
    schema=ToolSchema(
        properties={
            "action": {
                "type": "string",
                "enum": ["create", "read", "list"],
                "description": "The action to perform",
            },
            "project_id": {
                "type": "integer",
                "description": "The ID of the project to save the note to.",
            },
            "title": {
                "type": "string",
                "description": "Brief title for the finding",
            },
            "description": {
                "type": "string",
                "description": "Detailed description of the finding",
            },
            "scan_history_id": {
                "type": "integer",
                "description": "Optional: Scan history ID associated with the finding",
            },
            "subdomain_id": {
                "type": "integer",
                "description": "Optional: Subdomain ID associated with the finding",
            },
            "is_important": {
                "type": "boolean",
                "description": "Whether this is a high-confidence/critical finding",
            }
        },
        required=["action", "project_id"],
    ),
    category="utility",
)
async def notes(arguments: dict, runtime) -> str:
    """
    Manage persistent notes in the reconPoint database.
    """
    action = arguments["action"]
    # Try to get project_id from runtime or arguments
    project_id = arguments.get("project_id") or getattr(runtime, "project_id", None)
    if not project_id:
        return "Error: project_id is required."

    try:
        from ...recon_note.models import TodoNote
        from ...startScan.models import Project, ScanHistory, Subdomain
        
        # Link to objects if IDs provided
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return f"Error: Project with ID {project_id} does not exist."

    if action == "create":
        title = arguments.get("title", "AI Finding")
        description = arguments.get("description", "")
        scan_history_id = arguments.get("scan_history_id")
        subdomain_id = arguments.get("subdomain_id")
        is_important = arguments.get("is_important", False)

        note = TodoNote.objects.create(
            project=project,
            title=title,
            description=description,
            is_important=is_important,
            scan_history_id=scan_history_id,
            subdomain_id=subdomain_id
        )
        return f"Created note '{title}' in project {project.name} (ID: {note.id})"

    elif action == "list":
        notes = TodoNote.objects.filter(project=project)
        if not notes.exists():
            return f"No notes found for project {project.name}."
        
        lines = [f"Notes for project {project.name}:"]
        for n in notes:
            importance = " [IMPORTANT]" if n.is_important else ""
            lines.append(f"- [{n.id}]{importance} {n.title}: {n.description[:100]}...")
        return "\n".join(lines)

    elif action == "read":
        # Implementation for read by ID if needed
        pass

    return f"Unknown action: {action}"
