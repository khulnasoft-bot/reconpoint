"""Scans tool for ReconAgent."""

import logging
from typing import Any, Dict, List, Optional
from .registry import ToolSchema, register_tool

logger = logging.getLogger(__name__)

@register_tool(
    name="trigger_scan",
    description="Trigger a specialized security scan (nuclei, nmap, naabu, etc.) on a subdomain or project.",
    schema=ToolSchema(
        properties={
            "scan_type": {
                "type": "string",
                "description": "Type of scan to trigger (nuclei, nmap, naabu, dirsearch, etc.)",
                "enum": ["nuclei", "nmap", "naabu", "dirsearch", "subdomain_discovery", "dns_recon"]
            },
            "subdomain_id": {
                "type": "integer",
                "description": "Optional ID of the subdomain to scan."
            },
            "project_id": {
                "type": "integer",
                "description": "Optional ID of the project."
            },
            "engine_id": {
                "type": "integer",
                "description": "Optional ID of the scan engine to use."
            },
            "arguments": {
                "type": "object",
                "description": "Optional additional arguments for the scan."
            }
        },
        required=["scan_type"]
    ),
    category="recon"
)
async def trigger_scan(arguments: Dict[str, Any], runtime: Any) -> str:
    """Execute the scan trigger."""
    scan_type = arguments.get("scan_type")
    subdomain_id = arguments.get("subdomain_id")
    project_id = arguments.get("project_id") or getattr(runtime, "project_id", None)
    
    if not project_id:
        return "Error: project_id is required to trigger a scan."

    try:
        from startScan.models import Subdomain, ScanHistory, EngineType
        from startScan.tasks import initiate_scan, initiate_subscan
        from dashboard.models import Project
        
        project = Project.objects.get(id=project_id)
        
        # If subdomain_id is provided, try to trigger a subscan
        if subdomain_id:
            subdomain = Subdomain.objects.filter(id=subdomain_id, target_domain__project=project).first()
            if not subdomain:
                return f"Error: Subdomain with ID {subdomain_id} not found in project {project.name}."
            
            # Find an appropriate engine if not provided
            # This is a simplified logic - in a real system we'd map scan_type to EngineType
            engine = EngineType.objects.filter(pk=arguments.get("engine_id")).first()
            if not engine:
                # Default to an engine that matches the scan_type if possible
                engine = EngineType.objects.filter(engine_name__icontains=scan_type).first()
            
            if not engine:
                 return f"Error: No suitable scan engine found for {scan_type}."

            # Trigger subscan
            initiate_subscan.delay(
                scan_history_id=subdomain.scan_history.id,
                subdomain_id=subdomain.id,
                engine_id=engine.id,
                scan_type=scan_type
            )
            return f"Successfully triggered {scan_type} subscan for {subdomain.name}."
        
        # Otherwise trigger a full scan (simplified)
        else:
            # Full scans usually target a Domain
            from targetApp.models import Domain
            domain = Domain.objects.filter(project=project).first()
            if not domain:
                return f"Error: No domains found for project {project.name}."
                
            engine = EngineType.objects.filter(pk=arguments.get("engine_id")).first()
            if not engine:
                engine = EngineType.objects.filter(engine_name__icontains=scan_type).first()
            
            if not engine:
                 return f"Error: No suitable scan engine found for {scan_type}."
            
            # Create a scan history object first? initiate_scan usually expects one for live scans
            # For simplicity, we'll assume we want a standard trigger
            initiate_scan.delay(
                scan_history_id=None, # will be created if scan_type is SCHEDULED_SCAN but here we use LIVE_SCAN
                domain_id=domain.id,
                engine_id=engine.id
            )
            return f"Successfully triggered {scan_type} scan for {domain.name}."

    except Exception as e:
        logger.error(f"Failed to trigger scan: {e}")
        return f"Error triggering scan: {str(e)}"
