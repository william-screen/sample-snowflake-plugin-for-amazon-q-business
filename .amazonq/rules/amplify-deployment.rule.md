# AWS Amplify Deployment

## Purpose
This rule defines the deployment strategy for the Next.js frontend using AWS Amplify with GitHub integration.

## Instructions
- MUST host frontend on AWS Amplify connected to GitHub repository (ID: AMPLIFY_GITHUB_HOSTING)
- ALWAYS use amplify.yml for build configuration in repository root (ID: AMPLIFY_YML_CONFIG)
- MUST deploy CDK backend infrastructure separately from Amplify (ID: SEPARATE_BACKEND_DEPLOYMENT)
- ALWAYS configure environment variables in Amplify console after CDK deployment (ID: AMPLIFY_ENV_VARS)
- MUST use automatic deployments triggered by main branch pushes (ID: AUTO_DEPLOY_MAIN)
- ALWAYS ensure Amplify builds only the frontend app directory (ID: FRONTEND_ONLY_BUILD)
- MUST set AWS_REGION=us-west-2 in Amplify environment variables (ID: AMPLIFY_REGION)
- ALWAYS populate environment variables from CDK outputs and AgentCore endpoints (ID: CDK_OUTPUT_VARS)

## Priority
High

## Error Handling
- If Amplify build fails, check amplify.yml configuration and Node.js version compatibility
- If environment variables are missing, verify CDK deployment completed successfully
- If GitHub connection fails, check repository permissions and webhook configuration
- If build times are excessive, optimize dependencies and build process
