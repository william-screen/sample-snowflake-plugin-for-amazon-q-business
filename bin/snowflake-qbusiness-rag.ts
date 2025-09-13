#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SnowflakeQBusinessRagAutomatedStack } from '../lib/snowflake-qbusiness-rag-automated';

const app = new cdk.App();

const snowflakeAccount = app.node.tryGetContext('snowflakeAccount') || process.env.SNOWFLAKE_ACCOUNT;
const snowflakeUser = app.node.tryGetContext('snowflakeUser') || process.env.SNOWFLAKE_USER;
const identityCenterInstanceArn = app.node.tryGetContext('identityCenterInstanceArn') || process.env.IDENTITY_CENTER_INSTANCE_ARN;

if (!snowflakeAccount || !snowflakeUser || !identityCenterInstanceArn) {
  throw new Error(`
    Missing required configuration. Please provide:
    - snowflakeAccount: Your Snowflake account identifier
    - snowflakeUser: Your Snowflake username
    - identityCenterInstanceArn: Your AWS IAM Identity Center instance ARN
  `);
}

new SnowflakeQBusinessRagAutomatedStack(app, 'SnowflakeQBusinessRagAutomatedStack', {
  snowflakeAccount,
  snowflakeUser,
  identityCenterInstanceArn,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  description: '🚀 AUTOMATED Snowflake Cortex + Amazon Q Business RAG integration',
});
