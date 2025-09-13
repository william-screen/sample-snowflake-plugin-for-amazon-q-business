# Testing

## Purpose
This rule ensures thorough testing of each step and function before moving to the next development phase, preventing bugs from reaching QA and production.

## Instructions
- MUST test every function and component before proceeding to next development step (ID: TEST_BEFORE_PROCEED)
- ALWAYS implement Playwright end-to-end tests for all user flows and interactions (ID: PLAYWRIGHT_E2E)
- MUST create unit tests using Jest for all utility functions, hooks, and business logic (ID: JEST_UNIT_TESTS)
- ALWAYS test React components using React Testing Library with proper accessibility checks (ID: RTL_COMPONENT_TESTS)
- MUST test API routes with both success and error scenarios before frontend integration (ID: API_ROUTE_TESTS)
- ALWAYS run `npm test` and ensure 100% pass rate before committing code (ID: FULL_TEST_PASS)
- MUST test AgentCore locally with Docker and verify responses before deployment (ID: AGENTCORE_LOCAL_TEST)
- ALWAYS test Canvas artifact rendering for all artifact types (chart, image, document, table, video, audio, url, map) (ID: CANVAS_ARTIFACT_TESTS)
- MUST test LlamaIndex message format handling and parts array processing (ID: LLAMAINDEX_FORMAT_TESTS)
- ALWAYS test error boundaries and fallback states for failed artifact rendering (ID: ERROR_BOUNDARY_TESTS)
- MUST test responsive design on mobile, tablet, and desktop viewports using Playwright (ID: RESPONSIVE_TESTS)
- ALWAYS test accessibility compliance using axe-core in Playwright tests (ID: ACCESSIBILITY_TESTS)
- MUST test AWS service integrations with mocked responses before live testing (ID: AWS_MOCK_TESTS)
- ALWAYS create integration tests for CDK infrastructure using AWS CDK testing utilities (ID: CDK_INTEGRATION_TESTS)
- MUST test Amplify deployment pipeline with staging environment before production (ID: AMPLIFY_STAGING_TESTS)

## Priority
Critical

## Error Handling
- If tests fail, NEVER proceed to next step - fix failing tests first
- If Playwright tests are flaky, investigate and stabilize before continuing
- If API tests fail, check both request format and response handling
- If Canvas tests fail, verify artifact data structure and rendering logic
- If accessibility tests fail, address issues before deployment
- If CDK tests fail, verify resource configurations and permissions
