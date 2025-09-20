#!/usr/bin/env python3
"""
Plan Validation Hook for Claude Code
Validates plan structure and completeness before approval
"""

import json
import sys
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any

def validate_plan_structure(plan_data: Dict[str, Any]) -> List[str]:
    """Validate that the plan has all required fields"""
    errors = []

    required_fields = [
        'plan_id', 'phases', 'architecture', 'risks'
    ]

    for field in required_fields:
        if field not in plan_data:
            errors.append(f"Missing required field: {field}")

    # Validate phases structure
    if 'phases' in plan_data:
        for i, phase in enumerate(plan_data['phases']):
            phase_errors = validate_phase_structure(phase, i)
            errors.extend(phase_errors)

    return errors

def validate_phase_structure(phase: Dict[str, Any], phase_index: int) -> List[str]:
    """Validate individual phase structure"""
    errors = []
    prefix = f"Phase {phase_index}"

    required_phase_fields = ['phase_id', 'name', 'tasks']
    for field in required_phase_fields:
        if field not in phase:
            errors.append(f"{prefix}: Missing required field: {field}")

    # Validate tasks
    if 'tasks' in phase:
        for j, task in enumerate(phase['tasks']):
            task_errors = validate_task_structure(task, phase_index, j)
            errors.extend(task_errors)

    return errors

def validate_task_structure(task: Dict[str, Any], phase_index: int, task_index: int) -> List[str]:
    """Validate individual task structure"""
    errors = []
    prefix = f"Phase {phase_index}, Task {task_index}"

    required_task_fields = [
        'task_id', 'title', 'description', 'assigned_agent',
        'success_criteria', 'estimated_effort'
    ]

    for field in required_task_fields:
        if field not in task:
            errors.append(f"{prefix}: Missing required field: {field}")

    # Validate agent assignment
    if 'assigned_agent' in task:
        valid_agents = [
            'coder-frontend', 'coder-backend', 'coder-infra',
            'ui-reviewer', 'code-reviewer'
        ]
        if task['assigned_agent'] not in valid_agents:
            errors.append(f"{prefix}: Invalid agent '{task['assigned_agent']}'. Must be one of: {valid_agents}")

    # Validate success criteria
    if 'success_criteria' in task:
        if not isinstance(task['success_criteria'], list) or len(task['success_criteria']) == 0:
            errors.append(f"{prefix}: Success criteria must be a non-empty list")

    return errors

def check_dependency_cycles(plan_data: Dict[str, Any]) -> List[str]:
    """Check for circular dependencies in tasks"""
    errors = []
    task_dependencies = {}

    # Build dependency graph
    for phase in plan_data.get('phases', []):
        for task in phase.get('tasks', []):
            task_id = task.get('task_id')
            dependencies = task.get('dependencies', [])
            if task_id:
                task_dependencies[task_id] = dependencies

    # Simple cycle detection using DFS
    visited = set()
    rec_stack = set()

    def has_cycle(node: str) -> bool:
        if node in rec_stack:
            return True
        if node in visited:
            return False

        visited.add(node)
        rec_stack.add(node)

        for dependency in task_dependencies.get(node, []):
            if has_cycle(dependency):
                return True

        rec_stack.remove(node)
        return False

    for task_id in task_dependencies:
        if task_id not in visited and has_cycle(task_id):
            errors.append(f"Circular dependency detected involving task: {task_id}")

    return errors

def main():
    """Main hook execution"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "allow": False,
            "message": "Plan validation hook requires a plan file path"
        }))
        sys.exit(1)

    plan_file = sys.argv[1]

    if not os.path.exists(plan_file):
        print(json.dumps({
            "allow": False,
            "message": f"Plan file not found: {plan_file}"
        }))
        sys.exit(1)

    try:
        # Load plan file (support both JSON and YAML)
        with open(plan_file, 'r') as f:
            if plan_file.endswith('.yaml') or plan_file.endswith('.yml'):
                plan_data = yaml.safe_load(f)
            else:
                plan_data = json.load(f)

        # Validate plan structure
        errors = []
        errors.extend(validate_plan_structure(plan_data))
        errors.extend(check_dependency_cycles(plan_data))

        if errors:
            print(json.dumps({
                "allow": False,
                "message": "Plan validation failed",
                "errors": errors
            }))
            sys.exit(1)
        else:
            print(json.dumps({
                "allow": True,
                "message": "Plan validation passed"
            }))
            sys.exit(0)

    except Exception as e:
        print(json.dumps({
            "allow": False,
            "message": f"Error validating plan: {str(e)}"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()