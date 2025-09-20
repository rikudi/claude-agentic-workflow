# Testing Guidelines for Multi-Agent Development

This document provides comprehensive testing guidelines for projects using the Claude Code agentic template, covering unit tests, integration tests, end-to-end tests, and agent-specific testing strategies.

## Testing Philosophy

### Test Pyramid Principles
```
    /\     E2E Tests (Few)
   /  \    - Critical user journeys
  /____\   - Cross-browser compatibility
 /      \
/__UI___\  Integration Tests (Some)
/        \ - API endpoints
/_________ \ - Database interactions
/          \
/___UNIT___\ Unit Tests (Many)
             - Business logic
             - Utility functions
             - Component behavior
```

### Quality Standards
- **Unit Test Coverage**: ≥ 80%
- **Integration Test Coverage**: ≥ 60%
- **Critical Path E2E Coverage**: 100%
- **Test Reliability**: ≥ 95% pass rate
- **Test Performance**: Unit tests < 10ms, Integration < 1s

## Unit Testing Standards

### Test Structure (AAA Pattern)
```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', async () => {
      // Arrange
      const userData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'SecurePass123'
      };
      const mockRepository = createMockRepository();
      const userService = new UserService(mockRepository);

      // Act
      const result = await userService.createUser(userData);

      // Assert
      expect(result).toBeDefined();
      expect(result.email).toBe(userData.email);
      expect(result.username).toBe(userData.username);
      expect(result.password).not.toBe(userData.password); // Should be hashed
      expect(mockRepository.save).toHaveBeenCalledWith(
        expect.objectContaining({
          email: userData.email,
          username: userData.username
        })
      );
    });

    it('should throw ValidationError for invalid email', async () => {
      // Arrange
      const invalidUserData = {
        email: 'invalid-email',
        username: 'testuser',
        password: 'SecurePass123'
      };
      const userService = new UserService(createMockRepository());

      // Act & Assert
      await expect(userService.createUser(invalidUserData))
        .rejects
        .toThrow(ValidationError);
    });
  });
});
```

### Mock Strategies
```typescript
// 1. Mock external dependencies
jest.mock('../database/connection', () => ({
  query: jest.fn(),
  transaction: jest.fn()
}));

// 2. Create factory functions for test data
function createMockUser(overrides: Partial<User> = {}): User {
  return {
    id: 'user-123',
    email: 'test@example.com',
    username: 'testuser',
    createdAt: new Date(),
    ...overrides
  };
}

// 3. Use dependency injection for testability
class UserService {
  constructor(
    private userRepository: UserRepository,
    private emailService: EmailService,
    private logger: Logger
  ) {}

  async createUser(userData: UserCreateData): Promise<User> {
    // Implementation
  }
}

// In tests
const mockUserRepository = {
  save: jest.fn(),
  findByEmail: jest.fn(),
  findById: jest.fn()
} as jest.Mocked<UserRepository>;

const mockEmailService = {
  sendWelcomeEmail: jest.fn()
} as jest.Mocked<EmailService>;

const userService = new UserService(
  mockUserRepository,
  mockEmailService,
  console
);
```

### Testing Async Code
```typescript
// Promise-based testing
it('should handle async operations correctly', async () => {
  const promise = userService.createUser(validUserData);

  await expect(promise).resolves.toBeDefined();
  // or
  const result = await userService.createUser(validUserData);
  expect(result).toBeDefined();
});

// Error handling in async code
it('should handle async errors properly', async () => {
  mockRepository.save.mockRejectedValue(new Error('Database error'));

  await expect(userService.createUser(validUserData))
    .rejects
    .toThrow('Database error');
});

// Testing timeouts
it('should timeout after specified duration', async () => {
  jest.setTimeout(10000); // 10 seconds

  mockApiClient.request.mockImplementation(
    () => new Promise(resolve => setTimeout(resolve, 15000))
  );

  await expect(apiService.getData())
    .rejects
    .toThrow('Request timeout');
});
```

## Integration Testing

### API Endpoint Testing
```typescript
// Using supertest for Express.js
import request from 'supertest';
import { app } from '../app';
import { setupTestDatabase, teardownTestDatabase } from './test-utils';

describe('User API', () => {
  beforeAll(async () => {
    await setupTestDatabase();
  });

  afterAll(async () => {
    await teardownTestDatabase();
  });

  beforeEach(async () => {
    await clearDatabase();
  });

  describe('POST /api/v1/users', () => {
    it('should create user with valid data', async () => {
      const userData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'SecurePass123'
      };

      const response = await request(app)
        .post('/api/v1/users')
        .send(userData)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.any(String),
        email: userData.email,
        username: userData.username,
        createdAt: expect.any(String)
      });

      // Verify user was actually created in database
      const createdUser = await userRepository.findById(response.body.id);
      expect(createdUser).toBeDefined();
    });

    it('should return 400 for duplicate email', async () => {
      // Create existing user
      await userRepository.create({
        email: 'existing@example.com',
        username: 'existing',
        password: 'hashedPassword'
      });

      const response = await request(app)
        .post('/api/v1/users')
        .send({
          email: 'existing@example.com',
          username: 'newuser',
          password: 'SecurePass123'
        })
        .expect(400);

      expect(response.body.error).toBe('Email already exists');
    });
  });
});
```

### Database Integration Testing
```typescript
describe('UserRepository', () => {
  let repository: UserRepository;
  let db: Database;

  beforeAll(async () => {
    db = await createTestDatabase();
    repository = new UserRepository(db);
  });

  afterAll(async () => {
    await db.close();
  });

  beforeEach(async () => {
    await db.query('DELETE FROM users');
  });

  it('should save and retrieve user correctly', async () => {
    const userData = {
      email: 'test@example.com',
      username: 'testuser',
      passwordHash: 'hashedPassword'
    };

    // Save user
    const savedUser = await repository.save(userData);
    expect(savedUser.id).toBeDefined();

    // Retrieve user
    const retrievedUser = await repository.findById(savedUser.id);
    expect(retrievedUser).toMatchObject(userData);
  });

  it('should handle database constraints', async () => {
    const userData = {
      email: 'test@example.com',
      username: 'testuser',
      passwordHash: 'hashedPassword'
    };

    await repository.save(userData);

    // Try to save user with same email
    await expect(repository.save({
      ...userData,
      username: 'different'
    })).rejects.toThrow('Email already exists');
  });
});
```

## End-to-End Testing

### User Journey Testing with Playwright
```typescript
import { test, expect } from '@playwright/test';

test.describe('User Registration Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Reset test environment
    await page.goto('/reset-test-data');
  });

  test('complete user registration journey', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/register');

    // Fill registration form
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="username-input"]', 'testuser');
    await page.fill('[data-testid="password-input"]', 'SecurePass123');
    await page.fill('[data-testid="confirm-password-input"]', 'SecurePass123');

    // Submit form
    await page.click('[data-testid="submit-button"]');

    // Verify successful registration
    await expect(page.locator('[data-testid="success-message"]'))
      .toContainText('Registration successful');

    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard');

    // Verify user is logged in
    await expect(page.locator('[data-testid="user-menu"]'))
      .toContainText('testuser');
  });

  test('should show validation errors for invalid input', async ({ page }) => {
    await page.goto('/register');

    // Submit form without filling required fields
    await page.click('[data-testid="submit-button"]');

    // Verify validation errors
    await expect(page.locator('[data-testid="email-error"]'))
      .toContainText('Email is required');
    await expect(page.locator('[data-testid="username-error"]'))
      .toContainText('Username is required');
    await expect(page.locator('[data-testid="password-error"]'))
      .toContainText('Password is required');
  });
});
```

### Cross-Browser Testing
```typescript
// playwright.config.ts
import { PlaywrightTestConfig, devices } from '@playwright/test';

const config: PlaywrightTestConfig = {
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
};

export default config;
```

## Agent-Specific Testing

### Testing Subagent Functionality
```typescript
describe('Frontend Coder Agent', () => {
  let agent: FrontendCoderAgent;
  let mockTools: MockClaudeCodeTools;

  beforeEach(() => {
    mockTools = createMockClaudeCodeTools();
    agent = new FrontendCoderAgent(mockTools);
  });

  it('should create React component with proper structure', async () => {
    const task = {
      task_id: 'COMP-001',
      component_name: 'Button',
      props: ['children', 'onClick', 'variant'],
      styling: 'tailwind'
    };

    mockTools.read.mockResolvedValue('// existing component patterns');
    mockTools.write.mockResolvedValue(undefined);

    const result = await agent.createComponent(task);

    expect(result.status).toBe('success');
    expect(result.files_created).toContain('Button.tsx');
    expect(result.files_created).toContain('Button.test.tsx');

    // Verify component structure
    const componentCall = mockTools.write.mock.calls.find(
      call => call[0].endsWith('Button.tsx')
    );
    const componentContent = componentCall[1];

    expect(componentContent).toContain('interface ButtonProps');
    expect(componentContent).toContain('export const Button');
    expect(componentContent).toContain('React.FC<ButtonProps>');
  });

  it('should handle tool errors gracefully', async () => {
    const task = {
      task_id: 'COMP-002',
      component_name: 'Modal',
      props: ['isOpen', 'onClose', 'children']
    };

    mockTools.read.mockRejectedValue(new Error('File not found'));

    const result = await agent.createComponent(task);

    expect(result.status).toBe('error');
    expect(result.error).toContain('File not found');
    expect(mockTools.write).not.toHaveBeenCalled();
  });
});
```

### Testing Agent Coordination
```typescript
describe('Multi-Agent Workflow', () => {
  let workflow: MultiAgentWorkflow;
  let mockAgents: MockAgents;

  beforeEach(() => {
    mockAgents = {
      planner: createMockPlannerAgent(),
      planReviewer: createMockPlanReviewerAgent(),
      frontendCoder: createMockFrontendCoderAgent(),
      backendCoder: createMockBackendCoderAgent()
    };
    workflow = new MultiAgentWorkflow(mockAgents);
  });

  it('should execute complete feature implementation workflow', async () => {
    const requirements = {
      feature: 'user_authentication',
      scope: ['login', 'registration', 'password_reset']
    };

    // Mock planner response
    mockAgents.planner.createPlan.mockResolvedValue({
      plan_id: 'PLAN-001',
      phases: [
        {
          phase_id: 'PHASE-1',
          tasks: [
            { task_id: 'AUTH-001', assigned_agent: 'backend-coder' },
            { task_id: 'AUTH-002', assigned_agent: 'frontend-coder' }
          ]
        }
      ]
    });

    // Mock plan reviewer approval
    mockAgents.planReviewer.reviewPlan.mockResolvedValue({
      status: 'approved',
      plan_id: 'PLAN-001'
    });

    // Mock implementation
    mockAgents.backendCoder.implementTask.mockResolvedValue({
      status: 'completed',
      task_id: 'AUTH-001'
    });

    mockAgents.frontendCoder.implementTask.mockResolvedValue({
      status: 'completed',
      task_id: 'AUTH-002'
    });

    const result = await workflow.execute(requirements);

    expect(result.status).toBe('completed');
    expect(result.plan_id).toBe('PLAN-001');
    expect(result.completed_tasks).toHaveLength(2);

    // Verify workflow sequence
    expect(mockAgents.planner.createPlan).toHaveBeenCalledWith(requirements);
    expect(mockAgents.planReviewer.reviewPlan).toHaveBeenCalledAfter(
      mockAgents.planner.createPlan
    );
    expect(mockAgents.backendCoder.implementTask).toHaveBeenCalledAfter(
      mockAgents.planReviewer.reviewPlan
    );
  });
});
```

## Performance Testing

### Load Testing with Artillery
```yaml
# artillery-config.yml
config:
  target: 'http://localhost:3000'
  phases:
    - duration: 60
      arrivalRate: 10  # 10 users per second
    - duration: 120
      arrivalRate: 20  # Ramp up to 20 users per second

scenarios:
  - name: 'User Registration Flow'
    flow:
      - post:
          url: '/api/v1/users'
          json:
            email: 'test{{ $randomNumber() }}@example.com'
            username: 'user{{ $randomNumber() }}'
            password: 'SecurePass123'
      - think: 2  # 2 second pause
      - post:
          url: '/api/v1/auth/login'
          json:
            email: 'test{{ $randomNumber() }}@example.com'
            password: 'SecurePass123'
```

### Database Performance Testing
```typescript
describe('Database Performance', () => {
  it('should handle concurrent user creation', async () => {
    const concurrentUsers = 100;
    const userPromises = Array.from({ length: concurrentUsers }, (_, i) =>
      userService.createUser({
        email: `user${i}@example.com`,
        username: `user${i}`,
        password: 'SecurePass123'
      })
    );

    const start = Date.now();
    const results = await Promise.all(userPromises);
    const duration = Date.now() - start;

    expect(results).toHaveLength(concurrentUsers);
    expect(duration).toBeLessThan(5000); // Should complete in under 5 seconds
  });

  it('should maintain response time under load', async () => {
    // Pre-populate database with test data
    await populateTestData(10000);

    const start = Date.now();
    const users = await userService.searchUsers('test', { limit: 50 });
    const duration = Date.now() - start;

    expect(users).toHaveLength(50);
    expect(duration).toBeLessThan(1000); // Should respond in under 1 second
  });
});
```

## Test Data Management

### Test Fixtures
```typescript
// fixtures/users.ts
export const userFixtures = {
  validUser: {
    email: 'valid@example.com',
    username: 'validuser',
    password: 'SecurePass123'
  },

  adminUser: {
    email: 'admin@example.com',
    username: 'admin',
    password: 'AdminPass123',
    role: 'admin'
  },

  incompleteUser: {
    email: 'incomplete@example.com'
    // Missing username and password
  }
};

// fixtures/api-responses.ts
export const apiFixtures = {
  successfulUserCreation: {
    id: 'user-123',
    email: 'test@example.com',
    username: 'testuser',
    createdAt: '2024-01-01T00:00:00Z'
  },

  validationError: {
    error: 'Validation Error',
    message: 'Email is required',
    field: 'email'
  }
};
```

### Database Seeding
```typescript
// test-utils/database.ts
export async function seedTestDatabase() {
  // Clear existing data
  await db.query('DELETE FROM posts');
  await db.query('DELETE FROM users');

  // Create test users
  const users = await Promise.all([
    userRepository.create(userFixtures.validUser),
    userRepository.create(userFixtures.adminUser)
  ]);

  // Create test posts
  await Promise.all([
    postRepository.create({
      title: 'Test Post 1',
      content: 'Content for test post 1',
      authorId: users[0].id
    }),
    postRepository.create({
      title: 'Test Post 2',
      content: 'Content for test post 2',
      authorId: users[1].id
    })
  ]);

  return { users };
}
```

## Test Automation and CI/CD

### GitHub Actions Workflow
```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run database migrations
        run: npm run db:migrate
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test

      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Start application
        run: npm run start:test &

      - name: Wait for application
        run: npx wait-on http://localhost:3000

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

## Test Reporting and Metrics

### Coverage Reporting
```json
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './src/services/': {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    }
  }
};
```

### Test Metrics Dashboard
```typescript
// Generate test metrics report
export function generateTestMetrics(testResults: TestResults) {
  return {
    summary: {
      total: testResults.numTotalTests,
      passed: testResults.numPassedTests,
      failed: testResults.numFailedTests,
      skipped: testResults.numPendingTests,
      passRate: (testResults.numPassedTests / testResults.numTotalTests) * 100
    },
    coverage: {
      statements: testResults.coverageMap.statements.pct,
      branches: testResults.coverageMap.branches.pct,
      functions: testResults.coverageMap.functions.pct,
      lines: testResults.coverageMap.lines.pct
    },
    performance: {
      totalTime: testResults.testExecTime,
      averageTime: testResults.testExecTime / testResults.numTotalTests,
      slowestTests: findSlowestTests(testResults, 5)
    }
  };
}
```

These testing guidelines ensure comprehensive coverage and quality assurance across all aspects of multi-agent development projects. Teams should adapt these practices to their specific technology stacks and project requirements while maintaining the core principles of thorough, reliable, and maintainable testing.