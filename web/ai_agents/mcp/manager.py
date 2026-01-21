"""MCP server connection manager for ReconAgent."""

import asyncio
import json
import os
import atexit
import signal
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .tools import create_mcp_tool
from .transport import MCPTransport, StdioTransport


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""

    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    description: str = ""
    # Whether to auto-start this server when `connect_all()` is called.
    start_on_launch: bool = False


@dataclass
class MCPServer:
    """Represents a connected MCP server."""

    name: str
    config: MCPServerConfig
    transport: MCPTransport
    tools: List[dict] = field(default_factory=list)
    connected: bool = False
    # Lock for serializing all communication with this server
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def disconnect(self):
        """Disconnect from the server."""
        if self.connected:
            await self.transport.disconnect()
            self.connected = False


class MCPManager:
    """Manages MCP server connections and exposes tools to agents."""

    DEFAULT_CONFIG_PATHS = [
        Path.cwd() / "mcp_servers.json",
        Path.cwd() / "mcp.json",
        Path(__file__).parent / "mcp_servers.json",
        Path.home() / ".reconpoint" / "mcp_servers.json",
    ]

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._find_config()
        self.servers: Dict[str, MCPServer] = {}
        # Track adapters we auto-started so we can stop them later
        self._started_adapters: Dict[str, object] = {}
        self._message_id = 0
        # Ensure we attempt to clean up vendored servers on process exit
        try:
            atexit.register(self._atexit_cleanup)
        except Exception:
            pass

    def _find_config(self) -> Path:
        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                return path
        return self.DEFAULT_CONFIG_PATHS[0]

    def _get_next_id(self) -> int:
        self._message_id += 1
        return self._message_id

    def _load_config(self) -> Dict[str, MCPServerConfig]:
        if not self.config_path.exists():
            return {}
        try:
            raw = json.loads(self.config_path.read_text(encoding="utf-8"))
            servers = {}
            mcp_servers = raw.get("mcpServers", {})
            for name, config in mcp_servers.items():
                if not config.get("command"):
                    continue
                servers[name] = MCPServerConfig(
                    name=name,
                    command=config["command"],
                    args=config.get("args", []),
                    env=config.get("env", {}),
                    enabled=config.get("enabled", True),
                    start_on_launch=config.get("start_on_launch", False),
                    description=config.get("description", ""),
                )
            return servers
        except json.JSONDecodeError as e:
            print(f"[MCP] Error loading config: {e}")
            return {}

    def _save_config(self, servers: Dict[str, MCPServerConfig]):
        config = {"mcpServers": {}}
        for name, server in servers.items():
            server_config = {"command": server.command, "args": server.args}
            if server.env:
                server_config["env"] = server.env
            if server.description:
                server_config["description"] = server.description
            if not server.enabled:
                server_config["enabled"] = False
            config["mcpServers"][name] = server_config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    def _atexit_cleanup(self):
        """Synchronous atexit cleanup that attempts to stop adapters and disconnect servers."""
        try:
            asyncio.run(self._stop_started_adapters_and_disconnect())
        except Exception:
            for adapter in list(self._started_adapters.values()):
                try:
                    stop_sync = getattr(adapter, "stop_sync", None)
                    if stop_sync:
                        try:
                            stop_sync()
                            continue
                        except Exception:
                            pass
                    pid = None
                    proc = getattr(adapter, "_process", None)
                    if proc is not None:
                        pid = getattr(proc, "pid", None)
                    if pid:
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except Exception:
                            try:
                                os.kill(pid, signal.SIGKILL)
                            except Exception:
                                pass
                except Exception:
                    pass

    async def _stop_started_adapters_and_disconnect(self) -> None:
        # Stop any adapters we started
        for name, adapter in list(self._started_adapters.items()):
            try:
                stop = getattr(adapter, "stop", None)
                if stop:
                    if asyncio.iscoroutinefunction(stop):
                        await stop()
                    else:
                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(None, stop)
            except Exception:
                pass
        self._started_adapters.clear()

        # Disconnect any active MCP server connections
        try:
            await self.disconnect_all()
        except Exception:
            pass

    def add_server(
        self,
        name: str,
        command: str,
        args: List[str] = None,
        env: Dict[str, str] = None,
        description: str = "",
    ):
        servers = self._load_config()
        servers[name] = MCPServerConfig(
            name=name,
            command=command,
            args=args or [],
            env=env or {},
            description=description,
        )
        self._save_config(servers)
        print(f"[MCP] Added server: {name}")

    def remove_server(self, name: str) -> bool:
        servers = self._load_config()
        if name in servers:
            del servers[name]
            self._save_config(servers)
            return True
        return False

    def list_configured_servers(self) -> List[dict]:
        servers = self._load_config()
        return [
            {
                "name": n,
                "command": s.command,
                "args": s.args,
                "env": s.env,
                "enabled": s.enabled,
                "description": s.description,
                "connected": n in self.servers and self.servers[n].connected,
            }
            for n, s in servers.items()
        ]

    async def connect_all(self) -> List[Any]:
        servers_config = self._load_config()
        all_tools = []
        for name, config in servers_config.items():
            if not config.enabled:
                continue
            
            server = await self._connect_server(config)
            if server:
                self.servers[name] = server
                for tool_def in server.tools:
                    tool = create_mcp_tool(tool_def, server, self)
                    all_tools.append(tool)
        return all_tools

    async def connect_server(self, name: str) -> Optional[MCPServer]:
        servers_config = self._load_config()
        if name not in servers_config:
            return None
        config = servers_config[name]
        server = await self._connect_server(config)
        if server:
            self.servers[name] = server
        return server

    async def _connect_server(self, config: MCPServerConfig) -> Optional[MCPServer]:
        transport = None
        try:
            env = {**os.environ, **config.env}
            
            # Simple stdio transport for now
            transport = StdioTransport(
                command=config.command, args=config.args, env=env
            )
            await transport.connect()

            await transport.send(
                {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "reconpoint", "version": "0.1.0"},
                    },
                    "id": self._get_next_id(),
                }
            )
            await transport.send(
                {"jsonrpc": "2.0", "method": "notifications/initialized"}
            )

            tools_response = await transport.send(
                {"jsonrpc": "2.0", "method": "tools/list", "id": self._get_next_id()}
            )
            tools = tools_response.get("result", {}).get("tools", [])

            return MCPServer(
                name=config.name,
                config=config,
                transport=transport,
                tools=tools,
                connected=True,
            )
        except Exception as e:
            if transport:
                try:
                    await transport.disconnect()
                except Exception:
                    pass
            print(f"[MCP] Failed to connect to {config.name}: {e}")
            return None

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> Any:
        server = self.servers.get(server_name)
        if not server or not server.connected:
            raise ValueError(f"Server '{server_name}' not connected")

        async with server._lock:
            response = await server.transport.send(
                {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                    "id": self._get_next_id(),
                },
                timeout=300.0,
            )
        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error'].get('message')}")
        return response.get("result", {}).get("content", [])

    async def disconnect_all(self):
        for server in list(self.servers.values()):
            await server.disconnect()
        self.servers.clear()
