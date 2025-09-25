#!/bin/bash

# AWS Infrastructure Setup Script
# Deploys CDK stack and AWS resources

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="${1:-SnowflakeQBusinessRagStack-${AWS_REGION//-/}}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo -e "${YELLOW}AWS INFRASTRUCTURE SETUP${NC}"
echo -e "-------------------------"
echo -e "Stack Name: ${GREEN}${STACK_NAME}${NC}"
echo -e "Region:     ${GREEN}${AWS_REGION}${NC}"
echo ""

# Install Python dependencies
echo -e "${YELLOW}INSTALLING PYTHON DEPENDENCIES${NC}"
echo -e "-------------------------------"
pip install -r requirements.txt

# Install CDK dependencies
echo -e "${YELLOW}INSTALLING CDK DEPENDENCIES${NC}"
echo -e "---------------------------"
npm install

# Bootstrap CDK (if needed)
echo -e "${YELLOW}BOOTSTRAPPING CDK ENVIRONMENT${NC}"
echo -e "------------------------------"
cdk bootstrap --region ${AWS_REGION}

# Deploy CDK stack
echo -e "${YELLOW}DEPLOYING CDK STACK${NC}"
echo -e "-------------------"
cdk deploy ${STACK_NAME} --region ${AWS_REGION} --require-approval never

echo ""
echo -e "${GREEN}SUCCESS: AWS infrastructure deployed${NC}"
echo ""
