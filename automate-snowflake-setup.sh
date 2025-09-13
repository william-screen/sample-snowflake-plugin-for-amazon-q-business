#!/bin/bash

# FULLY AUTOMATED Snowflake + Q Business RAG integration
# This script now automates EVERYTHING including Snowflake SQL execution!

set -e

echo "🚀 Starting FULLY AUTOMATED Snowflake + Q Business integration..."

# Configuration
export SNOWFLAKE_ACCOUNT="YVCDOIW-PFC31944"
export SNOWFLAKE_USER="DEMODEVELOPER"
export IDENTITY_CENTER_INSTANCE_ARN="arn:aws:sso:::instance/ssoins-72231bbbfb28de47"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}📋 Step $1: $2${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Install Python dependencies
print_step 1 "Installing Python dependencies"
# pip3 install snowflake-connector-python boto3 requests  # Already installed

# Step 2: Deploy CDK infrastructure
print_step 2 "Deploying CDK infrastructure"
npm run build
cdk deploy --require-approval never

if [ $? -eq 0 ]; then
    print_success "CDK deployment completed successfully!"
else
    print_error "CDK deployment failed!"
    exit 1
fi

# Step 3: Download PDFs locally for Snowflake upload
print_step 3 "Downloading PDFs locally"
curl -o "1290IF_PumpHeadMaintenance_TN.pdf" "https://raw.githubusercontent.com/Snowflake-Labs/sfguide-getting-started-with-amazon-q-for-business-and-cortex/main/1290IF_PumpHeadMaintenance_TN.pdf"
curl -o "PumpWorks 610 PWI pump_Maintenance.pdf" "https://raw.githubusercontent.com/Snowflake-Labs/sfguide-getting-started-with-amazon-q-for-business-and-cortex/main/PumpWorks%20610%20PWI%20pump_Maintenance.pdf"

# Step 4: Run FULL Python automation (including Snowflake SQL execution)
print_step 4 "Running FULL Snowflake automation with Python connector"
cd scripts
python3 snowflake_automation.py
cd ..

print_success "Full automation completed!"

echo ""
echo "🎉 FULLY AUTOMATED DEPLOYMENT COMPLETE!"
echo ""
echo "📋 What was automated:"
echo "  ✅ AWS infrastructure deployment"
echo "  ✅ Q Business application + plugin creation"
echo "  ✅ Snowflake database, warehouse, stage creation"
echo "  ✅ PDF upload to Snowflake stage"
echo "  ✅ Document parsing and chunking"
echo "  ✅ Cortex Search Service creation"
echo "  ✅ OAuth integration setup"
echo "  ✅ Permissions configuration"
echo "  ✅ Search service testing"
echo ""
echo "📋 Only 2 manual steps remaining:"
echo "  1. 🔐 Update AWS Secrets Manager with OAuth credentials (shown in output above)"
echo "  2. 🧪 Test the cortex-pump plugin in Q Business"
echo ""
echo "🚀 Your FULLY AUTOMATED Snowflake + Amazon Q Business RAG system is ready!"
