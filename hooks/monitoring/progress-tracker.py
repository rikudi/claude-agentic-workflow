#!/usr/bin/env python3
"""
Progress Tracking Hook for Claude Code
Monitors and reports on workflow progress and agent activities
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class ProgressTracker:
    def __init__(self):
        self.reports_dir = Path(__file__).parent.parent.parent / "reports"
        self.progress_file = self.reports_dir / "workflow_progress.json"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_progress_data(self) -> Dict[str, Any]:
        """Load existing progress data"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            "workflows": {},
            "agents": {},
            "tasks": {},
            "metrics": {
                "total_tasks": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "blocked_tasks": 0,
                "total_time_spent": 0
            }
        }

    def save_progress_data(self, data: Dict[str, Any]) -> None:
        """Save progress data to file"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(data, f, indent=2)

    def track_task_start(self, task_id: str, agent_name: str, task_data: Dict[str, Any]) -> None:
        """Track when a task starts"""
        progress = self.load_progress_data()

        task_record = {
            "task_id": task_id,
            "agent": agent_name,
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "estimated_effort": task_data.get("estimated_effort", "unknown"),
            "title": task_data.get("title", ""),
            "phase": task_data.get("phase", ""),
            "dependencies": task_data.get("dependencies", []),
            "progress_updates": []
        }

        progress["tasks"][task_id] = task_record

        # Update agent statistics
        if agent_name not in progress["agents"]:
            progress["agents"][agent_name] = {
                "active_tasks": 0,
                "completed_tasks": 0,
                "total_time_spent": 0,
                "average_task_time": 0
            }

        progress["agents"][agent_name]["active_tasks"] += 1
        progress["metrics"]["in_progress_tasks"] += 1

        self.save_progress_data(progress)

    def track_task_completion(self, task_id: str, completion_data: Dict[str, Any]) -> None:
        """Track when a task completes"""
        progress = self.load_progress_data()

        if task_id in progress["tasks"]:
            task = progress["tasks"][task_id]
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            task["actual_effort"] = completion_data.get("actual_effort", "unknown")
            task["deliverables"] = completion_data.get("deliverables", [])
            task["notes"] = completion_data.get("notes", "")

            # Calculate time spent
            if "started_at" in task:
                start_time = datetime.fromisoformat(task["started_at"])
                end_time = datetime.fromisoformat(task["completed_at"])
                time_spent = (end_time - start_time).total_seconds() / 3600  # hours

                task["time_spent_hours"] = time_spent

                # Update agent statistics
                agent_name = task["agent"]
                if agent_name in progress["agents"]:
                    progress["agents"][agent_name]["active_tasks"] -= 1
                    progress["agents"][agent_name]["completed_tasks"] += 1
                    progress["agents"][agent_name]["total_time_spent"] += time_spent

                    # Calculate average task time
                    completed = progress["agents"][agent_name]["completed_tasks"]
                    total_time = progress["agents"][agent_name]["total_time_spent"]
                    progress["agents"][agent_name]["average_task_time"] = total_time / completed if completed > 0 else 0

            progress["metrics"]["completed_tasks"] += 1
            progress["metrics"]["in_progress_tasks"] -= 1

        self.save_progress_data(progress)

    def track_task_blocked(self, task_id: str, blocker_info: Dict[str, Any]) -> None:
        """Track when a task becomes blocked"""
        progress = self.load_progress_data()

        if task_id in progress["tasks"]:
            task = progress["tasks"][task_id]
            task["status"] = "blocked"
            task["blocked_at"] = datetime.now().isoformat()
            task["blocker"] = blocker_info

            progress["metrics"]["blocked_tasks"] += 1
            progress["metrics"]["in_progress_tasks"] -= 1

        self.save_progress_data(progress)

    def add_progress_update(self, task_id: str, update: str, percentage: Optional[int] = None) -> None:
        """Add a progress update to a task"""
        progress = self.load_progress_data()

        if task_id in progress["tasks"]:
            update_record = {
                "timestamp": datetime.now().isoformat(),
                "message": update,
                "percentage": percentage
            }

            progress["tasks"][task_id]["progress_updates"].append(update_record)

            if percentage is not None:
                progress["tasks"][task_id]["completion_percentage"] = percentage

        self.save_progress_data(progress)

    def generate_status_report(self) -> Dict[str, Any]:
        """Generate a comprehensive status report"""
        progress = self.load_progress_data()

        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": progress["metrics"],
            "active_tasks": [],
            "recent_completions": [],
            "blocked_tasks": [],
            "agent_performance": {},
            "timeline_analysis": {}
        }

        # Gather active tasks
        for task_id, task in progress["tasks"].items():
            if task["status"] == "in_progress":
                report["active_tasks"].append({
                    "task_id": task_id,
                    "title": task["title"],
                    "agent": task["agent"],
                    "started_at": task["started_at"],
                    "estimated_effort": task["estimated_effort"],
                    "completion_percentage": task.get("completion_percentage", 0)
                })

            elif task["status"] == "completed":
                completed_at = datetime.fromisoformat(task["completed_at"])
                if completed_at > datetime.now() - timedelta(days=7):  # Last 7 days
                    report["recent_completions"].append({
                        "task_id": task_id,
                        "title": task["title"],
                        "agent": task["agent"],
                        "completed_at": task["completed_at"],
                        "time_spent_hours": task.get("time_spent_hours", 0)
                    })

            elif task["status"] == "blocked":
                report["blocked_tasks"].append({
                    "task_id": task_id,
                    "title": task["title"],
                    "agent": task["agent"],
                    "blocked_at": task["blocked_at"],
                    "blocker": task.get("blocker", {})
                })

        # Agent performance summary
        report["agent_performance"] = progress["agents"]

        # Timeline analysis
        total_tasks = progress["metrics"]["total_tasks"]
        completed_tasks = progress["metrics"]["completed_tasks"]

        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            report["timeline_analysis"]["completion_rate"] = completion_rate

            # Estimate completion time based on current velocity
            if completed_tasks > 0:
                avg_time_per_task = progress["metrics"]["total_time_spent"] / completed_tasks
                remaining_tasks = total_tasks - completed_tasks
                estimated_remaining_time = remaining_tasks * avg_time_per_task

                report["timeline_analysis"]["estimated_completion_hours"] = estimated_remaining_time

        return report

    def check_for_issues(self) -> List[Dict[str, Any]]:
        """Check for potential issues in the workflow"""
        progress = self.load_progress_data()
        issues = []

        # Check for long-running tasks
        for task_id, task in progress["tasks"].items():
            if task["status"] == "in_progress" and "started_at" in task:
                start_time = datetime.fromisoformat(task["started_at"])
                hours_running = (datetime.now() - start_time).total_seconds() / 3600

                if hours_running > 24:  # Task running for more than 24 hours
                    issues.append({
                        "type": "long_running_task",
                        "severity": "medium",
                        "task_id": task_id,
                        "message": f"Task has been running for {hours_running:.1f} hours",
                        "recommendation": "Check if task needs assistance or should be broken down"
                    })

        # Check for blocked tasks
        blocked_count = progress["metrics"]["blocked_tasks"]
        if blocked_count > 0:
            issues.append({
                "type": "blocked_tasks",
                "severity": "high",
                "count": blocked_count,
                "message": f"{blocked_count} tasks are currently blocked",
                "recommendation": "Review and resolve blockers to maintain workflow velocity"
            })

        # Check agent workload distribution
        agent_workloads = {name: data["active_tasks"] for name, data in progress["agents"].items()}
        if agent_workloads:
            max_workload = max(agent_workloads.values())
            min_workload = min(agent_workloads.values())

            if max_workload > min_workload + 2:  # Significant workload imbalance
                issues.append({
                    "type": "workload_imbalance",
                    "severity": "low",
                    "message": "Uneven workload distribution among agents",
                    "recommendation": "Consider rebalancing task assignments"
                })

        return issues

def main():
    """Main hook execution"""
    if len(sys.argv) < 3:
        print(json.dumps({
            "allow": True,
            "message": "Progress tracker hook requires: <action> <data>"
        }))
        sys.exit(0)

    try:
        action = sys.argv[1]
        data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

        tracker = ProgressTracker()

        if action == "task_start":
            task_id = data.get("task_id")
            agent_name = data.get("agent")
            task_data = data.get("task_data", {})
            tracker.track_task_start(task_id, agent_name, task_data)

        elif action == "task_complete":
            task_id = data.get("task_id")
            completion_data = data.get("completion_data", {})
            tracker.track_task_completion(task_id, completion_data)

        elif action == "task_blocked":
            task_id = data.get("task_id")
            blocker_info = data.get("blocker_info", {})
            tracker.track_task_blocked(task_id, blocker_info)

        elif action == "progress_update":
            task_id = data.get("task_id")
            update = data.get("update", "")
            percentage = data.get("percentage")
            tracker.add_progress_update(task_id, update, percentage)

        elif action == "status_report":
            report = tracker.generate_status_report()
            print(json.dumps({
                "allow": True,
                "message": "Status report generated",
                "report": report
            }))
            sys.exit(0)

        elif action == "check_issues":
            issues = tracker.check_for_issues()
            print(json.dumps({
                "allow": True,
                "message": f"Found {len(issues)} potential issues",
                "issues": issues
            }))
            sys.exit(0)

        print(json.dumps({
            "allow": True,
            "message": f"Progress tracking action '{action}' completed successfully"
        }))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({
            "allow": True,  # Don't block on tracking errors
            "message": f"Error in progress tracking: {str(e)}"
        }))
        sys.exit(0)

if __name__ == "__main__":
    main()