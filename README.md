# Snowflake Cortex Search + Amazon Q Business Integration

A production-ready solution that connects Amazon Q Business to Snowflake Cortex Search, enabling natural language queries over your Snowflake data through a conversational AI interface.

## 🚀 Overview

This project provides a complete automation framework for integrating Amazon Q Business with Snowflake Cortex Search. Users can ask natural language questions about documents stored in Snowflake and receive intelligent responses powered by Cortex Search's vector similarity capabilities.

## ✨ Key Features

- **🤖 Natural Language Queries**: Ask questions in plain English about your Snowflake data
- **📄 PDF Document Processing**: Automated parsing and chunking of PDF documents
- **🔍 Vector Search**: Powered by Snowflake Cortex Search for accurate semantic retrieval
- **🔐 Secure OAuth Integration**: End-to-end OAuth 2.0 authentication between Q Business and Snowflake
- **☁️ Serverless Architecture**: Fully automated AWS CDK deployment
- **📊 Production Ready**: Includes monitoring, error handling, and best practices

## 🏗️ Architecture

The solution consists of:

1. **Amazon Q Business Application** - Conversational AI interface
2. **Custom Q Business Plugin** - Connects to Snowflake Cortex Search REST API
3. **Snowflake Cortex Search Service** - Vector search over processed documents
4. **OAuth Integration** - Secure authentication between services
5. **Automated Setup** - Python script handles all Snowflake configuration

## 📋 Prerequisites

- **AWS Account** with Amazon Q Business access
- **Snowflake Account** with Cortex Search enabled
- **IAM Identity Center** instance configured
- **Node.js 18+** and **AWS CDK** installed
- **Python 3.8+** with required packages

## 🚀 Quick Start

### Step 1: Clone and Install Dependencies

```bash
git clone https://github.com/william-screen/sample-snowflake-plugin-for-amazon-q-business.git
cd sample-snowflake-plugin-for-amazon-q-business
npm install
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

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

### Step 3: Deploy AWS Infrastructure

```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy
```

### Step 4: Enable General Knowledge (CRITICAL)

After deployment, you **MUST** enable General Knowledge for the plugin to work:

```bash
# Get the Application ID from CDK output, then run:
aws qbusiness update-chat-controls-configuration \
  --application-id YOUR_APPLICATION_ID \
  --response-scope EXTENDED_KNOWLEDGE_ENABLED \
  --creator-mode-configuration '{"creatorModeControl": "ENABLED"}' \
  --region us-east-1
```

**⚠️ Without this step, users will get "Amazon Q was not configured correctly" errors.**

### Step 5: Run Snowflake Automation Script

Execute the Python automation script to set up Snowflake infrastructure:

```bash
python3 scripts/snowflake_automation.py
```

This script automatically:
- ✅ Creates Snowflake database, warehouse, and stage
- ✅ Downloads and uploads sample PDF documents
- ✅ Parses PDFs and creates text chunks using Cortex functions
- ✅ Creates Cortex Search Service
- ✅ Sets up OAuth integration with correct redirect URI
- ✅ Retrieves OAuth credentials for AWS Secrets Manager
- ✅ Validates the complete setup

### Step 6: Update AWS Secrets Manager

The automation script outputs OAuth credentials. Update your AWS secret:

```bash
# Use the credentials output from the Python script
aws secretsmanager update-secret \
  --secret-id YOUR_SECRET_ARN \
  --secret-string '{"client_id":"...","client_secret":"...","redirect_uri":"..."}'
```

## 🧪 Testing the Integration

Once deployed and configured:

1. Navigate to the Amazon Q Business application URL (from CDK output)
2. Select the "cortex-pump" plugin
3. Ask questions about pump maintenance:
   - *"What is the part description for part number G4204-68741?"*
   - *"What are the pump head assembly parts?"*
   - *"What are the high level steps for Replacing the Heat Exchanger?"*

## 📊 Sample Data

The solution includes sample pump maintenance PDF documents:
- **1290IF_PumpHeadMaintenance_TN.pdf** - Agilent pump maintenance guide
- **PumpWorks 610 PWI pump_Maintenance.pdf** - PumpWorks maintenance manual

These documents are automatically processed into **197 text chunks** for semantic search.

## 🔧 Customization

### Adding Your Own Documents

1. Upload PDFs to the S3 bucket created by CDK
2. Update the Snowflake automation script to process your documents
3. Refresh the Cortex Search Service

### Modifying Search Parameters

- Adjust chunk size and overlap in `SPLIT_TEXT_RECURSIVE_CHARACTER`
- Modify the Cortex Search Service configuration
- Update the OpenAPI schema for different query patterns

## 🔐 Security Features

- **OAuth 2.0 Authentication** between Q Business and Snowflake
- **AWS Secrets Manager** for credential storage
- **IAM Roles** with least-privilege access
- **Encrypted S3 Storage** for documents
- **VPC Endpoints** support (optional)

## 🛠️ Key Technical Details

### OAuth Configuration
The solution uses the correct OAuth secret format required by Q Business:
```json
{
  "client_id": "base64-encoded-client-id",
  "client_secret": "base64-encoded-secret", 
  "redirect_uri": "https://your-qbusiness-url/oauth/callback"
}
```

### REST API Endpoint
Uses the correct Snowflake Cortex Search REST API format:
```
/api/v2/databases/pump_db/schemas/public/cortex-search-services/PUMP_SEARCH_SERVICE:query
```

### PDF Processing
- PDFs uploaded with `AUTO_COMPRESS=FALSE` to maintain compatibility
- Text extraction using `SNOWFLAKE.CORTEX.PARSE_DOCUMENT`
- Chunking with `SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER`

## 🐛 Troubleshooting

### Common Issues

1. **OAuth Authentication Errors**
   - Verify secret format includes `client_id`, `client_secret`, and `redirect_uri`
   - Check that redirect URI matches Q Business web experience URL
   - Ensure OAuth integration exists in Snowflake

2. **Plugin Not Found Errors**
   - Confirm General Knowledge is enabled in Q Business
   - Verify plugin is in "READY" state
   - Check OpenAPI schema syntax

3. **Cortex Search Errors**
   - Ensure Cortex Search is enabled in your Snowflake account
   - Verify documents were processed successfully
   - Check that search service is "ACTIVE"

### Logs and Monitoring

- **Q Business Logs**: Check Q Business console for plugin errors
- **Snowflake Logs**: Query history in Snowflake console
- **CloudWatch Logs**: Lambda function logs (if using custom middleware)

## 💰 Cost Considerations

- **Amazon Q Business**: Per-user subscription costs
- **Snowflake**: Warehouse compute and storage costs
- **AWS Services**: S3 storage, Secrets Manager, minimal Lambda costs
- **Cortex Search**: Included with Snowflake Enterprise edition

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 References

- [Snowflake Cortex Search Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)
- [Amazon Q Business Documentation](https://docs.aws.amazon.com/amazonq/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Snowflake Quickstart Guide](https://quickstarts.snowflake.com/guide/getting_started_with_amazon_q_business%20and_cortex/index.html)

---

**Built with ❤️ for the AWS and Snowflake communities**
