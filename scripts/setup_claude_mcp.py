import os
import json
import sys

def setup_claude_mcp():
    config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Base configuration
    config = {
        "mcpServers": {
            "reconPoint-Metasploit": {
                "command": "python3",
                "args": [
                    os.path.abspath("web/mcp_server/server.py")
                ],
                "env": {
                    "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", "YOUR_KEY_HERE")
                }
            }
        }
    }
    
    # Load existing config if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                existing_config = json.load(f)
                if "mcpServers" not in existing_config:
                    existing_config["mcpServers"] = {}
                existing_config["mcpServers"].update(config["mcpServers"])
                config = existing_config
        except Exception as e:
            print(f"Warning: Could not read existing config: {e}")

    # Write config
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print(f"✅ Successfully updated Claude Desktop config at: {config_path}")
        print("Please restart Claude Desktop to see the new tools.")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")

if __name__ == "__main__":
    setup_claude_mcp()
