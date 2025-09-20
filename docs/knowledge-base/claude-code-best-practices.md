# Claude Code Best Practices for Multi-Agent Workflows

This document outlines best practices for implementing multi-agent workflows using Claude Code's capabilities and tools.

## Table of Contents
1. [Subagent Design Principles](#subagent-design-principles)
2. [Tool Usage Guidelines](#tool-usage-guidelines)
3. [Workflow Coordination](#workflow-coordination)
4. [Security and Permissions](#security-and-permissions)
5. [Error Handling and Recovery](#error-handling-and-recovery)
6. [Performance Optimization](#performance-optimization)
7. [Documentation Standards](#documentation-standards)
8. [Testing and Validation](#testing-and-validation)

## Subagent Design Principles

### 1. Single Responsibility Principle
Each subagent should have a clearly defined, focused responsibility:

```yaml
# Good: Focused responsibility
name: "frontend-coder"
description: "Frontend development specialist for UI/UX implementation"

# Bad: Too broad
name: "general-coder"
description: "Handles all coding tasks including frontend, backend, and infrastructure"
```

### 2. Clear Input/Output Contracts
Define explicit schemas for subagent communication:

```yaml
input_schema:
  type: "object"
  properties:
    task:
      type: "object"
      required: ["task_id", "title", "description"]
    context:
      type: "object"
      required: ["project_type", "technology_stack"]

output_schema:
  type: "object"
  properties:
    implementation:
      type: "object"
      required: ["files_created", "tests_added"]
    quality_metrics:
      type: "object"
      required: ["test_coverage", "performance_score"]
```

### 3. Stateless Design
Subagents should be stateless and rely on external state management:

```yaml
# Store state in external systems
outputs:
  - path: "reports/implementation/{task_id}-status.json"
    format: "json"
  - path: "docs/progress/{task_id}-progress.md"
    format: "markdown"
```

## Tool Usage Guidelines

### 1. Tool Selection Strategy
Choose the most appropriate Claude Code tools for each task:

#### For Code Analysis
```markdown
- **Read**: Understand existing code and patterns
- **Grep**: Search for specific implementations or patterns
- **Glob**: Find related files efficiently
```

#### For Implementation
```markdown
- **Write**: Create new files (use sparingly)
- **Edit**: Modify existing files with precise changes
- **MultiEdit**: Make multiple related changes atomically
```

#### For Validation
```markdown
- **Bash**: Run tests, builds, and validation scripts
- **TodoWrite**: Track progress and maintain task lists
```

### 2. Tool Usage Patterns

#### Efficient File Discovery
```python
# Use Glob for pattern-based file discovery
files = glob("src/**/*.ts")  # Find all TypeScript files
components = glob("src/components/**/*.tsx")  # Find React components
tests = glob("tests/**/*.test.*")  # Find test files
```

#### Safe File Modifications
```python
# Use Read before Edit to understand context
content = read("src/components/Button.tsx")
# Analyze existing patterns
# Then make targeted changes
edit(
    file_path="src/components/Button.tsx",
    old_string="const Button = (props) => {",
    new_string="const Button: React.FC<ButtonProps> = (props) => {"
)
```

### 3. Batch Operations
Minimize tool calls by batching operations:

```python
# Good: Batch related reads
files_to_analyze = [
    "src/api/users.ts",
    "src/api/auth.ts",
    "src/api/posts.ts"
]

# Process all files in one go
for file in files_to_analyze:
    content = read(file)
    analyze_api_patterns(content)

# Make all changes in a single MultiEdit
multi_edit(
    file_path="src/api/users.ts",
    edits=[
        {"old_string": "old_pattern_1", "new_string": "new_pattern_1"},
        {"old_string": "old_pattern_2", "new_string": "new_pattern_2"}
    ]
)
```

## Workflow Coordination

### 1. Task Handoff Protocol
Establish clear handoff procedures between agents:

```markdown
## Handoff Checklist
- [ ] Task completion criteria verified
- [ ] Artifacts generated and stored
- [ ] Context documented for next agent
- [ ] Dependencies satisfied
- [ ] Quality gates passed
```

### 2. Progress Tracking
Use TodoWrite consistently for progress visibility:

```python
# Update progress at key milestones
todo_write([
    {
        "content": "Implement user authentication API",
        "status": "in_progress",
        "activeForm": "Implementing user authentication API"
    }
])

# Mark completion with details
todo_write([
    {
        "content": "Implement user authentication API",
        "status": "completed",
        "activeForm": "Implementing user authentication API"
    }
])
```

### 3. Inter-Agent Communication
Use structured artifacts for agent coordination:

```json
{
  "handoff_id": "handoff-20241220-143022",
  "from_agent": "planner",
  "to_agent": "coder-backend",
  "task": {
    "task_id": "AUTH-001",
    "title": "Implement JWT authentication",
    "requirements": ["..."],
    "success_criteria": ["..."]
  },
  "context": {
    "related_files": ["src/auth/*.ts"],
    "dependencies": ["AUTH-002"],
    "estimated_effort": "4 hours"
  }
}
```

## Security and Permissions

### 1. Principle of Least Privilege
Grant minimal necessary permissions to each subagent:

```yaml
claude_code:
  permissions:
    read_access: ["src/**/*.tsx", "src/**/*.ts"]  # Specific patterns
    write_access: ["src/components/**/*"]         # Limited scope
    tool_restrictions:
      - "no_bash_execution"                       # Prevent system access
      - "no_production_modifications"             # Protect critical files
```

### 2. Sensitive Data Handling
Protect sensitive information in configurations:

```yaml
# Never include secrets in configs
# Use environment variables or secure vaults
database_config:
  host: "${DATABASE_HOST}"
  port: "${DATABASE_PORT}"
  # Don't include passwords or keys directly
```

### 3. Audit Trail
Maintain comprehensive logging for security and debugging:

```python
# Log all significant actions
log_entry = {
    "timestamp": datetime.now().isoformat(),
    "agent": "coder-backend",
    "action": "file_modification",
    "file_path": "src/api/auth.py",
    "change_summary": "Added JWT token validation",
    "user_context": "task_AUTH-001"
}
```

## Error Handling and Recovery

### 1. Graceful Error Handling
Implement robust error handling in all agents:

```python
def handle_task_execution(task):
    try:
        result = execute_task(task)
        return {"status": "success", "result": result}
    except ValidationError as e:
        return {
            "status": "validation_error",
            "message": str(e),
            "recovery_suggestion": "Review input parameters"
        }
    except ToolError as e:
        return {
            "status": "tool_error",
            "message": str(e),
            "recovery_suggestion": "Check tool permissions and availability"
        }
    except Exception as e:
        return {
            "status": "unexpected_error",
            "message": str(e),
            "recovery_suggestion": "Contact system administrator"
        }
```

### 2. Recovery Strategies
Define clear recovery procedures for common failures:

```markdown
## Common Failure Scenarios

### File Access Denied
1. Check subagent permissions configuration
2. Verify file paths are within allowed scope
3. Escalate to administrator if needed

### Test Failures
1. Analyze test output and identify root cause
2. Fix implementation issues
3. Re-run tests to verify resolution
4. Update test cases if requirements changed

### Deployment Failures
1. Check infrastructure configuration
2. Verify environment variables and secrets
3. Roll back to previous stable version if needed
4. Fix issues and retry deployment
```

### 3. State Recovery
Implement checkpointing for long-running workflows:

```python
def save_checkpoint(workflow_id, current_state):
    checkpoint = {
        "workflow_id": workflow_id,
        "timestamp": datetime.now().isoformat(),
        "current_phase": current_state["phase"],
        "completed_tasks": current_state["completed"],
        "pending_tasks": current_state["pending"],
        "context": current_state["context"]
    }

    with open(f"reports/checkpoints/{workflow_id}.json", "w") as f:
        json.dump(checkpoint, f, indent=2)
```

## Performance Optimization

### 1. Efficient Tool Usage
Optimize tool calls for better performance:

```python
# Good: Batch file reads
files_content = {}
for file_path in file_list:
    files_content[file_path] = read(file_path)

# Bad: Repeated individual reads in a loop
for item in data:
    content = read(f"src/{item}.ts")  # Inefficient
```

### 2. Parallel Execution
Leverage Claude Code's parallel capabilities:

```python
# Execute independent tasks in parallel
parallel_tasks = [
    {"agent": "coder-frontend", "task": frontend_task},
    {"agent": "coder-backend", "task": backend_task},
    {"agent": "coder-infra", "task": infra_task}
]

# All tasks can run simultaneously
execute_parallel(parallel_tasks)
```

### 3. Resource Management
Monitor and optimize resource usage:

```python
# Monitor task execution time
import time

start_time = time.time()
result = execute_complex_task()
execution_time = time.time() - start_time

# Log performance metrics
performance_log = {
    "task_id": task.id,
    "execution_time": execution_time,
    "memory_usage": get_memory_usage(),
    "files_processed": len(processed_files)
}
```

## Documentation Standards

### 1. Configuration Documentation
Document all configuration options:

```yaml
# subagents/coder-frontend/config.yaml

# Agent identification
name: "coder-frontend"                    # Required: Unique agent identifier
description: "Frontend specialist..."      # Required: Clear description of capabilities
version: "1.0.0"                          # Required: Semantic version for tracking

# Claude Code integration
claude_code:
  tools:                                   # Required: List of allowed tools
    - "Read"                              # File reading capabilities
    - "Write"                             # File creation (use sparingly)
    - "Edit"                              # Targeted file modifications
  permissions:
    read_access: ["src/**/*.tsx"]          # Glob patterns for readable files
    write_access: ["src/components/**/*"] # Glob patterns for writable files
    tool_restrictions:                     # Security constraints
      - "no_bash_execution"               # Prevent shell access
```

### 2. Prompt Documentation
Maintain clear prompt documentation:

```markdown
# Agent Prompt Structure

## System Context
- Clear role definition and responsibilities
- Specific domain expertise areas
- Interaction guidelines

## Tool Usage Instructions
- When to use each tool
- Best practices for tool combinations
- Error handling approaches

## Quality Standards
- Code quality requirements
- Testing expectations
- Documentation standards

## Integration Guidelines
- Handoff procedures
- Artifact generation requirements
- Progress reporting expectations
```

### 3. Workflow Documentation
Document complete workflow processes:

```markdown
# Workflow: Feature Implementation

## Overview
End-to-end process for implementing new features using multi-agent coordination.

## Phases
1. **Planning** (planner agent)
   - Requirements analysis
   - Task breakdown
   - Architecture design

2. **Review** (plan-reviewer agent)
   - Plan validation
   - Risk assessment
   - Approval process

3. **Implementation** (coder agents)
   - Parallel development
   - Progress tracking
   - Quality assurance

4. **Testing** (QA agents)
   - Automated testing
   - Manual validation
   - Performance verification

## Success Criteria
- All tests pass
- Code quality gates met
- Documentation complete
- Deployment successful
```

## Testing and Validation

### 1. Agent Testing Strategy
Test individual agents thoroughly:

```python
# Unit tests for agent functionality
def test_frontend_coder_component_creation():
    agent = FrontendCoderAgent()
    task = {
        "task_id": "COMP-001",
        "component_name": "Button",
        "props": ["children", "onClick", "variant"],
        "styling": "tailwind"
    }

    result = agent.create_component(task)

    assert result["status"] == "success"
    assert "Button.tsx" in result["files_created"]
    assert "Button.test.tsx" in result["tests_created"]
```

### 2. Integration Testing
Test agent interactions and handoffs:

```python
def test_planner_to_coder_handoff():
    # Create plan with planner agent
    plan = planner_agent.create_plan(requirements)

    # Validate plan with reviewer
    review = plan_reviewer.review_plan(plan)
    assert review["status"] == "approved"

    # Execute plan with coder agents
    implementation = coder_agent.implement_tasks(plan["tasks"])

    # Verify handoff was successful
    assert implementation["tasks_completed"] == len(plan["tasks"])
    assert all(task["status"] == "completed" for task in implementation["task_results"])
```

### 3. Workflow Validation
Validate complete multi-agent workflows:

```python
def test_complete_feature_workflow():
    # Define feature requirements
    requirements = {
        "feature": "user_authentication",
        "scope": ["login", "registration", "password_reset"],
        "technology": "react_nodejs"
    }

    # Execute complete workflow
    workflow = MultiAgentWorkflow()
    result = workflow.execute(requirements)

    # Validate final outcome
    assert result["status"] == "completed"
    assert result["quality_score"] >= 80
    assert result["test_coverage"] >= 85
    assert len(result["critical_issues"]) == 0
```

### 4. Performance Testing
Test workflow performance and scalability:

```python
def test_workflow_performance():
    start_time = time.time()

    # Execute workflow with performance monitoring
    result = execute_monitored_workflow(complex_requirements)

    execution_time = time.time() - start_time

    # Validate performance criteria
    assert execution_time < 3600  # Complete within 1 hour
    assert result["agent_coordination_time"] < 300  # Handoffs under 5 minutes
    assert result["resource_usage"]["memory"] < "2GB"
```

## Monitoring and Observability

### 1. Metrics Collection
Track key performance indicators:

```python
metrics = {
    "workflow_execution_time": execution_time,
    "agent_utilization": {
        "planner": planner_active_time,
        "coder-frontend": frontend_active_time,
        "coder-backend": backend_active_time
    },
    "quality_metrics": {
        "code_quality_score": 85,
        "test_coverage": 92,
        "security_score": 88
    },
    "error_rates": {
        "tool_errors": 0.02,
        "validation_errors": 0.05,
        "system_errors": 0.01
    }
}
```

### 2. Alerting Strategy
Set up proactive monitoring:

```python
def check_workflow_health():
    if error_rate > 0.1:
        send_alert("High error rate detected in multi-agent workflow")

    if average_execution_time > threshold:
        send_alert("Workflow performance degradation detected")

    if agent_failure_count > 3:
        send_alert("Multiple agent failures, manual intervention required")
```

### 3. Continuous Improvement
Use metrics for optimization:

```python
def analyze_workflow_performance():
    # Identify bottlenecks
    bottlenecks = find_performance_bottlenecks(execution_logs)

    # Suggest optimizations
    optimizations = suggest_improvements(bottlenecks, historical_data)

    # Generate improvement report
    report = {
        "identified_issues": bottlenecks,
        "optimization_suggestions": optimizations,
        "expected_improvements": calculate_expected_gains(optimizations)
    }

    return report
```

---

## Conclusion

These best practices provide a foundation for building robust, efficient, and maintainable multi-agent workflows with Claude Code. Remember to:

1. **Start Simple**: Begin with basic workflows and gradually add complexity
2. **Monitor Continuously**: Track performance and quality metrics
3. **Iterate Regularly**: Refine agents and workflows based on experience
4. **Document Everything**: Maintain comprehensive documentation for team knowledge
5. **Test Thoroughly**: Validate all components and interactions
6. **Secure by Design**: Implement security from the ground up

By following these guidelines, teams can leverage Claude Code's capabilities to build sophisticated multi-agent systems that deliver high-quality software efficiently and reliably.