#!/bin/bash

# Snowflake Cortex Search + Amazon Q Business Integration Deployment Controller
# Orchestrates complete deployment: AWS infrastructure + Snowflake integration

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
AWS_REGION="${AWS_REGION:-us-east-1}"

echo -e "${BLUE}===============================================================================${NC}"
echo -e "${BLUE}                SNOWFLAKE CORTEX SEARCH + AMAZON Q BUSINESS${NC}"
echo -e "${BLUE}                           DEPLOYMENT CONTROLLER${NC}"
echo -e "${BLUE}===============================================================================${NC}"
echo ""
echo -e "Region: ${GREEN}${AWS_REGION}${NC}"
echo ""

# Validate prerequisites
echo -e "${YELLOW}VALIDATING PREREQUISITES${NC}"
echo -e "-------------------------"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}ERROR: AWS CLI not found. Please install AWS CLI.${NC}"
    exit 1
fi

# Check CDK
if ! command -v cdk &> /dev/null; then
    echo -e "${RED}ERROR: AWS CDK not found. Please install AWS CDK.${NC}"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found. Please install Python 3.8+.${NC}"
    exit 1
fi

# Check required environment variables
if [[ -z "${SNOWFLAKE_ACCOUNT:-}" ]]; then
    echo -e "${RED}ERROR: SNOWFLAKE_ACCOUNT environment variable not set.${NC}"
    exit 1
fi

if [[ -z "${SNOWFLAKE_USER:-}" ]]; then
    echo -e "${RED}ERROR: SNOWFLAKE_USER environment variable not set.${NC}"
    exit 1
fi

if [[ -z "${SNOWFLAKE_PASSWORD:-}" ]]; then
    echo -e "${RED}ERROR: SNOWFLAKE_PASSWORD environment variable not set.${NC}"
    exit 1
fi

if [[ -z "${SNOWFLAKE_ROLE:-}" ]]; then
    echo -e "${YELLOW}WARNING: SNOWFLAKE_ROLE not set, defaulting to ACCOUNTADMIN${NC}"
fi

if [[ -z "${IDENTITY_CENTER_INSTANCE_ARN:-}" ]]; then
    echo -e "${RED}ERROR: IDENTITY_CENTER_INSTANCE_ARN environment variable not set.${NC}"
    exit 1
fi

echo -e "${GREEN}SUCCESS: All prerequisites validated${NC}"
echo ""

# Step 1: Deploy AWS Infrastructure
echo -e "${BLUE}===============================================================================${NC}"
echo -e "${BLUE}                              STEP 1: AWS SETUP${NC}"
echo -e "${BLUE}===============================================================================${NC}"
echo ""

./scripts/setup_aws.sh

# Step 2: Configure Snowflake Integration
echo -e "${BLUE}===============================================================================${NC}"
echo -e "${BLUE}                          STEP 2: SNOWFLAKE SETUP${NC}"
echo -e "${BLUE}===============================================================================${NC}"
echo ""

./scripts/setup_snowflake.sh

# Final Summary
echo -e "${GREEN}===============================================================================${NC}"
echo -e "${GREEN}                           DEPLOYMENT COMPLETED${NC}"
echo -e "${GREEN}===============================================================================${NC}"
echo ""
echo -e "${YELLOW}NEXT STEPS${NC}"
echo -e "----------"
echo -e "1. Assign users to your Q Business application via IAM Identity Center"
echo -e ""
echo -e "2. Test access in a private browser window using your Web Experience URL"
echo -e ""
echo -e "3. Try sample queries to verify the Snowflake integration"
echo ""
