# Snowflake Cortex Search + Amazon Q Business Integration

Connect Amazon Q Business to Snowflake Cortex Search for natural language queries over your Snowflake data.

## Quick Start

### Prerequisites
- AWS Account with Amazon Q Business access
- Snowflake Account with Cortex Search enabled
- IAM Identity Center instance configured

### 1. Deploy Infrastructure

```bash
git clone https://github.com/william-screen/sample-snowflake-plugin-for-amazon-q-business.git
cd sample-snowflake-plugin-for-amazon-q-business/cdk-snowflake
npm install
pip install -r requirements.txt
./scripts/deploy.sh
```

### 2. Configure Environment

Set your Snowflake credentials:

```bash
cd cdk-snowflake
cp .env.example .env
# Edit .env with your Snowflake details
```

### 3. Setup Snowflake

```bash
python3 src/lambda/snowflake_automation.py
```

### 4. Enable General Knowledge

```bash
aws qbusiness update-chat-controls-configuration \
  --application-id YOUR_APPLICATION_ID \
  --response-scope EXTENDED_KNOWLEDGE_ENABLED \
  --region us-east-1
```

## Usage

Ask natural language questions about your documents:

- *"What is the part description for part number G4204-68741?"*
- *"What are the pump head assembly parts?"*
- *"What are the steps for replacing the heat exchanger?"*

## Configuration

Required environment variables:

```bash
SNOWFLAKE_ACCOUNT=your-account-identifier
SNOWFLAKE_USER=your-snowflake-username
SNOWFLAKE_PASSWORD=your-snowflake-password
IDENTITY_CENTER_INSTANCE_ARN=arn:aws:sso:::instance/ssoins-xxxxxxxxx
```

## Cleanup

```bash
cd cdk-snowflake
cdk destroy
```

## Architecture

- **Amazon Q Business** - Conversational AI interface
- **Snowflake Cortex Search** - Vector search over processed documents
- **AWS CDK** - Infrastructure as code deployment
- **OAuth 2.0** - Secure authentication between services

## Documentation

- [Deployment Guide](cdk-snowflake/docs/DEPLOYMENT.md)
- [Troubleshooting](cdk-snowflake/docs/TROUBLESHOOTING.md)
- [CDK Documentation](cdk-snowflake/README.md)

## License

This project is licensed under the MIT-0 License - see the [LICENSE](LICENSE) file for details.
