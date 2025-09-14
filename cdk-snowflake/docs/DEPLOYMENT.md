# Deployment Guide

## Prerequisites

- AWS Account with Amazon Q Business access
- Snowflake Account with Cortex Search enabled
- IAM Identity Center instance configured
- Python 3.8+ and AWS CDK installed

## Quick Start

1. **Clone and configure:**
   ```bash
   git clone https://github.com/william-screen/sample-snowflake-plugin-for-amazon-q-business.git
   cd sample-snowflake-plugin-for-amazon-q-business
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Deploy infrastructure:**
   ```bash
   ./scripts/deploy.sh
   ```

3. **Setup Snowflake:**
   ```bash
   python3 scripts/snowflake_automation.py
   ```

4. **Enable General Knowledge:**
   ```bash
   aws qbusiness update-chat-controls-configuration \
     --application-id YOUR_APPLICATION_ID \
     --response-scope EXTENDED_KNOWLEDGE_ENABLED \
     --creator-mode-configuration '{"creatorModeControl": "ENABLED"}'
   ```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SNOWFLAKE_ACCOUNT` | Your Snowflake account identifier | Yes |
| `SNOWFLAKE_USER` | Your Snowflake username | Yes |
| `SNOWFLAKE_PASSWORD` | Your Snowflake password | Yes |
| `IDENTITY_CENTER_INSTANCE_ARN` | IAM Identity Center instance ARN | Yes |
| `AWS_REGION` | AWS region for deployment | No (default: us-east-1) |

### CDK Context

You can also pass configuration via CDK context:

```bash
cdk deploy \
  -c snowflakeAccount=your-account \
  -c snowflakeUser=your-user \
  -c identityCenterInstanceArn=arn:aws:sso:::instance/ssoins-xxxxxxxxx
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.
