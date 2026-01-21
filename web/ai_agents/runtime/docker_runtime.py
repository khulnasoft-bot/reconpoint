import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from .runtime import Runtime, CommandResult, detect_environment

logger = logging.getLogger(__name__)

class DockerRuntime(Runtime):
    """Runtime that executes commands inside ephemeral Docker containers."""

    def __init__(
        self, 
        image: str = "kalilinux/kali-rolling", 
        project_id: int = 0,
        mcp_manager: Optional[Any] = None
    ):
        super().__init__(mcp_manager)
        self.image = image
        self.project_id = project_id
        self._container_id: Optional[str] = None
        self._running = False
        self._loop = asyncio.get_event_policy().get_event_loop()

    async def start(self):
        """Start the Docker container."""
        if self._running:
            return

        # Ensure loot directory exists on host
        project_root = Path(__file__).parent.parent.parent.parent.parent
        self.host_loot_dir = project_root / "loot" / str(self.project_id)
        self.host_loot_dir.mkdir(parents=True, exist_ok=True)

        # Launch container
        command = [
            "docker", "run", "-d",
            "--rm",
            "--network", "none", # Security first: isolate by default
            "-v", f"{self.host_loot_dir}:/loot",
            "--name", f"reconpoint-worker-{self.project_id}-{os.urandom(4).hex()}",
            self.image,
            "tail", "-f", "/dev/null"
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Failed to start Docker container: {stderr.decode()}")

        self._container_id = stdout.decode().strip()
        self._running = True
        logger.info(f"Started Docker runtime container: {self._container_id}")

    async def stop(self):
        """Stop and remove the Docker container."""
        if not self._container_id:
            return

        command = ["docker", "stop", self._container_id]
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        self._container_id = None
        self._running = False

    async def execute_command(self, command: str, timeout: int = 300) -> CommandResult:
        """Execute command via 'docker exec'."""
        if not self._running or not self._container_id:
            await self.start()

        # Wrap command to use /loot as working directory if needed
        docker_command = [
            "docker", "exec",
            "-w", "/loot",
            self._container_id,
            "sh", "-c", command
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *docker_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            return CommandResult(
                exit_code=process.returncode or 0,
                stdout=stdout.decode(errors="replace"),
                stderr=stderr.decode(errors="replace")
            )
        except asyncio.TimeoutError:
            return CommandResult(
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout}s inside container"
            )
        except Exception as e:
            return CommandResult(exit_code=-1, stdout="", stderr=str(e))

    async def browser_action(self, action: str, **kwargs) -> dict:
        """Browser actions inside Docker (requires image with Playwright)."""
        # For now, fallback to local or suggest a browser-equipped image
        return {"error": "Browser actions not yet implemented in DockerRuntime. Use a Playwright-enabled image."}

    async def proxy_action(self, action: str, **kwargs) -> dict:
        return {"error": "Proxy actions not yet implemented in DockerRuntime."}

    async def is_running(self) -> bool:
        return self._running

    async def get_status(self) -> dict:
        return {
            "type": "docker",
            "container_id": self._container_id,
            "image": self.image,
            "running": self._running
        }
