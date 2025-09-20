#!/usr/bin/env python3
"""
Agent Configuration Validator

Validates that all agent configurations follow the required schema
and contain necessary fields for Claude Code integration.
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from jsonschema import validate, ValidationError


# Schema for agent configuration validation
AGENT_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["name", "description", "version", "claude_code"],
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[a-z][a-z0-9-]*$"
        },
        "description": {
            "type": "string",
            "minLength": 10
        },
        "version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$"
        },
        "claude_code": {
            "type": "object",
            "required": ["tools"],
            "properties": {
                "tools": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "Read", "Write", "Edit", "MultiEdit",
                            "Glob", "Grep", "Bash", "TodoWrite",
                            "WebFetch", "BashOutput", "KillShell"
                        ]
                    },
                    "minItems": 1
                },
                "permissions": {
                    "type": "object",
                    "properties": {
                        "read_access": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "write_access": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "tool_restrictions": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        },
        "capabilities": {
            "type": "array",
            "items": {"type": "string"}
        },
        "input_schema": {
            "type": "object"
        },
        "output_schema": {
            "type": "object"
        },
        "workflow": {
            "type": "object",
            "properties": {
                "triggers": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "dependencies": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "next_agents": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "outputs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["path", "format"],
                        "properties": {
                            "path": {"type": "string"},
                            "format": {"type": "string"}
                        }
                    }
                }
            }
        }
    },
    "additionalProperties": True
}


def validate_agent_config(config_path: Path) -> List[Dict[str, Any]]:
    """Validate a single agent configuration file."""
    errors = []

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Validate against schema
        try:
            validate(instance=config, schema=AGENT_CONFIG_SCHEMA)
        except ValidationError as e:
            errors.append({
                "type": "schema_validation",
                "message": f"Schema validation failed: {e.message}",
                "path": e.absolute_path
            })

        # Additional custom validations
        agent_name = config_path.parent.name

        # Check name matches directory
        if config.get("name") != agent_name:
            errors.append({
                "type": "name_mismatch",
                "message": f"Agent name '{config.get('name')}' doesn't match directory '{agent_name}'"
            })

        # Check for required tools based on agent type
        tools = config.get("claude_code", {}).get("tools", [])

        if "coder" in agent_name:
            required_tools = ["Read", "Write", "Edit"]
            missing_tools = [tool for tool in required_tools if tool not in tools]
            if missing_tools:
                errors.append({
                    "type": "missing_tools",
                    "message": f"Coder agent missing required tools: {missing_tools}"
                })

        if "reviewer" in agent_name:
            if "Read" not in tools:
                errors.append({
                    "type": "missing_tools",
                    "message": "Reviewer agent must have Read tool"
                })

        # Check permissions
        permissions = config.get("claude_code", {}).get("permissions", {})

        if "coder" in agent_name and not permissions.get("write_access"):
            errors.append({
                "type": "missing_permissions",
                "message": "Coder agent should have write_access permissions defined"
            })

        if "reviewer" in agent_name and permissions.get("write_access"):
            # Reviewers should generally be read-only except for reports
            write_paths = permissions.get("write_access", [])
            non_report_writes = [path for path in write_paths if not path.startswith("reports/")]
            if non_report_writes:
                errors.append({
                    "type": "excessive_permissions",
                    "message": f"Reviewer agent has write access to non-report paths: {non_report_writes}"
                })

        # Check workflow configuration
        workflow = config.get("workflow", {})
        if workflow:
            outputs = workflow.get("outputs", [])
            for output in outputs:
                path = output.get("path", "")
                if "{" in path and "}" in path:
                    # Template path - check for required variables
                    if "task_id" in path and "task_id" not in path:
                        errors.append({
                            "type": "invalid_template",
                            "message": f"Output path template missing task_id variable: {path}"
                        })

    except yaml.YAMLError as e:
        errors.append({
            "type": "yaml_error",
            "message": f"YAML parsing error: {str(e)}"
        })
    except FileNotFoundError:
        errors.append({
            "type": "file_not_found",
            "message": f"Configuration file not found: {config_path}"
        })
    except Exception as e:
        errors.append({
            "type": "unexpected_error",
            "message": f"Unexpected error: {str(e)}"
        })

    return errors


def validate_prompt_file(prompt_path: Path) -> List[Dict[str, Any]]:
    """Validate agent prompt file."""
    errors = []

    try:
        if not prompt_path.exists():
            errors.append({
                "type": "file_not_found",
                "message": f"Prompt file not found: {prompt_path}"
            })
            return errors

        with open(prompt_path, 'r') as f:
            content = f.read()

        # Check minimum content length
        if len(content) < 500:
            errors.append({
                "type": "insufficient_content",
                "message": "Prompt file appears to be too short (< 500 characters)"
            })

        # Check for required sections
        required_sections = [
            "Core Responsibilities",
            "Claude Code",
            "Tool Usage"
        ]

        for section in required_sections:
            if section not in content:
                errors.append({
                    "type": "missing_section",
                    "message": f"Prompt missing recommended section: {section}"
                })

        # Check for Claude Code integration mentions
        if "Claude Code" not in content:
            errors.append({
                "type": "missing_integration",
                "message": "Prompt should mention Claude Code integration"
            })

        # Check for tool usage instructions
        claude_tools = ["Read", "Write", "Edit", "Bash", "TodoWrite"]
        tool_mentions = sum(1 for tool in claude_tools if tool in content)

        if tool_mentions == 0:
            errors.append({
                "type": "missing_tool_guidance",
                "message": "Prompt should include guidance on Claude Code tool usage"
            })

    except Exception as e:
        errors.append({
            "type": "unexpected_error",
            "message": f"Error validating prompt file: {str(e)}"
        })

    return errors


def main():
    """Main validation function."""
    print("🔍 Validating agent configurations...")

    subagents_dir = Path("subagents")
    if not subagents_dir.exists():
        print("❌ Subagents directory not found")
        sys.exit(1)

    total_errors = 0
    total_warnings = 0
    agents_validated = 0

    # Find all agent directories
    agent_dirs = [d for d in subagents_dir.iterdir() if d.is_dir()]

    if not agent_dirs:
        print("❌ No agent directories found")
        sys.exit(1)

    for agent_dir in agent_dirs:
        agent_name = agent_dir.name
        print(f"\n📋 Validating agent: {agent_name}")

        config_path = agent_dir / "config.yaml"
        prompt_path = agent_dir / "prompt.md"

        # Validate configuration
        config_errors = validate_agent_config(config_path)
        prompt_errors = validate_prompt_file(prompt_path)

        all_errors = config_errors + prompt_errors

        if not all_errors:
            print(f"✅ {agent_name}: Configuration valid")
            agents_validated += 1
        else:
            error_count = len([e for e in all_errors if e["type"] in ["schema_validation", "yaml_error", "file_not_found"]])
            warning_count = len(all_errors) - error_count

            total_errors += error_count
            total_warnings += warning_count

            if error_count > 0:
                print(f"❌ {agent_name}: {error_count} errors, {warning_count} warnings")
            else:
                print(f"⚠️ {agent_name}: {warning_count} warnings")

            for error in all_errors:
                severity = "❌" if error["type"] in ["schema_validation", "yaml_error", "file_not_found"] else "⚠️"
                print(f"   {severity} {error['type']}: {error['message']}")

    # Summary
    print(f"\n📊 Validation Summary:")
    print(f"   Agents validated: {agents_validated}/{len(agent_dirs)}")
    print(f"   Total errors: {total_errors}")
    print(f"   Total warnings: {total_warnings}")

    if total_errors > 0:
        print(f"\n❌ Validation failed with {total_errors} errors")
        sys.exit(1)
    elif total_warnings > 0:
        print(f"\n⚠️ Validation passed with {total_warnings} warnings")
        print("   Consider addressing warnings for best practices")
    else:
        print(f"\n🎉 All agent configurations valid!")

    print("\n✅ Agent configuration validation completed successfully")


if __name__ == "__main__":
    main()