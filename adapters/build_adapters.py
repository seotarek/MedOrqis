"""
MedOrqis Platform Adapters Generator (v2.1.0)
Compiles and generates platform-specific configuration packages for:
1. Claude Code & Agent Skills
2. Gemini CLI Extension (with commands/*.toml)
3. OpenAI API & Strict Structured Function Calling
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

def build_claude_adapter():
    """Generates Claude Code plugin manifest and skill bindings."""
    claude_dir = os.path.join(BASE_DIR, "adapters", "claude")
    os.makedirs(claude_dir, exist_ok=True)

    manifest = {
        "name": "medorqis-claude-skills",
        "version": "2.1.0",
        "description": "Evidence-grounded medical AI skills ecosystem for Claude Code.",
        "skills_directory": "../../skills",
        "skills_count": 24,
        "entrypoint_skill": "medorqis-orchestrator",
        "mcp_server_config": {
            "medorqis_core": {
                "command": "python3",
                "args": ["mcp_server/medorqis_mcp_server.py"]
            }
        }
    }
    with open(os.path.join(claude_dir, "claude-skill-package.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("Claude Code adapter generated.")


def build_gemini_adapter():
    """Generates Gemini CLI Extension (gemini-extension.json + GEMINI.md + commands/*.toml)."""
    gemini_dir = os.path.join(BASE_DIR, "adapters", "gemini")
    commands_dir = os.path.join(gemini_dir, "commands")
    os.makedirs(commands_dir, exist_ok=True)

    # 1. commands/clinical-calc.toml
    calc_toml = """name = "clinical-calc"
description = "Execute deterministic clinical calculators via MedOrqis MCP."
prompt = "Invoke the calculate_clinical_score tool with the specified calculator_id and parameters."
"""
    with open(os.path.join(commands_dir, "clinical-calc.toml"), "w", encoding="utf-8") as f:
        f.write(calc_toml)

    # 2. commands/triage.toml
    triage_toml = """name = "triage"
description = "Screen for clinical emergency red flags and lethal contraindications."
prompt = "Invoke the check_red_flags tool with patient clinical context."
"""
    with open(os.path.join(commands_dir, "triage.toml"), "w", encoding="utf-8") as f:
        f.write(triage_toml)

    manifest = {
        "name": "medorqis-gemini-extension",
        "version": "2.1.0",
        "description": "MedOrqis Medical AI Skills Ecosystem extension for Gemini CLI.",
        "contextFileName": "GEMINI.md",
        "mcpServers": {
            "medorqis_mcp": {
                "command": "python3",
                "args": ["${extensionPath}/mcp_server/medorqis_mcp_server.py"]
            }
        },
        "commands": [
            {
                "name": "clinical-calc",
                "description": "Run deterministic clinical calculation via MedOrqis MCP."
            },
            {
                "name": "triage",
                "description": "Screen for clinical emergency red flags."
            }
        ]
    }
    with open(os.path.join(gemini_dir, "gemini-extension.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    gemini_md = """# MedOrqis Gemini CLI Extension Context (v2.1.0)

You are connected to the **MedOrqis Medical AI Skills Ecosystem**.
All medical decision support tasks must adhere to:
1. **Zero-Hallucination Epistemic Provenance**: Never accept unverified hypotheses as confirmed indications for high-risk therapy.
2. **Deterministic Calculators**: Always invoke `calculate_clinical_score` via the connected `medorqis_mcp` server. Do not estimate clinical scores with free-text arithmetic.
3. **Emergency Redirection**: If acute red flags (ACS, stroke, sepsis, meningococcemia, ruptured ectopic, active suicide plan) are present, trigger immediate emergency medical redirection.
4. **Drug Interaction Verification**: Cross-reference active patient medications against `check_drug_interactions` before suggesting pharmaceutical interventions.
"""
    with open(os.path.join(gemini_dir, "GEMINI.md"), "w", encoding="utf-8") as f:
        f.write(gemini_md)

    print("Gemini CLI extension adapter generated.")


def build_openai_adapter():
    """Generates OpenAI Strict Structured Function Calling definitions."""
    openai_dir = os.path.join(BASE_DIR, "adapters", "openai")
    os.makedirs(os.path.join(openai_dir, "assistant_configs"), exist_ok=True)

    from mcp_server.medorqis_mcp_server import TOOLS_REGISTRY

    openai_functions = []
    for tool in TOOLS_REGISTRY:
        schema = dict(tool["inputSchema"])
        schema["additionalProperties"] = False
        # In OpenAI strict mode, all defined properties must be listed in required
        if "properties" in schema:
            schema["required"] = list(schema["properties"].keys())

        openai_functions.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "strict": True,
                "parameters": schema
            }
        })

    with open(os.path.join(openai_dir, "openai_functions.json"), "w", encoding="utf-8") as f:
        json.dump({"tools": openai_functions}, f, indent=2)

    assistant_config = {
        "name": "MedOrqis Clinical Assistant",
        "version": "2.1.0",
        "model": "gpt-4o",
        "instructions": "You are a clinical decision support assistant governed by MedOrqis safety rules. Always invoke the provided tools for scores, evidence verification, and safety screening.",
        "tools": openai_functions
    }
    with open(os.path.join(openai_dir, "assistant_configs", "medorqis_assistant.json"), "w", encoding="utf-8") as f:
        json.dump(assistant_config, f, indent=2)

    print("OpenAI adapter generated with Strict Structured Outputs.")


if __name__ == "__main__":
    build_claude_adapter()
    build_gemini_adapter()
    build_openai_adapter()
