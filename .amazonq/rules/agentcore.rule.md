# AgentCore Development

## Purpose
This rule ensures proper AgentCore development practices, local testing requirements, and deployment procedures for the multimedia RAG chatbot project.

## Instructions
- ALWAYS test AgentCore locally with Docker before any deployment using: `docker build --no-cache -t multimedia-rag-agent:latest .` (ID: LOCAL_DOCKER_TEST)
- MUST use correct import: `from bedrock_agentcore.runtime import BedrockAgentCoreApp` NOT `from bedrock_agentcore import BedrockAgentCoreApp` (ID: CORRECT_IMPORT)
- ALWAYS include OpenTelemetry instrumentation in Dockerfile CMD: `CMD ["opentelemetry-instrument", "python", "multimedia_rag_agent.py"]` (ID: OTEL_INSTRUMENTATION)
- MUST use correct agentcore invoke format: `agentcore invoke '{"input": {"prompt": "query"}}'` NOT `'{"message": "query"}'` (ID: CORRECT_INVOKE_FORMAT)
- ALWAYS use Claude 3.7 Sonnet model: `us.anthropic.claude-3-7-sonnet-20250219-v1:0` in agent decorator (ID: CLAUDE_MODEL)
- MUST include required packages in requirements.txt: bedrock-agentcore, 'strands-agents[otel]', aws-opentelemetry-distro, pydantic, maplibre (ID: REQUIRED_PACKAGES)
- When creating agents, ALWAYS use Strands Agents framework with structured output using Pydantic models (ID: STRANDS_STRUCTURED_OUTPUT)
- MUST mount AWS credentials for local testing: `-v ~/.aws:/root/.aws:ro -e AWS_DEFAULT_REGION=us-west-2` (ID: AWS_CREDENTIALS_MOUNT)

## Priority
Critical

## Error Handling
- If Docker build fails, check for --no-cache flag and correct import statements
- If agentcore invoke fails, verify the correct JSON format with "input" and "prompt" keys
- If model access fails, check IAM permissions for Claude 3.7 Sonnet model
- If local testing fails, verify AWS credentials are properly mounted and region is set
