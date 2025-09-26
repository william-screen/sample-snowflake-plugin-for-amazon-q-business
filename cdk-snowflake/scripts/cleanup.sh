#!/bin/bash

# Cleanup script for Snowflake Q Business RAG Stack
set -e

echo "🧹 Starting cleanup of Snowflake Q Business RAG Stack..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please ensure you're in the cdk-snowflake directory."
    exit 1
fi

# Load environment variables (excluding comments)
echo "📋 Loading environment variables..."
export $(grep -v '^#' .env | xargs)

# Verify required variables are set
if [ -z "$SNOWFLAKE_ACCOUNT" ] || [ -z "$SNOWFLAKE_USER" ] || [ -z "$IDENTITY_CENTER_INSTANCE_ARN" ]; then
    echo "❌ Error: Missing required environment variables in .env file"
    echo "Required: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, IDENTITY_CENTER_INSTANCE_ARN"
    exit 1
fi

echo "🚀 Destroying CDK stack..."
cdk destroy --force

echo "✅ Cleanup completed successfully!"
echo "📝 Note: Snowflake resources (database, warehouse) remain and need manual cleanup if desired."
