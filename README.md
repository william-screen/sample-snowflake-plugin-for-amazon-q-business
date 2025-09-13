# Snowflake Cortex + Amazon Q Business RAG Integration

This CDK project automates the deployment of a RAG (Retrieval Augmented Generation) system that connects Amazon Q Business to Snowflake Cortex Search, based on the [Snowflake quickstart guide](https://quickstarts.snowflake.com/guide/getting_started_with_amazon_q_business%20and_cortex/index.html).

## Architecture

The solution automates these 7 key steps:

1. **Prerequisites Setup** - AWS and Snowflake account requirements
2. **Snowflake Infrastructure** - Database, warehouse, and stage creation
3. **Document Processing** - PDF parsing and text chunking
4. **Cortex Search Service** - Vector search service creation
5. **Amazon Q Business App** - Q Business application setup
6. **OAuth Integration** - Secure connection between Q and Snowflake
7. **Plugin Configuration** - Custom plugin for Cortex Search queries

## What Gets Deployed

### AWS Resources
- **Amazon Q Business Application** - Main chat interface
- **Lambda Function** - Snowflake API operations
- **S3 Bucket** - PDF document storage
- **Secrets Manager** - Snowflake credentials and OAuth tokens
- **IAM Roles** - Required permissions for Q Business
- **Custom Plugin** - Connects Q Business to Cortex Search

### Snowflake Resources (via API)
- **HOL_WH Warehouse** - Compute resources
- **PUMP_DB Database** - Data storage
- **DOCS Stage** - File upload area
- **PUMP_TABLE** - Raw document data
- **PUMP_TABLE_CHUNK** - Processed text chunks
- **PUMP_SEARCH_SERVICE** - Cortex Search service
- **Q_AUTH_HOL** - OAuth integration

## Prerequisites

1. **AWS Account** with Amazon Q Business access
2. **Snowflake Account** with Cortex Search enabled
3. **IAM Identity Center** instance configured
4. **Node.js 18+** and **AWS CDK** installed

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
cd /Users/bscreen/Documents/Development/snowflake-qbusiness-rag
npm install
```

### 2. Configure Environment

Set your configuration via environment variables:

```bash
export SNOWFLAKE_ACCOUNT="your-account-identifier"
export SNOWFLAKE_USER="your-snowflake-username"
export IDENTITY_CENTER_INSTANCE_ARN="arn:aws:sso:::instance/ssoins-xxxxxxxxx"
```

Or pass via CDK context:

```bash
cdk deploy \
  -c snowflakeAccount=your-account \
  -c snowflakeUser=your-user \
  -c identityCenterInstanceArn=arn:aws:sso:::instance/ssoins-xxxxxxxxx
```

### 3. Deploy the Stack

```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy
```

### 4. **CRITICAL: Enable General Knowledge**

After deployment, you **MUST** enable General Knowledge for file uploads to work:

```bash
# Get the Application ID from CDK output, then run:
aws qbusiness update-chat-controls-configuration \
  --application-id YOUR_APPLICATION_ID \
  --response-scope EXTENDED_KNOWLEDGE_ENABLED \
  --creator-mode-configuration '{"creatorModeControl": "ENABLED"}' \
  --region us-east-1
```

**Without this step, users will get "Amazon Q was not configured correctly" errors.**

### 5. Upload Sample Documents

After deployment, upload the pump maintenance PDFs to the created S3 bucket:

```bash
# Download sample documents
curl -O https://raw.githubusercontent.com/Snowflake-Labs/sfguide-getting-started-with-amazon-q-for-business-and-cortex/main/1290IF_PumpHeadMaintenance_TN.pdf
curl -O https://raw.githubusercontent.com/Snowflake-Labs/sfguide-getting-started-with-amazon-q-for-business-and-cortex/main/PumpWorks%20610%20PWI%20pump_Maintenance.pdf

# Upload to S3 bucket (replace with your bucket name from CDK output)
aws s3 cp 1290IF_PumpHeadMaintenance_TN.pdf s3://snowflake-qbusiness-docs-ACCOUNT/
aws s3 cp "PumpWorks 610 PWI pump_Maintenance.pdf" s3://snowflake-qbusiness-docs-ACCOUNT/
```

### 6. Complete Snowflake Setup

The automation script now automatically:
- ✅ Uses correct Web Experience URL for OAuth redirect URI
- ✅ Creates Snowflake database, warehouse, and Cortex Search Service  
- ✅ Uploads and processes PDF documents
- ✅ Configures OAuth integration with proper redirect URI
- ✅ Retrieves OAuth credentials for Secrets Manager

**If you need to re-run Snowflake setup:**
```bash
python3 scripts/snowflake_automation.py
```

**Credentials:** `DEMODEVELOPER` / `9o0TLi2T!fQQAqJIC`

## Usage

Once deployed and configured:

1. Navigate to the Amazon Q Business application URL (from CDK output)
2. Select the "cortex-pump" plugin
3. Ask questions about pump maintenance:
   - "What is the part description for part number G4204-68741?"
   - "What are the pump head assembly parts?"
   - "What are the high level steps for Replacing the Heat Exchanger?"

## Customization

### Adding More Documents
- Upload additional PDFs to the S3 bucket
- Update the Snowflake tables to include new documents
- Refresh the Cortex Search Service

### Modifying Search Parameters
- Adjust chunk size and overlap in `SPLIT_TEXT_RECURSIVE_CHARACTER`
- Modify the Cortex Search Service configuration
- Update the OpenAPI schema for different query patterns

## Troubleshooting

### Common Issues

1. **Snowflake Connection Errors**
   - Verify account identifier format
   - Check user permissions (ACCOUNTADMIN role recommended)
   - Ensure Cortex Search is enabled in your Snowflake account

2. **Q Business Plugin Errors**
   - Verify OAuth configuration
   - Check IAM permissions
   - Ensure Identity Center instance ARN is correct

3. **Lambda Function Timeouts**
   - Increase timeout in CDK stack
   - Check Snowflake API rate limits
   - Verify network connectivity

### Logs and Monitoring

- **Lambda Logs**: CloudWatch Logs for Snowflake operations
- **Q Business Logs**: Check Q Business console for plugin errors
- **Snowflake Logs**: Query history in Snowflake console

## Cost Considerations

- **Amazon Q Business**: Per-user subscription costs
- **Lambda**: Pay-per-invocation (minimal for setup)
- **S3**: Storage costs for PDF documents
- **Snowflake**: Warehouse compute and storage costs
- **Secrets Manager**: Secret storage costs

## Security

- Credentials stored in AWS Secrets Manager
- OAuth 2.0 for secure API access
- IAM roles with least-privilege access
- Encrypted S3 bucket and Snowflake stage

## Cleanup

To remove all resources:

```bash
cdk destroy
```

Note: You may need to manually clean up Snowflake resources if the Lambda function fails during deletion.

## Contributing

This project automates the manual steps from the Snowflake quickstart. To contribute:

1. Test with different Snowflake account configurations
2. Add support for additional document types
3. Improve error handling and retry logic
4. Add CloudFormation outputs for easier integration

## References

- [Snowflake Quickstart Guide](https://quickstarts.snowflake.com/guide/getting_started_with_amazon_q_business%20and_cortex/index.html)
- [Amazon Q Business Documentation](https://docs.aws.amazon.com/amazonq/)
- [Snowflake Cortex Search](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
