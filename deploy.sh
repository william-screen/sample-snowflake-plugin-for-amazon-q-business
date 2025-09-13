#!/bin/bash

# Deployment script for Snowflake + Amazon Q Business RAG integration

set -e

echo "🚀 Starting Snowflake + Amazon Q Business RAG deployment..."

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK is required but not installed. Run: npm install -g aws-cdk"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is required but not installed."
    exit 1
fi

# Check required environment variables
if [[ -z "$SNOWFLAKE_ACCOUNT" ]]; then
    echo "❌ SNOWFLAKE_ACCOUNT environment variable is required"
    echo "   Set it with: export SNOWFLAKE_ACCOUNT='your-account-identifier'"
    exit 1
fi

if [[ -z "$SNOWFLAKE_USER" ]]; then
    echo "❌ SNOWFLAKE_USER environment variable is required"
    echo "   Set it with: export SNOWFLAKE_USER='your-snowflake-username'"
    exit 1
fi

if [[ -z "$IDENTITY_CENTER_INSTANCE_ARN" ]]; then
    echo "❌ IDENTITY_CENTER_INSTANCE_ARN environment variable is required"
    echo "   Set it with: export IDENTITY_CENTER_INSTANCE_ARN='arn:aws:sso:::instance/ssoins-xxxxxxxxx'"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the project
echo "🔨 Building TypeScript..."
npm run build

# Bootstrap CDK (if needed)
echo "🏗️  Bootstrapping CDK..."
cdk bootstrap

# Deploy the stack
echo "🚀 Deploying CDK stack..."
cdk deploy --require-approval never

echo "✅ Deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Check the CDK outputs for your Q Business Application ID and S3 bucket name"
echo "2. Download sample PDFs:"
echo "   curl -O https://raw.githubusercontent.com/Snowflake-Labs/sfguide-getting-started-with-amazon-q-for-business-and-cortex/main/1290IF_PumpHeadMaintenance_TN.pdf"
echo "   curl -O 'https://raw.githubusercontent.com/Snowflake-Labs/sfguide-getting-started-with-amazon-q-for-business-and-cortex/main/PumpWorks%20610%20PWI%20pump_Maintenance.pdf'"
echo "3. Upload PDFs to your S3 bucket"
echo "4. Check Lambda function logs for Snowflake SQL commands"
echo "5. Execute the SQL commands in your Snowflake console"
echo "6. Test the Q Business application with pump maintenance questions"
echo ""
echo "🎉 Your Snowflake + Amazon Q Business RAG system is ready!"
