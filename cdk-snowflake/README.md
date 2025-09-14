# CDK Snowflake Cortex Search Plugin

This directory contains the AWS CDK infrastructure code for the Snowflake Cortex Search + Amazon Q Business integration.

## Quick Start

```bash
# Install dependencies
npm install
pip install -r ../requirements.txt

# Deploy infrastructure
./scripts/deploy.sh

# Setup Snowflake
python3 src/lambda/snowflake_automation.py
```

## Project Structure

```
cdk-snowflake/
├── bin/                         # CDK app entry point
├── lib/                         # CDK stack definitions
├── src/                         # Source code
│   ├── lambda/                  # Lambda function code
│   └── openapi/                 # OpenAPI schema
├── scripts/                     # Utility scripts
├── docs/                        # Documentation
├── assets/                      # Static assets
└── tests/                       # Test files
```

## Configuration

Set environment variables or CDK context:

```bash
export SNOWFLAKE_ACCOUNT="your-account-identifier"
export SNOWFLAKE_USER="your-snowflake-username"
export IDENTITY_CENTER_INSTANCE_ARN="arn:aws:sso:::instance/ssoins-xxxxxxxxx"
```

## Deployment

```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy
```

See the main [README.md](../README.md) for complete setup instructions.
