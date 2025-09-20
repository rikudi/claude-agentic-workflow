# Coding Standards for Multi-Agent Development

This document establishes coding standards and conventions for projects using the Claude Code agentic template.

## General Principles

### 1. Consistency
- Follow established patterns within the codebase
- Use consistent naming conventions across all files
- Maintain uniform code formatting and style

### 2. Clarity
- Write self-documenting code with clear intent
- Use descriptive variable and function names
- Include comments for complex business logic

### 3. Maintainability
- Keep functions and classes focused and small
- Minimize dependencies and coupling
- Follow SOLID principles

## Language-Specific Standards

### TypeScript/JavaScript

#### Naming Conventions
```typescript
// Variables and functions: camelCase
const userName = 'john_doe';
const calculateTotalPrice = (items: Item[]) => { };

// Constants: SCREAMING_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com';
const MAX_RETRY_ATTEMPTS = 3;

// Classes and interfaces: PascalCase
class UserService { }
interface UserProfile { }
type ApiResponse<T> = { };

// Files: kebab-case
// user-service.ts
// api-client.test.ts
// user-profile.component.tsx
```

#### Code Structure
```typescript
// 1. Imports (external libraries first, then internal)
import React from 'react';
import { Router } from 'express';

import { UserService } from '../services/user-service';
import { validateInput } from '../utils/validation';

// 2. Types and interfaces
interface UserProps {
  id: string;
  name: string;
  email: string;
}

// 3. Constants
const DEFAULT_PAGE_SIZE = 20;

// 4. Main implementation
export class UserController {
  constructor(private userService: UserService) {}

  async getUsers(req: Request, res: Response): Promise<void> {
    // Implementation
  }
}

// 5. Default export (if applicable)
export default UserController;
```

#### Function Guidelines
```typescript
// Good: Clear function signature with proper typing
async function createUser(
  userData: UserCreateData,
  options: CreateUserOptions = {}
): Promise<User> {
  // Validate input
  const validatedData = validateUserData(userData);

  // Business logic
  const user = await userService.create(validatedData);

  // Return result
  return user;
}

// Bad: Unclear parameters and return type
function createUser(data: any, opts?: any): any {
  // Implementation
}
```

### Python

#### Naming Conventions
```python
# Variables and functions: snake_case
user_name = "john_doe"
def calculate_total_price(items: List[Item]) -> Decimal:
    pass

# Constants: SCREAMING_SNAKE_CASE
API_BASE_URL = "https://api.example.com"
MAX_RETRY_ATTEMPTS = 3

# Classes: PascalCase
class UserService:
    pass

# Files: snake_case
# user_service.py
# api_client_test.py
```

#### Code Structure
```python
"""
Module docstring explaining the purpose and usage.
"""

# 1. Standard library imports
import json
import logging
from typing import List, Optional, Dict, Any

# 2. Third-party imports
import requests
from fastapi import FastAPI, HTTPException

# 3. Local imports
from .models import User, UserCreate
from .services import UserService
from .utils import validate_email

# 4. Constants
DEFAULT_PAGE_SIZE = 20
LOGGER = logging.getLogger(__name__)

# 5. Classes and functions
class UserController:
    """Handles user-related HTTP endpoints."""

    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user account.

        Args:
            user_data: User creation data

        Returns:
            Created user instance

        Raises:
            HTTPException: If validation fails or user exists
        """
        # Implementation
        pass
```

## Testing Standards

### Test Organization
```
tests/
├── unit/                 # Unit tests
│   ├── services/
│   ├── controllers/
│   └── utils/
├── integration/          # Integration tests
│   ├── api/
│   └── database/
├── e2e/                 # End-to-end tests
│   └── user-flows/
└── fixtures/            # Test data and fixtures
    ├── users.json
    └── products.json
```

### Test Naming
```typescript
// Test file naming: [module].test.[ext]
// user-service.test.ts
// payment-processor.test.ts

// Test function naming: descriptive scenarios
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', async () => {
      // Test implementation
    });

    it('should throw error when email already exists', async () => {
      // Test implementation
    });

    it('should validate required fields', async () => {
      // Test implementation
    });
  });
});
```

### Test Structure (AAA Pattern)
```typescript
it('should calculate discount correctly for premium users', async () => {
  // Arrange
  const user = createMockUser({ type: 'premium' });
  const order = createMockOrder({ total: 100 });
  const discountService = new DiscountService();

  // Act
  const discountedTotal = await discountService.applyDiscount(user, order);

  // Assert
  expect(discountedTotal).toBe(85); // 15% discount
  expect(order.discountApplied).toBe(15);
});
```

## Documentation Standards

### Code Comments
```typescript
/**
 * Calculates the optimal shipping route for multiple destinations.
 *
 * Uses the Traveling Salesman Problem algorithm with nearest neighbor
 * heuristic for performance with large datasets.
 *
 * @param origin - Starting location coordinates
 * @param destinations - Array of delivery locations
 * @param constraints - Delivery time windows and vehicle capacity
 * @returns Optimized route with estimated delivery times
 *
 * @example
 * ```typescript
 * const route = calculateOptimalRoute(
 *   { lat: 40.7128, lng: -74.0060 },
 *   destinations,
 *   { maxStops: 10, timeWindow: '09:00-17:00' }
 * );
 * ```
 */
async function calculateOptimalRoute(
  origin: Coordinates,
  destinations: Destination[],
  constraints: RouteConstraints
): Promise<OptimizedRoute> {
  // Implementation
}
```

### API Documentation
```typescript
/**
 * @api {post} /api/v1/users Create User
 * @apiName CreateUser
 * @apiGroup Users
 * @apiVersion 1.0.0
 *
 * @apiDescription Creates a new user account with the provided information.
 *
 * @apiParam {String} email User's email address (must be unique)
 * @apiParam {String} username Desired username (3-50 characters)
 * @apiParam {String} password Strong password (min 8 characters)
 * @apiParam {String} [firstName] User's first name
 * @apiParam {String} [lastName] User's last name
 *
 * @apiSuccess {String} id Unique user identifier
 * @apiSuccess {String} email User's email address
 * @apiSuccess {String} username User's username
 * @apiSuccess {String} createdAt Account creation timestamp
 *
 * @apiError (400) ValidationError Invalid input data
 * @apiError (409) ConflictError Email or username already exists
 * @apiError (500) InternalError Server error occurred
 *
 * @apiExample {curl} Example Request:
 * curl -X POST \
 *   https://api.example.com/v1/users \
 *   -H 'Content-Type: application/json' \
 *   -d '{
 *     "email": "user@example.com",
 *     "username": "johndoe",
 *     "password": "SecurePass123",
 *     "firstName": "John",
 *     "lastName": "Doe"
 *   }'
 */
```

## Security Standards

### Input Validation
```typescript
// Always validate and sanitize input
function createUser(userData: UserCreateData): Promise<User> {
  // Validate input schema
  const validationResult = userCreateSchema.safeParse(userData);
  if (!validationResult.success) {
    throw new ValidationError(validationResult.error);
  }

  // Sanitize input
  const sanitizedData = {
    email: sanitizeEmail(userData.email),
    username: sanitizeUsername(userData.username),
    // Never store plain text passwords
    password: hashPassword(userData.password)
  };

  return userService.create(sanitizedData);
}
```

### Secret Management
```typescript
// Good: Use environment variables
const config = {
  database: {
    host: process.env.DB_HOST,
    password: process.env.DB_PASSWORD,
  },
  jwt: {
    secret: process.env.JWT_SECRET,
  }
};

// Bad: Hardcoded secrets
const config = {
  database: {
    password: "hardcoded_password", // Never do this
  }
};
```

### Authentication and Authorization
```typescript
// Implement proper authentication middleware
async function requireAuth(req: Request, res: Response, next: NextFunction) {
  try {
    const token = extractToken(req);
    const user = await verifyToken(token);

    // Add user to request context
    req.user = user;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Authentication required' });
  }
}

// Role-based authorization
function requireRole(roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
}
```

## Performance Standards

### Database Queries
```typescript
// Good: Efficient query with proper indexing
async function getUsersWithPosts(userId: string): Promise<UserWithPosts> {
  return await db.user.findUnique({
    where: { id: userId },
    include: {
      posts: {
        select: { id: true, title: true, createdAt: true },
        orderBy: { createdAt: 'desc' },
        take: 10
      }
    }
  });
}

// Bad: N+1 query problem
async function getUsersWithPosts(): Promise<UserWithPosts[]> {
  const users = await db.user.findMany();

  // This creates N+1 queries
  for (const user of users) {
    user.posts = await db.post.findMany({
      where: { userId: user.id }
    });
  }

  return users;
}
```

### Caching Strategies
```typescript
// Implement appropriate caching
class UserService {
  private cache = new Map<string, User>();

  async getUser(id: string): Promise<User | null> {
    // Check cache first
    if (this.cache.has(id)) {
      return this.cache.get(id)!;
    }

    // Fetch from database
    const user = await this.repository.findById(id);

    if (user) {
      // Cache with TTL
      this.cache.set(id, user);
      setTimeout(() => this.cache.delete(id), 300000); // 5 minutes
    }

    return user;
  }
}
```

## Error Handling Standards

### Structured Error Handling
```typescript
// Define custom error types
class ValidationError extends Error {
  constructor(
    public field: string,
    public value: any,
    public constraint: string
  ) {
    super(`Validation failed for ${field}: ${constraint}`);
    this.name = 'ValidationError';
  }
}

class NotFoundError extends Error {
  constructor(resource: string, id: string) {
    super(`${resource} with id ${id} not found`);
    this.name = 'NotFoundError';
  }
}

// Centralized error handler
function handleError(error: Error, req: Request, res: Response) {
  const errorId = generateErrorId();

  // Log error for debugging
  logger.error('Request error', {
    errorId,
    error: error.message,
    stack: error.stack,
    request: {
      method: req.method,
      url: req.url,
      headers: req.headers
    }
  });

  // Return appropriate response
  if (error instanceof ValidationError) {
    return res.status(400).json({
      error: 'Validation Error',
      message: error.message,
      errorId
    });
  }

  if (error instanceof NotFoundError) {
    return res.status(404).json({
      error: 'Not Found',
      message: error.message,
      errorId
    });
  }

  // Generic server error
  return res.status(500).json({
    error: 'Internal Server Error',
    message: 'An unexpected error occurred',
    errorId
  });
}
```

## Git and Version Control Standards

### Commit Messages
```
feat: add user authentication with JWT tokens

- Implement login and registration endpoints
- Add password hashing with bcrypt
- Create JWT token generation and validation
- Add authentication middleware for protected routes

Closes #123
```

### Branch Naming
```bash
# Feature branches
feature/user-authentication
feature/payment-integration
feature/admin-dashboard

# Bug fixes
bugfix/login-validation-error
bugfix/payment-processing-timeout

# Hotfixes
hotfix/security-vulnerability-patch
hotfix/critical-performance-issue

# Release branches
release/v1.2.0
release/v2.0.0-beta
```

### Pull Request Template
```markdown
## Description
Brief description of the changes and their purpose.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings or errors introduced
```

## Code Review Guidelines

### Review Checklist
```markdown
## Functionality
- [ ] Code meets requirements and acceptance criteria
- [ ] Edge cases are handled appropriately
- [ ] Error handling is comprehensive
- [ ] Performance implications considered

## Code Quality
- [ ] Code is readable and well-structured
- [ ] Functions are focused and single-purpose
- [ ] Naming conventions followed
- [ ] No code duplication

## Security
- [ ] Input validation implemented
- [ ] Authentication and authorization appropriate
- [ ] No hardcoded secrets or sensitive data
- [ ] SQL injection and XSS vulnerabilities addressed

## Testing
- [ ] Adequate test coverage
- [ ] Tests are meaningful and well-written
- [ ] All tests pass
- [ ] Test data is appropriate

## Documentation
- [ ] Code is self-documenting
- [ ] Complex logic is commented
- [ ] API documentation updated
- [ ] README updated if necessary
```

### Review Comments
```markdown
# Constructive feedback examples

## Suggestion
Consider using a Map instead of an object for better performance with large datasets:
```typescript
// Instead of
const userLookup = {};

// Consider
const userLookup = new Map<string, User>();
```

## Nitpick
Minor style issue - consider using const for immutable values:
```typescript
// Instead of
let maxRetries = 3;

// Use
const MAX_RETRIES = 3;
```

## Must Fix
This function is vulnerable to SQL injection. Please use parameterized queries:
```typescript
// Vulnerable
const query = `SELECT * FROM users WHERE id = ${userId}`;

// Safe
const query = 'SELECT * FROM users WHERE id = ?';
const result = await db.query(query, [userId]);
```
```

These coding standards ensure consistency, maintainability, and quality across all projects using the Claude Code agentic template. Teams should adapt these guidelines to their specific technology stacks and organizational requirements.