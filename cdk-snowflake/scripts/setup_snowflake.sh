#!/bin/bash

# Snowflake Integration Setup Script
# Configures Snowflake Cortex Search and Q Business integration

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}SNOWFLAKE INTEGRATION SETUP${NC}"
echo -e "----------------------------"

# Run Snowflake automation
python3 src/automation/snowflake_automation.py

echo ""
echo -e "${GREEN}SUCCESS: Snowflake integration configured${NC}"
echo ""
