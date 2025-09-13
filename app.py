#!/usr/bin/env python3
import os
import aws_cdk as cdk
from lib.snowflake_qbusiness_rag_stack import SnowflakeQBusinessRagStack

app = cdk.App()

# Get configuration from context or environment variables
snowflake_account = app.node.try_get_context("snowflakeAccount") or os.environ.get("SNOWFLAKE_ACCOUNT")
snowflake_user = app.node.try_get_context("snowflakeUser") or os.environ.get("SNOWFLAKE_USER")
identity_center_instance_arn = app.node.try_get_context("identityCenterInstanceArn") or os.environ.get("IDENTITY_CENTER_INSTANCE_ARN")

if not snowflake_account or not snowflake_user or not identity_center_instance_arn:
    raise ValueError("""
    Missing required configuration. Please provide:
    - snowflakeAccount: Your Snowflake account identifier
    - snowflakeUser: Your Snowflake username
    - identityCenterInstanceArn: Your AWS IAM Identity Center instance ARN
    """)

SnowflakeQBusinessRagStack(
    app,
    "SnowflakeQBusinessRagStack",
    snowflake_account=snowflake_account,
    snowflake_user=snowflake_user,
    identity_center_instance_arn=identity_center_instance_arn,
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION"),
    ),
    description="🚀 AUTOMATED Snowflake Cortex + Amazon Q Business RAG integration (Python)",
)

app.synth()
