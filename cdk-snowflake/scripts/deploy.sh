#!/bin/bash

# Snowflake Cortex Search + Amazon Q Business Integration Deployment Script
# Production-ready deployment with proper error handling and validation

set -euo pipefail

# Store any existing environment variables
EXISTING_AWS_REGION="${AWS_REGION:-}"

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Restore environment variables if they were set before loading .env
if [ -n "$EXISTING_AWS_REGION" ]; then
    export AWS_REGION="$EXISTING_AWS_REGION"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="${1:-SnowflakeQBusinessRagStack-${AWS_REGION//-/}}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo -e "${BLUE}🚀 SNOWFLAKE CORTEX SEARCH + AMAZON Q BUSINESS DEPLOYMENT${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""
echo -e "📦 Stack Name: ${GREEN}${STACK_NAME}${NC}"
echo -e "🌍 Region: ${GREEN}${AWS_REGION}${NC}"
echo ""

# Validate prerequisites
echo -e "${YELLOW}🔍 Validating prerequisites...${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI.${NC}"
    exit 1
fi

# Check CDK
if ! command -v cdk &> /dev/null; then
    echo -e "${RED}❌ AWS CDK not found. Please install AWS CDK.${NC}"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+.${NC}"
    exit 1
fi

# Check required environment variables
if [[ -z "${SNOWFLAKE_ACCOUNT:-}" ]]; then
    echo -e "${RED}❌ SNOWFLAKE_ACCOUNT environment variable not set.${NC}"
    exit 1
fi

if [[ -z "${SNOWFLAKE_USER:-}" ]]; then
    echo -e "${RED}❌ SNOWFLAKE_USER environment variable not set.${NC}"
    exit 1
fi

if [[ -z "${IDENTITY_CENTER_INSTANCE_ARN:-}" ]]; then
    echo -e "${RED}❌ IDENTITY_CENTER_INSTANCE_ARN environment variable not set.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites validated${NC}"
echo ""

# Install Python dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Install CDK dependencies
echo -e "${YELLOW}📦 Installing CDK dependencies...${NC}"
npm install

# Bootstrap CDK (if needed)
echo -e "${YELLOW}🏗️ Bootstrapping CDK...${NC}"
cdk bootstrap --region ${AWS_REGION}

# Deploy CDK stack
echo -e "${YELLOW}🚀 Deploying CDK stack...${NC}"
cdk deploy ${STACK_NAME} --region ${AWS_REGION} --require-approval never

echo ""
echo -e "${GREEN}✅ CDK deployment completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "1. Run the Snowflake automation script: ${BLUE}python3 src/lambda/snowflake_automation.py${NC}"
echo -e "2. Enable General Knowledge in Q Business application"
echo -e "3. Test the integration with sample queries"
echo ""
