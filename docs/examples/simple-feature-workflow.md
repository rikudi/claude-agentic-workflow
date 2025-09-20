# Example: Simple Feature Workflow

This example demonstrates how to implement a user authentication feature using the Claude Code agentic template workflow.

## Scenario
Build a complete user authentication system with:
- User registration and login
- JWT token-based authentication
- Password reset functionality
- Frontend React components
- Backend API endpoints

## Step-by-Step Workflow

### 1. Initial Requirements

```json
{
  "feature": "user_authentication",
  "description": "Complete user authentication system with registration, login, and password reset",
  "scope": [
    "user_registration",
    "user_login",
    "password_reset",
    "jwt_authentication",
    "frontend_components"
  ],
  "technology_stack": {
    "frontend": "React + TypeScript",
    "backend": "Node.js + Express",
    "database": "PostgreSQL",
    "authentication": "JWT"
  },
  "timeline": "1 week",
  "team_size": 2,
  "constraints": {
    "budget": "low",
    "security_level": "high",
    "performance_requirements": "standard"
  }
}
```

### 2. Planning Phase (Planner Agent)

**Input to Planner Agent:**
```yaml
agent: planner
input:
  requirements: [requirements from above]
  project_context:
    existing_codebase: "React + Node.js starter template"
    team_skills: ["React", "Node.js", "PostgreSQL"]
    deployment_target: "AWS"
```

**Expected Planner Output:**
```json
{
  "plan_id": "PLAN-AUTH-20241220-001",
  "title": "User Authentication Implementation Plan",
  "estimated_duration": "5 days",
  "phases": [
    {
      "phase_id": "PHASE-1",
      "name": "Backend Foundation",
      "description": "Set up authentication infrastructure and APIs",
      "estimated_duration": "2 days",
      "tasks": [
        {
          "task_id": "AUTH-001",
          "title": "Database Schema Design",
          "description": "Create users table with proper indexes and constraints",
          "assigned_agent": "coder-backend",
          "estimated_effort": "2 hours",
          "dependencies": [],
          "deliverables": ["migration files", "user model"]
        },
        {
          "task_id": "AUTH-002",
          "title": "JWT Authentication Middleware",
          "description": "Implement JWT token generation and validation",
          "assigned_agent": "coder-backend",
          "estimated_effort": "3 hours",
          "dependencies": ["AUTH-001"],
          "deliverables": ["auth middleware", "token utilities"]
        },
        {
          "task_id": "AUTH-003",
          "title": "User Registration API",
          "description": "Create user registration endpoint with validation",
          "assigned_agent": "coder-backend",
          "estimated_effort": "4 hours",
          "dependencies": ["AUTH-002"],
          "deliverables": ["registration endpoint", "input validation", "tests"]
        },
        {
          "task_id": "AUTH-004",
          "title": "User Login API",
          "description": "Create login endpoint with password verification",
          "assigned_agent": "coder-backend",
          "estimated_effort": "3 hours",
          "dependencies": ["AUTH-002"],
          "deliverables": ["login endpoint", "password verification", "tests"]
        }
      ]
    },
    {
      "phase_id": "PHASE-2",
      "name": "Frontend Implementation",
      "description": "Build user interface components and forms",
      "estimated_duration": "2 days",
      "dependencies": ["PHASE-1"],
      "tasks": [
        {
          "task_id": "AUTH-005",
          "title": "Registration Form Component",
          "description": "Create React registration form with validation",
          "assigned_agent": "coder-frontend",
          "estimated_effort": "4 hours",
          "dependencies": ["AUTH-003"],
          "deliverables": ["RegisterForm component", "form validation", "tests"]
        },
        {
          "task_id": "AUTH-006",
          "title": "Login Form Component",
          "description": "Create React login form with error handling",
          "assigned_agent": "coder-frontend",
          "estimated_effort": "3 hours",
          "dependencies": ["AUTH-004"],
          "deliverables": ["LoginForm component", "error handling", "tests"]
        },
        {
          "task_id": "AUTH-007",
          "title": "Authentication Context",
          "description": "Implement React context for auth state management",
          "assigned_agent": "coder-frontend",
          "estimated_effort": "3 hours",
          "dependencies": ["AUTH-005", "AUTH-006"],
          "deliverables": ["AuthContext", "auth hooks", "protected routes"]
        }
      ]
    },
    {
      "phase_id": "PHASE-3",
      "name": "Testing & Integration",
      "description": "Quality assurance and deployment preparation",
      "estimated_duration": "1 day",
      "dependencies": ["PHASE-2"],
      "tasks": [
        {
          "task_id": "AUTH-008",
          "title": "Integration Testing",
          "description": "End-to-end testing of authentication flow",
          "assigned_agent": "ui-reviewer",
          "estimated_effort": "4 hours",
          "dependencies": ["AUTH-007"],
          "deliverables": ["E2E tests", "accessibility audit", "performance tests"]
        },
        {
          "task_id": "AUTH-009",
          "title": "Security Review",
          "description": "Code review focusing on security best practices",
          "assigned_agent": "code-reviewer",
          "estimated_effort": "2 hours",
          "dependencies": ["AUTH-007"],
          "deliverables": ["security report", "vulnerability assessment"]
        }
      ]
    }
  ],
  "architecture": {
    "system_overview": "JWT-based stateless authentication with React frontend and Express backend",
    "security_measures": ["password hashing", "JWT tokens", "input validation", "rate limiting"],
    "scalability_considerations": ["stateless design", "database indexing", "caching strategy"]
  },
  "risks": [
    {
      "risk_id": "RISK-001",
      "description": "JWT token security vulnerabilities",
      "impact": "high",
      "probability": "low",
      "mitigation": "Use secure token generation, implement token rotation, add rate limiting"
    }
  ]
}
```

### 3. Plan Review Phase (Plan Reviewer Agent)

**Input to Plan Reviewer:**
```yaml
agent: plan-reviewer
input:
  plan: [output from planner]
  review_criteria:
    timeline_constraints: "5 days maximum"
    security_standards: "enterprise"
    team_capacity: "2 developers"
```

**Expected Review Output:**
```json
{
  "review_id": "REVIEW-AUTH-20241220-001",
  "plan_id": "PLAN-AUTH-20241220-001",
  "status": "approved",
  "overall_score": 88,
  "findings": [
    {
      "category": "task_breakdown",
      "severity": "minor",
      "description": "Consider adding password reset functionality task",
      "recommendation": "Add password reset endpoint and UI components",
      "affected_items": ["PHASE-1", "PHASE-2"]
    },
    {
      "category": "security",
      "severity": "info",
      "description": "Good security practices included in plan",
      "recommendation": "Ensure rate limiting is implemented on auth endpoints"
    }
  ],
  "recommendations": [
    {
      "type": "enhancement",
      "priority": "medium",
      "description": "Add password reset functionality",
      "implementation": "Create additional tasks AUTH-010 and AUTH-011 for backend and frontend"
    },
    {
      "type": "optimization",
      "priority": "low",
      "description": "Consider parallel execution of AUTH-005 and AUTH-006",
      "implementation": "Mark tasks as independent to enable parallel development"
    }
  ]
}
```

### 4. Implementation Phase (Coder Agents)

#### Backend Implementation (AUTH-001: Database Schema)

**Input to Backend Coder:**
```yaml
agent: coder-backend
input:
  task:
    task_id: "AUTH-001"
    title: "Database Schema Design"
    description: "Create users table with proper indexes and constraints"
  context:
    database: "PostgreSQL"
    orm: "Sequelize"
    existing_schema: []
```

**Expected Implementation:**
```sql
-- migrations/001-create-users-table.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_login TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Email verification tokens table
CREATE TABLE email_verification_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_verification_tokens_user_id ON email_verification_tokens(user_id);
CREATE INDEX idx_verification_tokens_token ON email_verification_tokens(token);
```

#### Frontend Implementation (AUTH-005: Registration Form)

**Input to Frontend Coder:**
```yaml
agent: coder-frontend
input:
  task:
    task_id: "AUTH-005"
    title: "Registration Form Component"
    description: "Create React registration form with validation"
  context:
    framework: "React + TypeScript"
    styling: "Tailwind CSS"
    form_library: "React Hook Form"
    validation: "Zod"
```

**Expected Implementation:**
```typescript
// src/components/auth/RegisterForm.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { useAuth } from '../../hooks/useAuth';

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  username: z.string()
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username must be less than 50 characters')
    .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirmPassword: z.string(),
  firstName: z.string().min(1, 'First name is required'),
  lastName: z.string().min(1, 'Last name is required')
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
});

type RegisterFormData = z.infer<typeof registerSchema>;

export const RegisterForm: React.FC = () => {
  const { register: registerUser, isLoading, error } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema)
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await registerUser({
        email: data.email,
        username: data.username,
        password: data.password,
        firstName: data.firstName,
        lastName: data.lastName
      });
    } catch (error) {
      // Error is handled by useAuth hook
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Input
            {...register('firstName')}
            label="First Name"
            error={errors.firstName?.message}
            required
          />
        </div>
        <div>
          <Input
            {...register('lastName')}
            label="Last Name"
            error={errors.lastName?.message}
            required
          />
        </div>
      </div>

      <Input
        {...register('email')}
        type="email"
        label="Email Address"
        error={errors.email?.message}
        required
      />

      <Input
        {...register('username')}
        label="Username"
        error={errors.username?.message}
        required
      />

      <Input
        {...register('password')}
        type="password"
        label="Password"
        error={errors.password?.message}
        required
      />

      <Input
        {...register('confirmPassword')}
        type="password"
        label="Confirm Password"
        error={errors.confirmPassword?.message}
        required
      />

      {error && (
        <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md">
          {error}
        </div>
      )}

      <Button
        type="submit"
        disabled={isSubmitting || isLoading}
        loading={isSubmitting || isLoading}
        className="w-full"
      >
        Create Account
      </Button>
    </form>
  );
};

export default RegisterForm;
```

### 5. Quality Assurance Phase

#### UI Review (AUTH-008: Integration Testing)

**Input to UI Reviewer:**
```yaml
agent: ui-reviewer
input:
  tasks: ["AUTH-005", "AUTH-006", "AUTH-007"]
  application_url: "http://localhost:3000"
  test_scenarios:
    - "user_registration_flow"
    - "user_login_flow"
    - "form_validation"
    - "error_handling"
    - "accessibility_compliance"
```

**Expected UI Review Output:**
```json
{
  "review_id": "UI-REVIEW-AUTH-20241220-001",
  "overall_score": 92,
  "test_results": {
    "accessibility_score": 96,
    "performance_score": 88,
    "cross_browser_compatibility": 94,
    "responsive_design": 98
  },
  "test_scenarios": [
    {
      "scenario": "user_registration_flow",
      "status": "passed",
      "execution_time": "2.3s",
      "issues": []
    },
    {
      "scenario": "form_validation",
      "status": "passed",
      "issues": [
        {
          "severity": "minor",
          "description": "Password strength indicator could be more prominent",
          "recommendation": "Add visual password strength meter"
        }
      ]
    }
  ],
  "accessibility_audit": {
    "wcag_aa_compliance": 98,
    "issues": [
      {
        "severity": "minor",
        "rule": "color-contrast",
        "element": "error messages",
        "recommendation": "Increase contrast ratio to 4.5:1"
      }
    ]
  }
}
```

#### Code Review (AUTH-009: Security Review)

**Input to Code Reviewer:**
```yaml
agent: code-reviewer
input:
  tasks: ["AUTH-001", "AUTH-002", "AUTH-003", "AUTH-004", "AUTH-005", "AUTH-006", "AUTH-007"]
  focus_areas: ["security", "performance", "maintainability"]
  review_scope: "full"
```

**Expected Code Review Output:**
```json
{
  "review_id": "CODE-REVIEW-AUTH-20241220-001",
  "overall_score": 89,
  "security_score": 95,
  "maintainability_score": 87,
  "test_coverage": 92,
  "issues": [
    {
      "severity": "minor",
      "category": "security",
      "file": "src/middleware/auth.js",
      "line": 23,
      "description": "Consider adding rate limiting to prevent brute force attacks",
      "recommendation": "Implement express-rate-limit middleware"
    },
    {
      "severity": "minor",
      "category": "maintainability",
      "file": "src/components/auth/RegisterForm.tsx",
      "line": 15,
      "description": "Complex validation schema could be extracted",
      "recommendation": "Move schema to separate validation file"
    }
  ],
  "recommendations": [
    {
      "type": "security_enhancement",
      "priority": "medium",
      "description": "Add rate limiting to authentication endpoints",
      "implementation": "Install and configure express-rate-limit"
    },
    {
      "type": "code_organization",
      "priority": "low",
      "description": "Extract validation schemas to dedicated files",
      "implementation": "Create src/validations/ directory structure"
    }
  ]
}
```

### 6. Final Report

```json
{
  "workflow_id": "workflow-auth-20241220-001",
  "plan_id": "PLAN-AUTH-20241220-001",
  "status": "completed",
  "completion_time": "4.5 days",
  "summary": {
    "total_tasks": 9,
    "completed_tasks": 9,
    "failed_tasks": 0,
    "success_rate": 100
  },
  "quality_metrics": {
    "code_quality_score": 89,
    "security_score": 95,
    "test_coverage": 92,
    "ui_score": 92,
    "accessibility_score": 96
  },
  "deliverables": {
    "backend_endpoints": [
      "POST /api/auth/register",
      "POST /api/auth/login",
      "POST /api/auth/refresh",
      "POST /api/auth/logout"
    ],
    "frontend_components": [
      "RegisterForm",
      "LoginForm",
      "AuthContext",
      "ProtectedRoute"
    ],
    "database_migrations": [
      "001-create-users-table.sql",
      "002-create-verification-tokens.sql"
    ],
    "tests": {
      "unit_tests": 24,
      "integration_tests": 8,
      "e2e_tests": 6
    }
  },
  "performance_metrics": {
    "registration_api_response_time": "145ms",
    "login_api_response_time": "98ms",
    "frontend_load_time": "1.2s",
    "bundle_size_increase": "12KB"
  }
}
```

## Key Takeaways

1. **Clear Requirements**: Well-defined requirements lead to better planning and implementation
2. **Incremental Approach**: Breaking work into phases enables parallel development and easier tracking
3. **Quality Gates**: Built-in review processes catch issues early
4. **Automated Validation**: Quality assurance agents provide consistent, objective feedback
5. **Comprehensive Documentation**: All decisions and implementations are documented for future reference

## Next Steps

After completing this workflow:
1. Deploy to staging environment
2. Conduct user acceptance testing
3. Security penetration testing
4. Performance load testing
5. Production deployment
6. Monitor and iterate based on user feedback

This example demonstrates how the Claude Code agentic template enables efficient, high-quality feature development through coordinated multi-agent workflows.