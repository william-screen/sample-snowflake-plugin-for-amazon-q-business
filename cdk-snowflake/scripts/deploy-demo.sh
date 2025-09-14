#!/bin/bash

# Quick deployment for DEMODEVELOPER account

set -e

echo "🚀 Deploying Snowflake + Amazon Q Business RAG for DEMODEVELOPER..."

# Set your Snowflake configuration
export SNOWFLAKE_ACCOUNT="YVCDOIW-PFC31944"
export SNOWFLAKE_USER="DEMODEVELOPER"

# You need to set your Identity Center ARN
if [[ -z "$IDENTITY_CENTER_INSTANCE_ARN" ]]; then
    echo "❌ Please set your Identity Center ARN:"
    echo "   export IDENTITY_CENTER_INSTANCE_ARN='arn:aws:sso:::instance/ssoins-xxxxxxxxx'"
    echo ""
    echo "💡 To find your Identity Center ARN:"
    echo "   1. Go to AWS Console > IAM Identity Center"
    echo "   2. Copy the Instance ARN from the dashboard"
    exit 1
fi

echo "✅ Using Snowflake Account: $SNOWFLAKE_ACCOUNT"
echo "✅ Using Snowflake User: $SNOWFLAKE_USER"

# Install and deploy
npm install
npm run build
cdk bootstrap
cdk deploy --require-approval never

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. The Lambda function has generated SQL commands for your Snowflake account"
echo "2. Check CloudWatch Logs for the SnowflakeSetupFunction"
echo "3. Copy and execute the SQL commands in your Snowflake console"
echo "4. Upload sample PDFs to the S3 bucket (check CDK outputs)"
echo "5. Test your Q Business application!"
echo ""
echo "🔗 Snowflake Console: https://app.snowflake.com/YVCDOIW/PFC31944/"
