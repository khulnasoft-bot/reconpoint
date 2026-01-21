import os
import sys

import django

# Setup Django environment
sys.path.append("/Users/seamless/projects/reconpoint/web")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reconPoint.settings")
# django.setup() # Uncomment if running in a real environment with DB access

from ai_agents.manager import AIReasoningManager


def test_ai_flow():
    mock_recon_data = {
        "domain": "example.com",
        "subdomains": [
            {
                "name": "api.example.com",
                "ip": "1.2.3.4",
                "ports": [80, 443],
                "tech": ["Nginx", "Node.js"],
            },
            {
                "name": "dev.example.com",
                "ip": "1.2.3.5",
                "ports": [8080, 22],
                "tech": ["Apache", "Jenkins"],
            },
            {
                "name": "staging.example.com",
                "ip": "1.2.3.6",
                "ports": [443],
                "tech": ["IIS 10.0"],
            },
        ],
        "vulnerabilities": [
            {
                "name": "Outdated Jenkins",
                "severity": "High",
                "target": "dev.example.com",
            }
        ],
    }

    print("--- Initializing AI Manager ---")
    manager = AIReasoningManager()

    print("--- Running Full Analysis ---")
    # Note: This will attempt to call OpenAI API.
    # In a real environment, you'd need the API key set in settings.
    try:
        results = manager.perform_full_analysis(mock_recon_data)

        print("\n=== RECON ANALYSIS ===")
        print(results["recon_analysis"])

        print("\n=== ATTACK HYPOTHESES ===")
        print(results["attack_hypotheses"])

        print("\n=== RISK ASSESSMENT ===")
        print(results["risk_assessment"])

        print("\n=== FINAL REPORT ===")
        print(results["final_report"])

    except Exception as e:
        print(f"Error during analysis: {e}")
        print("Note: Ensure OPENAI_API_KEY is configured in Django settings.")


if __name__ == "__main__":
    test_ai_flow()
