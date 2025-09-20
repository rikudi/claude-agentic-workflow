# Getting Started with Claude Code Agentic Workflows

This guide will help you set up and use the Claude Code agentic template for coordinated multi-agent software development workflows.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Your First Workflow](#your-first-workflow)
5. [Understanding the Agents](#understanding-the-agents)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before getting started, ensure you have:

### Required Software
- **Claude Code**: Latest version installed and configured
- **Python 3.8+**: For orchestration scripts and hooks
- **Node.js 16+**: For JavaScript/TypeScript projects (optional)
- **Git**: For version control

### Claude Code Setup
1. Install Claude Code following the [official documentation](https://docs.claude.com/en/docs/claude-code/)
2. Verify installation:
   ```bash
   claude-code --version
   ```
3. Configure your workspace and permissions

### System Requirements
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for package downloads

## Installation

### 1. Clone the Template Repository

```bash
# Clone the template
git clone https://github.com/your-org/claude-agentic-workflow.git
cd claude-agentic-workflow

# Or use this as a template for a new repository
# (if you're creating a new project)
```

### 2. Install Dependencies

```bash
# Install Python dependencies for orchestration
pip install -r requirements.txt

# Install Node.js dependencies (if working on JS/TS projects)
npm install

# Make scripts executable
chmod +x scripts/**/*.py
chmod +x hooks/**/*.py
```

### 3. Validate Repository Structure

```bash
# Run the structure validator
python scripts/validation/structure-validator.py

# Should output: ✅ Validation Results: PASS
```

## Configuration

### 1. Configure Claude Code Subagents

Each subagent needs to be configured for your specific environment:

```bash
# Review subagent configurations
ls subagents/

# Output should show:
# planner/
# plan-reviewer/
# coder-frontend/
# coder-backend/
# coder-infra/
# ui-reviewer/
# code-reviewer/
```

### 2. Customize Agent Permissions

Edit the permissions in each `subagents/*/config.yaml` file:

```yaml
# Example: subagents/coder-frontend/config.yaml
claude_code:
  permissions:
    read_access:
      - "src/**/*.tsx"
      - "src/**/*.ts"
      - "src/**/*.css"
    write_access:
      - "src/components/**/*"
      - "src/pages/**/*"
      - "tests/**/*"
    tool_restrictions:
      - "no_bash_execution"
      - "no_server_modifications"
```

### 3. Set Up Project-Specific Configuration

Create a `claude-code-config.yaml` file in your project root:

```yaml
# claude-code-config.yaml
project:
  name: "my-project"
  type: "web-application"
  technology_stack:
    frontend: "React + TypeScript"
    backend: "Node.js + Express"
    database: "PostgreSQL"
    deployment: "AWS"

workflow:
  max_concurrent_agents: 3
  task_timeout_minutes: 60
  retry_attempts: 2

quality_standards:
  test_coverage_threshold: 80
  security_severity_threshold: "medium"
  performance_requirements:
    api_response_time: 200
    page_load_time: 3000

agents:
  planner:
    planning_style: "detailed"
    architecture_focus: "scalability"

  coder-frontend:
    framework_preference: "React"
    styling_approach: "Tailwind CSS"
    testing_framework: "Jest + React Testing Library"

  coder-backend:
    language: "TypeScript"
    framework: "Express"
    database_orm: "Prisma"
```

## Your First Workflow

Let's create a simple "Hello World" feature to test the workflow:

### 1. Define Requirements

Create a requirements file:

```json
{
  "feature": "hello_world_api",
  "description": "Simple Hello World API endpoint with frontend display",
  "scope": [
    "api_endpoint",
    "frontend_component",
    "basic_styling"
  ],
  "technology_stack": {
    "frontend": "React",
    "backend": "Node.js"
  },
  "timeline": "2 hours",
  "acceptance_criteria": [
    "API returns 'Hello, World!' message",
    "Frontend displays the message",
    "Basic error handling implemented",
    "Tests included"
  ]
}
```

### 2. Execute the Workflow

```bash
# Start the workflow orchestrator
python scripts/orchestration/workflow-orchestrator.py \
  --requirements requirements/hello-world.json \
  --config claude-code-config.yaml

# Or use the interactive mode
python scripts/orchestration/workflow-orchestrator.py --interactive
```

### 3. Monitor Progress

The orchestrator will:

1. **Planning Phase**: Planner agent creates implementation plan
2. **Review Phase**: Plan reviewer validates and approves the plan
3. **Implementation Phase**: Coder agents implement the features
4. **QA Phase**: UI and Code reviewers validate the implementation

Track progress in real-time:

```bash
# Check workflow status
python scripts/orchestration/workflow-orchestrator.py --status

# View detailed logs
tail -f logs/orchestrator.log
```

### 4. Review Results

After completion, check the generated artifacts:

```bash
# View the implementation plan
cat docs/plans/PLAN-*/plan.md

# Check implementation reports
ls reports/implementation/

# Review code quality reports
ls reports/code/

# See UI review results
ls reports/ui/
```

## Understanding the Agents

### Planning Agents

#### Planner Agent
- **Purpose**: Breaks down requirements into implementable tasks
- **Input**: High-level requirements and constraints
- **Output**: Detailed implementation plan with phases and tasks
- **Key Features**:
  - Architecture design
  - Task dependency mapping
  - Technology recommendations
  - Risk assessment

#### Plan Reviewer Agent
- **Purpose**: Validates and optimizes implementation plans
- **Input**: Plan from planner agent
- **Output**: Approved plan with recommendations
- **Key Features**:
  - Feasibility analysis
  - Resource optimization
  - Quality gate validation

### Implementation Agents

#### Frontend Coder Agent
- **Purpose**: Implements UI components and client-side logic
- **Specializations**:
  - React/Vue/Angular components
  - CSS/SCSS styling
  - State management
  - Frontend testing
- **Tools**: Read, Write, Edit, MultiEdit, Bash

#### Backend Coder Agent
- **Purpose**: Implements APIs, databases, and server-side logic
- **Specializations**:
  - RESTful/GraphQL APIs
  - Database design
  - Authentication systems
  - Performance optimization
- **Tools**: Read, Write, Edit, MultiEdit, Bash

#### Infrastructure Coder Agent
- **Purpose**: Handles deployment, DevOps, and system administration
- **Specializations**:
  - Docker/Kubernetes
  - CI/CD pipelines
  - Cloud infrastructure
  - Monitoring setup
- **Tools**: Read, Write, Edit, Bash

### Quality Assurance Agents

#### UI Reviewer Agent
- **Purpose**: Validates user interface quality and accessibility
- **Key Checks**:
  - Visual regression testing
  - Accessibility compliance
  - Cross-browser compatibility
  - Performance metrics
- **Tools**: Read, Bash (for test execution)

#### Code Reviewer Agent
- **Purpose**: Ensures code quality, security, and maintainability
- **Key Checks**:
  - Static code analysis
  - Security vulnerability scanning
  - Test coverage validation
  - Performance optimization
- **Tools**: Read, Bash (for analysis tools)

## Customization

### Adding New Agents

1. **Create Agent Directory**:
   ```bash
   mkdir subagents/my-custom-agent
   ```

2. **Create Configuration**:
   ```yaml
   # subagents/my-custom-agent/config.yaml
   name: "my-custom-agent"
   description: "Custom agent for specific tasks"
   version: "1.0.0"

   claude_code:
     tools: ["Read", "Write", "Edit"]
     permissions:
       read_access: ["**/*"]
       write_access: ["custom/**/*"]

   capabilities:
     - "custom functionality"
     - "specialized processing"
   ```

3. **Create Prompt**:
   ```markdown
   <!-- subagents/my-custom-agent/prompt.md -->
   # My Custom Agent System Prompt

   You are a specialized agent for handling custom tasks...
   ```

### Modifying Workflows

Edit the orchestrator to customize workflow behavior:

```python
# scripts/orchestration/workflow-orchestrator.py

class CustomWorkflowOrchestrator(WorkflowOrchestrator):
    async def execute_custom_phase(self, plan):
        """Add custom workflow phase."""
        # Custom implementation
        pass
```

### Adding Hooks

Create custom hooks for workflow events:

```python
#!/usr/bin/env python3
# hooks/custom/my-hook.py

import json
import sys

def main():
    # Read hook input
    hook_data = json.loads(sys.argv[1])

    # Custom validation/processing
    result = process_hook_data(hook_data)

    # Return result
    print(json.dumps({
        "allow": result["valid"],
        "message": result["message"]
    }))

if __name__ == "__main__":
    main()
```

## Troubleshooting

### Common Issues

#### Agent Not Found
```
Error: Agent 'coder-frontend' not found
```
**Solution**: Verify agent configuration exists and is valid:
```bash
python scripts/validation/structure-validator.py
```

#### Permission Denied
```
Error: Permission denied for file access
```
**Solution**: Check agent permissions in config.yaml:
```yaml
claude_code:
  permissions:
    read_access: ["src/**/*"]  # Add required paths
    write_access: ["src/components/**/*"]
```

#### Tool Execution Failed
```
Error: Tool 'Bash' execution failed
```
**Solution**:
1. Check tool restrictions in agent config
2. Verify Claude Code tool availability
3. Check file permissions

#### Workflow Timeout
```
Error: Task execution timed out
```
**Solution**:
1. Increase timeout in configuration:
   ```yaml
   workflow:
     task_timeout_minutes: 120  # Increase from 60
   ```
2. Break down complex tasks into smaller ones

### Debugging

#### Enable Debug Logging
```bash
export CLAUDE_CODE_LOG_LEVEL=DEBUG
python scripts/orchestration/workflow-orchestrator.py --debug
```

#### Check Agent Status
```bash
# Validate all agent configurations
for agent in subagents/*/; do
  echo "Validating $(basename $agent)..."
  python scripts/validation/structure-validator.py --agent $(basename $agent)
done
```

#### Inspect Generated Plans
```bash
# View detailed plan structure
cat docs/plans/*/plan.json | jq '.phases[].tasks[] | {id: .task_id, agent: .assigned_agent}'
```

## Next Steps

Now that you have the basics working:

1. **Explore Examples**: Review detailed examples in `docs/examples/`
2. **Customize Agents**: Modify agent prompts and configurations for your needs
3. **Add Integrations**: Connect with your existing tools and workflows
4. **Scale Usage**: Use for larger, more complex projects
5. **Contribute**: Submit improvements and new agents back to the template

For more advanced topics, see:
- [Agent Customization Guide](agent-customization.md)
- [Workflow Patterns](workflow-patterns.md)
- [Integration Examples](integrations/)
- [Best Practices](knowledge-base/claude-code-best-practices.md)

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review the [knowledge base](knowledge-base/)
3. Search existing [GitHub issues](https://github.com/your-org/claude-agentic-workflow/issues)
4. Create a new issue with detailed error information

Happy coding with Claude Code agentic workflows! 🚀