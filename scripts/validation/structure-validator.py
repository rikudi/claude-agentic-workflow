#!/usr/bin/env python3
"""
Repository Structure Validator

Validates that the agentic template repository maintains the required
structure and configuration files for proper multi-agent workflow operation.
"""

import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    level: ValidationLevel
    category: str
    message: str
    path: Optional[str] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "category": self.category,
            "message": self.message,
            "path": self.path,
            "suggestion": self.suggestion
        }


class StructureValidator:
    """Validates the repository structure and configuration."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.results: List[ValidationResult] = []

    def validate(self) -> Dict[str, Any]:
        """Run all validation checks and return results."""
        print("🔍 Validating repository structure...")

        # Clear previous results
        self.results = []

        # Run validation checks
        self._validate_directory_structure()
        self._validate_subagent_configs()
        self._validate_hook_scripts()
        self._validate_knowledge_base()
        self._validate_documentation()
        self._validate_scripts()
        self._validate_github_workflows()

        # Generate summary
        summary = self._generate_summary()

        return {
            "summary": summary,
            "results": [result.to_dict() for result in self.results],
            "valid": summary["errors"] == 0
        }

    def _validate_directory_structure(self):
        """Validate required directory structure."""
        required_dirs = [
            "subagents",
            "hooks",
            "docs",
            "reports",
            "scripts",
            "claude-code",
            ".github/workflows"
        ]

        for dir_path in required_dirs:
            full_path = self.root_path / dir_path
            if not full_path.exists():
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="structure",
                    message=f"Required directory missing: {dir_path}",
                    path=str(full_path),
                    suggestion=f"Create directory: mkdir -p {dir_path}"
                ))
            elif not full_path.is_dir():
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="structure",
                    message=f"Path exists but is not a directory: {dir_path}",
                    path=str(full_path),
                    suggestion=f"Remove file and create directory: rm {dir_path} && mkdir -p {dir_path}"
                ))

        # Validate subagent subdirectories
        subagents_dir = self.root_path / "subagents"
        if subagents_dir.exists():
            expected_subagents = [
                "planner",
                "plan-reviewer",
                "coder-frontend",
                "coder-backend",
                "coder-infra",
                "ui-reviewer",
                "code-reviewer"
            ]

            for agent in expected_subagents:
                agent_dir = subagents_dir / agent
                if not agent_dir.exists():
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="subagents",
                        message=f"Missing subagent directory: {agent}",
                        path=str(agent_dir),
                        suggestion=f"Create subagent directory: mkdir -p subagents/{agent}"
                    ))

        # Validate hook subdirectories
        hooks_dir = self.root_path / "hooks"
        if hooks_dir.exists():
            expected_hook_dirs = ["validation", "monitoring", "coordination"]

            for hook_dir in expected_hook_dirs:
                hook_path = hooks_dir / hook_dir
                if not hook_path.exists():
                    self.results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        category="hooks",
                        message=f"Missing hooks directory: {hook_dir}",
                        path=str(hook_path),
                        suggestion=f"Create hooks directory: mkdir -p hooks/{hook_dir}"
                    ))

    def _validate_subagent_configs(self):
        """Validate subagent configuration files."""
        subagents_dir = self.root_path / "subagents"
        if not subagents_dir.exists():
            return

        for agent_dir in subagents_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            agent_name = agent_dir.name

            # Check for required files
            config_file = agent_dir / "config.yaml"
            prompt_file = agent_dir / "prompt.md"

            if not config_file.exists():
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="subagent_config",
                    message=f"Missing config.yaml for agent: {agent_name}",
                    path=str(config_file),
                    suggestion=f"Create configuration file for {agent_name}"
                ))
                continue

            if not prompt_file.exists():
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="subagent_config",
                    message=f"Missing prompt.md for agent: {agent_name}",
                    path=str(prompt_file),
                    suggestion=f"Create prompt file for {agent_name}"
                ))

            # Validate config.yaml structure
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)

                self._validate_agent_config(agent_name, config, config_file)

            except yaml.YAMLError as e:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="subagent_config",
                    message=f"Invalid YAML in {agent_name} config: {str(e)}",
                    path=str(config_file),
                    suggestion="Fix YAML syntax errors"
                ))
            except Exception as e:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="subagent_config",
                    message=f"Error reading {agent_name} config: {str(e)}",
                    path=str(config_file),
                    suggestion="Check file permissions and content"
                ))

    def _validate_agent_config(self, agent_name: str, config: Dict[str, Any], config_path: Path):
        """Validate individual agent configuration."""
        required_fields = ["name", "description", "version", "claude_code"]

        for field in required_fields:
            if field not in config:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="subagent_config",
                    message=f"Missing required field '{field}' in {agent_name} config",
                    path=str(config_path),
                    suggestion=f"Add {field} field to configuration"
                ))

        # Validate Claude Code configuration
        if "claude_code" in config:
            claude_config = config["claude_code"]

            if "tools" not in claude_config:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="subagent_config",
                    message=f"Missing 'tools' in claude_code config for {agent_name}",
                    path=str(config_path),
                    suggestion="Add tools list to claude_code configuration"
                ))
            else:
                # Validate tools
                tools = claude_config["tools"]
                if not isinstance(tools, list):
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="subagent_config",
                        message=f"'tools' must be a list in {agent_name} config",
                        path=str(config_path),
                        suggestion="Convert tools to list format"
                    ))

            if "permissions" not in claude_config:
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="subagent_config",
                    message=f"Missing 'permissions' in claude_code config for {agent_name}",
                    path=str(config_path),
                    suggestion="Add permissions configuration for security"
                ))

        # Validate agent name matches directory
        if config.get("name") != agent_name:
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="subagent_config",
                message=f"Agent name '{config.get('name')}' doesn't match directory '{agent_name}'",
                path=str(config_path),
                suggestion=f"Update name field to '{agent_name}' or rename directory"
            ))

    def _validate_hook_scripts(self):
        """Validate hook scripts."""
        hooks_dir = self.root_path / "hooks"
        if not hooks_dir.exists():
            return

        expected_hooks = [
            "validation/plan-validation.py",
            "coordination/agent-handoff.py",
            "monitoring/progress-tracker.py"
        ]

        for hook_path in expected_hooks:
            full_path = hooks_dir / hook_path
            if not full_path.exists():
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="hooks",
                    message=f"Missing hook script: {hook_path}",
                    path=str(full_path),
                    suggestion=f"Create hook script: {hook_path}"
                ))
            elif not os.access(full_path, os.X_OK):
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="hooks",
                    message=f"Hook script not executable: {hook_path}",
                    path=str(full_path),
                    suggestion=f"Make executable: chmod +x {hook_path}"
                ))

    def _validate_knowledge_base(self):
        """Validate knowledge base documentation."""
        kb_dir = self.root_path / "docs" / "knowledge-base"
        if not kb_dir.exists():
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="knowledge_base",
                message="Knowledge base directory missing",
                path=str(kb_dir),
                suggestion="Create docs/knowledge-base directory"
            ))
            return

        expected_docs = [
            "claude-code-best-practices.md",
            "coding-standards.md",
            "testing-guidelines.md"
        ]

        for doc in expected_docs:
            doc_path = kb_dir / doc
            if not doc_path.exists():
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="knowledge_base",
                    message=f"Missing knowledge base document: {doc}",
                    path=str(doc_path),
                    suggestion=f"Create knowledge base document: {doc}"
                ))
            else:
                # Check if document is not empty
                if doc_path.stat().st_size == 0:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        category="knowledge_base",
                        message=f"Empty knowledge base document: {doc}",
                        path=str(doc_path),
                        suggestion=f"Add content to {doc}"
                    ))

    def _validate_documentation(self):
        """Validate main documentation files."""
        docs_dir = self.root_path / "docs"
        if not docs_dir.exists():
            return

        # Check for main documentation directories
        expected_dirs = ["plans", "decisions", "examples"]
        for dir_name in expected_dirs:
            dir_path = docs_dir / dir_name
            if not dir_path.exists():
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="documentation",
                    message=f"Missing documentation directory: docs/{dir_name}",
                    path=str(dir_path),
                    suggestion=f"Create directory: mkdir -p docs/{dir_name}"
                ))

        # Check README.md
        readme_path = self.root_path / "README.md"
        if not readme_path.exists():
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="documentation",
                message="Missing README.md file",
                path=str(readme_path),
                suggestion="Create comprehensive README.md"
            ))
        elif readme_path.stat().st_size < 100:  # Very minimal README
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="documentation",
                message="README.md appears to be minimal",
                path=str(readme_path),
                suggestion="Expand README.md with setup instructions and usage examples"
            ))

    def _validate_scripts(self):
        """Validate orchestration and utility scripts."""
        scripts_dir = self.root_path / "scripts"
        if not scripts_dir.exists():
            return

        expected_scripts = [
            "orchestration/workflow-orchestrator.py",
            "orchestration/claude-code-sdk-client.py",
            "validation/structure-validator.py"
        ]

        for script_path in expected_scripts:
            full_path = scripts_dir / script_path
            if not full_path.exists():
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="scripts",
                    message=f"Missing script: {script_path}",
                    path=str(full_path),
                    suggestion=f"Create script: {script_path}"
                ))

    def _validate_github_workflows(self):
        """Validate GitHub Actions workflows."""
        workflows_dir = self.root_path / ".github" / "workflows"
        if not workflows_dir.exists():
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="ci_cd",
                message="GitHub workflows directory missing",
                path=str(workflows_dir),
                suggestion="Create .github/workflows directory for CI/CD"
            ))
            return

        # Check for basic workflow files
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        if not workflow_files:
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="ci_cd",
                message="No GitHub workflow files found",
                path=str(workflows_dir),
                suggestion="Add GitHub Actions workflows for validation and testing"
            ))

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary."""
        errors = len([r for r in self.results if r.level == ValidationLevel.ERROR])
        warnings = len([r for r in self.results if r.level == ValidationLevel.WARNING])
        info = len([r for r in self.results if r.level == ValidationLevel.INFO])

        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {"errors": 0, "warnings": 0, "info": 0}
            categories[result.category][result.level.value + "s"] += 1

        return {
            "total_checks": len(self.results),
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "categories": categories,
            "status": "FAIL" if errors > 0 else "PASS" if warnings == 0 else "WARN"
        }

    def print_results(self, validation_result: Dict[str, Any]):
        """Print validation results in a human-readable format."""
        summary = validation_result["summary"]

        # Print header
        status_emoji = {
            "PASS": "✅",
            "WARN": "⚠️",
            "FAIL": "❌"
        }

        print(f"\n{status_emoji[summary['status']]} Validation Results: {summary['status']}")
        print(f"📊 Total: {summary['total_checks']} | "
              f"❌ Errors: {summary['errors']} | "
              f"⚠️ Warnings: {summary['warnings']} | "
              f"ℹ️ Info: {summary['info']}")

        # Print category breakdown
        if summary["categories"]:
            print("\n📋 Issues by Category:")
            for category, counts in summary["categories"].items():
                if counts["errors"] > 0 or counts["warnings"] > 0:
                    print(f"  {category}: {counts['errors']} errors, {counts['warnings']} warnings")

        # Print detailed results
        if validation_result["results"]:
            print("\n📝 Detailed Results:")

            # Group by level
            by_level = {"error": [], "warning": [], "info": []}
            for result in validation_result["results"]:
                by_level[result["level"]].append(result)

            # Print errors first
            for level in ["error", "warning", "info"]:
                results = by_level[level]
                if not results:
                    continue

                level_emoji = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}
                print(f"\n{level_emoji[level]} {level.upper()}S:")

                for result in results:
                    print(f"  • {result['message']}")
                    if result["path"]:
                        print(f"    Path: {result['path']}")
                    if result["suggestion"]:
                        print(f"    💡 {result['suggestion']}")
                    print()

        # Print conclusion
        if summary["status"] == "PASS":
            print("🎉 Repository structure validation passed!")
        elif summary["status"] == "WARN":
            print("⚠️ Repository structure validation passed with warnings.")
            print("   Consider addressing warnings for best practices.")
        else:
            print("❌ Repository structure validation failed.")
            print("   Please fix all errors before proceeding.")

        return summary["status"] == "PASS"


def main():
    """Main entry point for the structure validator."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate repository structure")
    parser.add_argument("--path", default=".", help="Path to repository root")
    parser.add_argument("--output", help="Output file for JSON results")
    parser.add_argument("--quiet", action="store_true", help="Only output summary")
    args = parser.parse_args()

    validator = StructureValidator(args.path)
    result = validator.validate()

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")

    # Print results unless quiet mode
    if not args.quiet:
        success = validator.print_results(result)
    else:
        success = result["summary"]["errors"] == 0
        print(f"Validation: {'PASS' if success else 'FAIL'}")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()