#!/usr/bin/env python3
"""
Agent Handoff Hook for Claude Code
Manages task assignment and coordination between agents
"""

import json
import sys
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class AgentCoordinator:
    def __init__(self):
        self.agents_dir = Path(__file__).parent.parent.parent / "subagents"
        self.reports_dir = Path(__file__).parent.parent.parent / "reports"

    def load_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Load agent configuration"""
        config_path = self.agents_dir / agent_name / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return None

    def check_agent_availability(self, agent_name: str) -> bool:
        """Check if an agent is available for task assignment"""
        # Check if agent configuration exists
        config = self.load_agent_config(agent_name)
        if not config:
            return False

        # Check if agent is not already overloaded
        # (This could be extended to check actual workload)
        return True

    def validate_task_assignment(self, task: Dict[str, Any], agent_name: str) -> List[str]:
        """Validate that a task can be assigned to the specified agent"""
        errors = []

        # Check agent availability
        if not self.check_agent_availability(agent_name):
            errors.append(f"Agent {agent_name} is not available or does not exist")
            return errors

        # Load agent config to check capabilities
        config = self.load_agent_config(agent_name)
        if not config:
            errors.append(f"Could not load configuration for agent {agent_name}")
            return errors

        # Check if required tools are available to the agent
        required_tools = task.get('required_tools', [])
        agent_tools = config.get('claude_code', {}).get('tools', [])

        for tool in required_tools:
            if tool not in agent_tools:
                errors.append(f"Agent {agent_name} does not have access to required tool: {tool}")

        # Check if task type matches agent capabilities
        agent_capabilities = config.get('capabilities', [])
        task_description = task.get('description', '').lower()

        # Simple capability matching (could be enhanced with NLP)
        capability_match = False
        for capability in agent_capabilities:
            if any(keyword in task_description for keyword in capability.lower().split()):
                capability_match = True
                break

        if not capability_match and agent_capabilities:
            errors.append(f"Task may not match agent {agent_name} capabilities")

        return errors

    def create_task_handoff(self, task: Dict[str, Any], from_agent: str, to_agent: str) -> Dict[str, Any]:
        """Create a task handoff record"""
        handoff = {
            "handoff_id": f"handoff-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task": task,
            "status": "pending",
            "context": {
                "dependencies_met": self.check_dependencies(task),
                "required_tools": task.get('required_tools', []),
                "success_criteria": task.get('success_criteria', [])
            }
        }

        # Save handoff record
        handoff_file = self.reports_dir / "implementation" / f"{handoff['handoff_id']}.json"
        handoff_file.parent.mkdir(parents=True, exist_ok=True)

        with open(handoff_file, 'w') as f:
            json.dump(handoff, f, indent=2)

        return handoff

    def check_dependencies(self, task: Dict[str, Any]) -> bool:
        """Check if task dependencies are satisfied"""
        dependencies = task.get('dependencies', [])

        # Check if dependency tasks are completed
        for dep_id in dependencies:
            # Look for completion records in reports
            completion_files = list((self.reports_dir / "implementation").glob(f"*{dep_id}*-completed.json"))
            if not completion_files:
                return False

        return True

    def generate_agent_context(self, agent_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate context information for the receiving agent"""
        config = self.load_agent_config(agent_name)

        context = {
            "agent_name": agent_name,
            "task_summary": {
                "id": task.get('task_id'),
                "title": task.get('title'),
                "description": task.get('description'),
                "estimated_effort": task.get('estimated_effort')
            },
            "available_tools": config.get('claude_code', {}).get('tools', []),
            "permissions": config.get('claude_code', {}).get('permissions', {}),
            "success_criteria": task.get('success_criteria', []),
            "dependencies": task.get('dependencies', []),
            "deliverables": task.get('deliverables', []),
            "context_files": self.find_relevant_files(task),
            "related_documentation": self.find_related_docs(task)
        }

        return context

    def find_relevant_files(self, task: Dict[str, Any]) -> List[str]:
        """Find files relevant to the task"""
        # This is a simplified implementation
        # In practice, this could use more sophisticated file analysis
        relevant_files = []

        task_desc = task.get('description', '').lower()

        # Look for file patterns mentioned in task description
        if 'frontend' in task_desc or 'ui' in task_desc:
            relevant_files.extend(['**/*.tsx', '**/*.jsx', '**/*.vue', '**/*.css'])
        if 'backend' in task_desc or 'api' in task_desc:
            relevant_files.extend(['**/*.py', '**/*.js', '**/*.ts', '**/api/**/*'])
        if 'database' in task_desc or 'db' in task_desc:
            relevant_files.extend(['**/*.sql', '**/migrations/**/*', '**/models/**/*'])

        return relevant_files

    def find_related_docs(self, task: Dict[str, Any]) -> List[str]:
        """Find documentation related to the task"""
        docs_dir = Path(__file__).parent.parent.parent / "docs"
        related_docs = []

        if docs_dir.exists():
            # Look for relevant documentation files
            for doc_file in docs_dir.rglob("*.md"):
                # Simple relevance check based on filename and content
                if any(keyword in doc_file.name.lower() for keyword in
                       task.get('description', '').lower().split()):
                    related_docs.append(str(doc_file.relative_to(docs_dir.parent)))

        return related_docs

def main():
    """Main hook execution"""
    if len(sys.argv) < 4:
        print(json.dumps({
            "allow": False,
            "message": "Agent handoff hook requires: <task_json> <from_agent> <to_agent>"
        }))
        sys.exit(1)

    try:
        task_json = sys.argv[1]
        from_agent = sys.argv[2]
        to_agent = sys.argv[3]

        # Parse task data
        task = json.loads(task_json)

        coordinator = AgentCoordinator()

        # Validate the task assignment
        errors = coordinator.validate_task_assignment(task, to_agent)

        if errors:
            print(json.dumps({
                "allow": False,
                "message": "Task assignment validation failed",
                "errors": errors
            }))
            sys.exit(1)

        # Create handoff record
        handoff = coordinator.create_task_handoff(task, from_agent, to_agent)

        # Generate context for receiving agent
        context = coordinator.generate_agent_context(to_agent, task)

        print(json.dumps({
            "allow": True,
            "message": f"Task successfully handed off to {to_agent}",
            "handoff_id": handoff["handoff_id"],
            "context": context
        }))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({
            "allow": False,
            "message": f"Error in agent handoff: {str(e)}"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()