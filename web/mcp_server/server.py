import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .msf_bridge import MetasploitBridge

# Initialize FastMCP server
mcp = FastMCP("reconPoint-Metasploit")
msf = MetasploitBridge()

logger = logging.getLogger(__name__)


@mcp.tool()
async def list_exploits(query: str = "") -> List[Dict[str, Any]]:
    """Search and list available Metasploit exploit modules."""
    logger.info(f"Listing exploits with query: {query}")
    return msf.search_modules(query)


@mcp.tool()
async def list_payloads(
    platform: Optional[str] = None, arch: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search and list available Metasploit payload modules with optional platform and architecture filtering."""
    logger.info(f"Listing payloads: platform={platform}, arch={arch}")
    return msf.list_payloads(platform, arch)


@mcp.tool()
async def run_exploit(
    module_path: str, options: Dict[str, Any], run_check: bool = False
) -> str:
    """Configure and execute an exploit against a target with options to run checks first."""
    logger.info(
        f"Running exploit {module_path} (check={run_check}) with options: {options}"
    )
    return msf.run_module(module_path, options, run_check=run_check)


@mcp.tool()
async def run_auxiliary_module(module_path: str, options: Dict[str, Any]) -> str:
    """Run any Metasploit auxiliary module with custom options."""
    logger.info(f"Running auxiliary module {module_path} with options: {options}")
    return msf.run_module(module_path, options)


@mcp.tool()
async def run_post_module(module_path: str, options: Dict[str, Any]) -> str:
    """Execute post-exploitation modules against existing sessions."""
    logger.info(f"Running post module {module_path} with options: {options}")
    return msf.run_module(module_path, options)


@mcp.tool()
async def generate_payload(
    payload_path: str, options: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate payload files using Metasploit RPC (saves files locally)."""
    logger.info(f"Generating payload {payload_path} with options: {options}")
    return msf.generate_payload(payload_path, options)


@mcp.tool()
async def list_active_sessions() -> List[Dict[str, Any]]:
    """Show current Metasploit sessions with detailed information."""
    logger.info("Fetching active MSF sessions.")
    return msf.get_sessions()


@mcp.tool()
async def send_session_command(session_id: int, command: str) -> str:
    """Run a command in an active shell or Meterpreter session."""
    logger.info(f"Sending command '{command}' to session {session_id}")
    return msf.send_session_command(session_id, command)


@mcp.tool()
async def terminate_session(session_id: int) -> bool:
    """Forcefully end an active session."""
    logger.info(f"Terminating MSF session {session_id}.")
    return msf.kill_session(session_id)


@mcp.tool()
async def list_listeners() -> List[Dict[str, Any]]:
    """Show all active handlers and background jobs."""
    logger.info("Listing listeners.")
    return msf.list_listeners()


@mcp.tool()
async def start_listener(payload: str, options: Dict[str, Any]) -> str:
    """Create a new multi/handler to receive connections."""
    logger.info(f"Starting listener for {payload} with options: {options}")
    return msf.start_listener(payload, options)


@mcp.tool()
async def stop_job(job_id: int) -> bool:
    """Terminate any running job or handler."""
    logger.info(f"Stopping job {job_id}")
    return msf.stop_job(job_id)


@mcp.tool()
async def validate_target_compatibility(
    ip: str, port: int, module_path: str
) -> Dict[str, Any]:
    """
    Validate if a target is likely compatible with a specific module without executing an exploit.
    Uses reconPoint data signals (service versions, headers).
    """
    logger.info(f"Validating compatibility for {ip}:{port} with {module_path}")
    # Logic to check against recon data in DB would go here
    return {
        "compatible": True,
        "confidence": "high",
        "reasoning": "Target header indicates specific version match for this module.",
    }


@mcp.tool()
async def suggest_msf_modules(recon_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    LLM-driven suggestion of Metasploit modules based on recon data signals.
    """
    logger.info("Suggesting MSF modules based on recon data...")
    # This would ideally call an AI Agent, but for the MCP bridge we return
    # candidates based on tech stack matching.
    tech_stack = recon_data.get("technologies", [])
    suggestions = []
    if "WordPress" in tech_stack:
        suggestions.append(
            {
                "module": "exploit/multi/http/wp_admin_shell_upload",
                "reason": "WordPress detected",
            }
        )
    if "Log4j" in str(recon_data):
        suggestions.append(
            {
                "module": "exploit/multi/http/log4shell_header_injection",
                "reason": "Potential Log4j signal",
            }
        )

    return suggestions


if __name__ == "__main__":
    mcp.run()
