#!/usr/bin/env python3
"""
Multi-Agent Workflow Orchestrator for Claude Code

This script orchestrates the execution of multiple Claude Code subagents
in a coordinated workflow for software development tasks.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from hooks.coordination.agent_handoff import AgentCoordinator
from hooks.monitoring.progress_tracker import ProgressTracker


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class AgentType(Enum):
    PLANNER = "planner"
    PLAN_REVIEWER = "plan-reviewer"
    CODER_FRONTEND = "coder-frontend"
    CODER_BACKEND = "coder-backend"
    CODER_INFRA = "coder-infra"
    UI_REVIEWER = "ui-reviewer"
    CODE_REVIEWER = "code-reviewer"


@dataclass
class Task:
    task_id: str
    title: str
    description: str
    assigned_agent: AgentType
    dependencies: List[str]
    estimated_effort: str
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['assigned_agent'] = self.assigned_agent.value
        data['status'] = self.status.value
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data


@dataclass
class WorkflowPlan:
    plan_id: str
    title: str
    description: str
    phases: List[Dict[str, Any]]
    tasks: List[Task]
    created_at: datetime
    status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['tasks'] = [task.to_dict() for task in self.tasks]
        data['created_at'] = self.created_at.isoformat()
        return data


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows for software development."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.agent_coordinator = AgentCoordinator()
        self.progress_tracker = ProgressTracker()
        self.active_workflows: Dict[str, WorkflowPlan] = {}
        self.results_dir = Path("reports/orchestration")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load orchestrator configuration."""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)

        # Default configuration
        return {
            "max_concurrent_agents": 3,
            "task_timeout_minutes": 60,
            "retry_attempts": 2,
            "agent_configs": {
                agent.value: f"subagents/{agent.value}/config.yaml"
                for agent in AgentType
            }
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/orchestrator.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)

    async def execute_workflow(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete multi-agent workflow."""
        workflow_id = f"workflow-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.logger.info(f"Starting workflow {workflow_id}")

        try:
            # Phase 1: Planning
            plan = await self._execute_planning_phase(workflow_id, requirements)
            if not plan:
                return {"status": "failed", "error": "Planning phase failed"}

            # Phase 2: Plan Review
            review_result = await self._execute_plan_review_phase(plan)
            if review_result["status"] != "approved":
                return {"status": "failed", "error": "Plan review failed", "review": review_result}

            # Phase 3: Implementation
            implementation_result = await self._execute_implementation_phase(plan)

            # Phase 4: Quality Assurance
            qa_result = await self._execute_qa_phase(plan, implementation_result)

            # Generate final report
            final_result = await self._generate_workflow_report(
                workflow_id, plan, implementation_result, qa_result
            )

            self.logger.info(f"Workflow {workflow_id} completed successfully")
            return final_result

        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            return {
                "status": "failed",
                "workflow_id": workflow_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _execute_planning_phase(self, workflow_id: str, requirements: Dict[str, Any]) -> Optional[WorkflowPlan]:
        """Execute the planning phase using the planner agent."""
        self.logger.info("Executing planning phase")

        try:
            # Invoke planner agent through Claude Code
            planner_input = {
                "requirements": requirements,
                "workflow_id": workflow_id,
                "constraints": self.config.get("planning_constraints", {})
            }

            # This would be replaced with actual Claude Code agent invocation
            plan_result = await self._invoke_claude_code_agent(
                AgentType.PLANNER,
                planner_input
            )

            if plan_result["status"] == "success":
                # Convert plan result to WorkflowPlan object
                plan_data = plan_result["plan"]
                tasks = [
                    Task(
                        task_id=task["task_id"],
                        title=task["title"],
                        description=task["description"],
                        assigned_agent=AgentType(task["assigned_agent"]),
                        dependencies=task.get("dependencies", []),
                        estimated_effort=task.get("estimated_effort", "unknown")
                    )
                    for phase in plan_data["phases"]
                    for task in phase["tasks"]
                ]

                plan = WorkflowPlan(
                    plan_id=plan_data["plan_id"],
                    title=plan_data.get("title", "Workflow Plan"),
                    description=plan_data.get("description", ""),
                    phases=plan_data["phases"],
                    tasks=tasks,
                    created_at=datetime.now()
                )

                self.active_workflows[workflow_id] = plan
                await self._save_plan(plan)
                return plan

        except Exception as e:
            self.logger.error(f"Planning phase failed: {str(e)}")

        return None

    async def _execute_plan_review_phase(self, plan: WorkflowPlan) -> Dict[str, Any]:
        """Execute plan review phase using the plan-reviewer agent."""
        self.logger.info(f"Reviewing plan {plan.plan_id}")

        try:
            review_input = {
                "plan": plan.to_dict(),
                "review_criteria": self.config.get("review_criteria", {})
            }

            review_result = await self._invoke_claude_code_agent(
                AgentType.PLAN_REVIEWER,
                review_input
            )

            # Save review results
            review_file = self.results_dir / f"{plan.plan_id}-review.json"
            with open(review_file, 'w') as f:
                json.dump(review_result, f, indent=2)

            return review_result

        except Exception as e:
            self.logger.error(f"Plan review failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def _execute_implementation_phase(self, plan: WorkflowPlan) -> Dict[str, Any]:
        """Execute implementation phase with parallel task execution."""
        self.logger.info("Starting implementation phase")

        completed_tasks = []
        failed_tasks = []
        task_results = {}

        # Execute tasks in dependency order
        remaining_tasks = plan.tasks.copy()
        max_concurrent = self.config["max_concurrent_agents"]

        while remaining_tasks:
            # Find tasks with satisfied dependencies
            ready_tasks = [
                task for task in remaining_tasks
                if all(dep in [t.task_id for t in completed_tasks] for dep in task.dependencies)
            ]

            if not ready_tasks:
                # Check for circular dependencies or unsatisfiable conditions
                self.logger.error("No ready tasks found - possible circular dependencies")
                break

            # Execute ready tasks in parallel (up to max_concurrent)
            batch_tasks = ready_tasks[:max_concurrent]
            batch_results = await asyncio.gather(
                *[self._execute_task(task) for task in batch_tasks],
                return_exceptions=True
            )

            # Process results
            for task, result in zip(batch_tasks, batch_results):
                remaining_tasks.remove(task)

                if isinstance(result, Exception):
                    self.logger.error(f"Task {task.task_id} failed: {str(result)}")
                    task.status = TaskStatus.FAILED
                    task.error = str(result)
                    failed_tasks.append(task)
                elif result["status"] == "success":
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now()
                    task.result = result
                    completed_tasks.append(task)
                    task_results[task.task_id] = result
                else:
                    task.status = TaskStatus.FAILED
                    task.error = result.get("error", "Unknown error")
                    failed_tasks.append(task)

        return {
            "status": "completed" if not failed_tasks else "partial",
            "completed_tasks": [task.to_dict() for task in completed_tasks],
            "failed_tasks": [task.to_dict() for task in failed_tasks],
            "task_results": task_results,
            "total_tasks": len(plan.tasks),
            "success_rate": len(completed_tasks) / len(plan.tasks) * 100
        }

    async def _execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a single task using the appropriate agent."""
        self.logger.info(f"Executing task {task.task_id} with agent {task.assigned_agent.value}")

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()

        # Track task start
        await self.progress_tracker.track_task_start(
            task.task_id,
            task.assigned_agent.value,
            task.to_dict()
        )

        try:
            # Prepare task input
            task_input = {
                "task": task.to_dict(),
                "context": await self._get_task_context(task),
                "project_config": self.config.get("project_config", {})
            }

            # Invoke Claude Code agent
            result = await self._invoke_claude_code_agent(
                task.assigned_agent,
                task_input
            )

            # Track task completion
            if result["status"] == "success":
                await self.progress_tracker.track_task_completion(
                    task.task_id,
                    result.get("completion_data", {})
                )
            else:
                await self.progress_tracker.track_task_blocked(
                    task.task_id,
                    {"error": result.get("error", "Unknown error")}
                )

            return result

        except Exception as e:
            await self.progress_tracker.track_task_blocked(
                task.task_id,
                {"error": str(e)}
            )
            raise

    async def _execute_qa_phase(self, plan: WorkflowPlan, implementation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute quality assurance phase."""
        self.logger.info("Starting QA phase")

        qa_results = {}

        # UI Review (if frontend tasks were completed)
        frontend_tasks = [t for t in plan.tasks if t.assigned_agent == AgentType.CODER_FRONTEND]
        if frontend_tasks and implementation_result["status"] != "failed":
            ui_review_result = await self._invoke_claude_code_agent(
                AgentType.UI_REVIEWER,
                {
                    "tasks": [t.to_dict() for t in frontend_tasks],
                    "implementation_results": implementation_result["task_results"]
                }
            )
            qa_results["ui_review"] = ui_review_result

        # Code Review (for all implementation tasks)
        if implementation_result["completed_tasks"]:
            code_review_result = await self._invoke_claude_code_agent(
                AgentType.CODE_REVIEWER,
                {
                    "tasks": implementation_result["completed_tasks"],
                    "implementation_results": implementation_result["task_results"]
                }
            )
            qa_results["code_review"] = code_review_result

        return qa_results

    async def _invoke_claude_code_agent(self, agent_type: AgentType, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a Claude Code agent (placeholder for actual implementation)."""
        # This is a placeholder for the actual Claude Code agent invocation
        # In a real implementation, this would use the Claude Code SDK/API

        self.logger.info(f"Invoking agent {agent_type.value}")

        # Simulate agent processing time
        await asyncio.sleep(1)

        # Mock successful response
        return {
            "status": "success",
            "agent": agent_type.value,
            "timestamp": datetime.now().isoformat(),
            "result": f"Mock result from {agent_type.value}",
            "execution_time": 1.0
        }

    async def _get_task_context(self, task: Task) -> Dict[str, Any]:
        """Get context information for task execution."""
        return {
            "task_id": task.task_id,
            "dependencies": task.dependencies,
            "related_files": await self._find_related_files(task),
            "project_structure": await self._get_project_structure(),
            "existing_patterns": await self._find_existing_patterns(task)
        }

    async def _find_related_files(self, task: Task) -> List[str]:
        """Find files related to the task."""
        # Implementation would use file analysis
        return []

    async def _get_project_structure(self) -> Dict[str, Any]:
        """Get current project structure."""
        # Implementation would analyze project structure
        return {}

    async def _find_existing_patterns(self, task: Task) -> List[str]:
        """Find existing code patterns relevant to the task."""
        # Implementation would analyze existing code
        return []

    async def _save_plan(self, plan: WorkflowPlan):
        """Save plan to filesystem."""
        plan_file = Path(f"docs/plans/{plan.plan_id}")
        plan_file.mkdir(parents=True, exist_ok=True)

        # Save as JSON
        with open(plan_file / "plan.json", 'w') as f:
            json.dump(plan.to_dict(), f, indent=2)

        # Save as Markdown
        markdown_content = self._generate_plan_markdown(plan)
        with open(plan_file / "plan.md", 'w') as f:
            f.write(markdown_content)

    def _generate_plan_markdown(self, plan: WorkflowPlan) -> str:
        """Generate markdown representation of the plan."""
        content = f"""# {plan.title}

**Plan ID**: {plan.plan_id}
**Created**: {plan.created_at.isoformat()}
**Status**: {plan.status}

## Description
{plan.description}

## Phases

"""
        for i, phase in enumerate(plan.phases, 1):
            content += f"### Phase {i}: {phase.get('name', 'Unnamed Phase')}\n\n"
            content += f"{phase.get('description', 'No description provided.')}\n\n"

        content += "## Tasks\n\n"
        for task in plan.tasks:
            content += f"### {task.task_id}: {task.title}\n\n"
            content += f"- **Assigned Agent**: {task.assigned_agent.value}\n"
            content += f"- **Status**: {task.status.value}\n"
            content += f"- **Estimated Effort**: {task.estimated_effort}\n"
            if task.dependencies:
                content += f"- **Dependencies**: {', '.join(task.dependencies)}\n"
            content += f"\n{task.description}\n\n"

        return content

    async def _generate_workflow_report(
        self,
        workflow_id: str,
        plan: WorkflowPlan,
        implementation_result: Dict[str, Any],
        qa_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive workflow report."""
        report = {
            "workflow_id": workflow_id,
            "plan_id": plan.plan_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tasks": len(plan.tasks),
                "completed_tasks": len(implementation_result.get("completed_tasks", [])),
                "failed_tasks": len(implementation_result.get("failed_tasks", [])),
                "success_rate": implementation_result.get("success_rate", 0)
            },
            "phases": {
                "planning": {"status": "completed"},
                "implementation": implementation_result,
                "qa": qa_result
            }
        }

        # Save report
        report_file = self.results_dir / f"{workflow_id}-report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Generate markdown report
        markdown_report = self._generate_report_markdown(report)
        markdown_file = self.results_dir / f"{workflow_id}-report.md"
        with open(markdown_file, 'w') as f:
            f.write(markdown_report)

        return report

    def _generate_report_markdown(self, report: Dict[str, Any]) -> str:
        """Generate markdown workflow report."""
        return f"""# Workflow Report: {report['workflow_id']}

**Plan ID**: {report['plan_id']}
**Status**: {report['status']}
**Generated**: {report['timestamp']}

## Summary
- **Total Tasks**: {report['summary']['total_tasks']}
- **Completed Tasks**: {report['summary']['completed_tasks']}
- **Failed Tasks**: {report['summary']['failed_tasks']}
- **Success Rate**: {report['summary']['success_rate']:.1f}%

## Phase Results

### Planning
Status: {report['phases']['planning']['status']}

### Implementation
Status: {report['phases']['implementation']['status']}
Success Rate: {report['phases']['implementation'].get('success_rate', 0):.1f}%

### Quality Assurance
{self._format_qa_results(report['phases']['qa'])}

## Recommendations
- Review failed tasks and address issues
- Monitor performance metrics
- Update workflows based on lessons learned
"""

    def _format_qa_results(self, qa_results: Dict[str, Any]) -> str:
        """Format QA results for markdown report."""
        if not qa_results:
            return "No QA results available"

        content = ""
        for review_type, result in qa_results.items():
            content += f"**{review_type.replace('_', ' ').title()}**: {result.get('status', 'unknown')}\n"

        return content


async def main():
    """Main entry point for the orchestrator."""
    orchestrator = WorkflowOrchestrator()

    # Example workflow execution
    requirements = {
        "feature": "user_authentication",
        "scope": ["login", "registration", "password_reset"],
        "technology_stack": ["React", "Node.js", "PostgreSQL"],
        "timeline": "2 weeks",
        "team_size": 3
    }

    result = await orchestrator.execute_workflow(requirements)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())