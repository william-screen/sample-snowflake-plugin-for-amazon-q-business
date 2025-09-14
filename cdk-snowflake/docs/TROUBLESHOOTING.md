# Troubleshooting Guide

## Common Issues

### OAuth Authentication Errors

**Problem:** Plugin returns authentication errors when querying Snowflake.

**Solution:**
1. Verify OAuth secret format includes all required fields:
   ```json
   {
     "client_id": "base64-encoded-client-id",
     "client_secret": "base64-encoded-secret", 
     "redirect_uri": "https://your-qbusiness-url/oauth/callback"
   }
   ```
2. Ensure redirect URI matches Q Business web experience URL exactly
3. Verify OAuth integration exists and is active in Snowflake

### Plugin Not Found Errors

**Problem:** Users see "Amazon Q was not configured correctly" errors.

**Solution:**
1. Enable General Knowledge in Q Business:
   ```bash
   aws qbusiness update-chat-controls-configuration \
     --application-id YOUR_APPLICATION_ID \
     --response-scope EXTENDED_KNOWLEDGE_ENABLED
   ```
2. Verify plugin is in "READY" state in Q Business console
3. Check OpenAPI schema syntax is valid

### Cortex Search Errors

**Problem:** Search queries return no results or errors.

**Solution:**
1. Ensure Cortex Search is enabled in your Snowflake account
2. Verify documents were processed successfully:
   ```sql
   SELECT COUNT(*) FROM PUMP_CHUNKS;
   ```
3. Check that search service is "ACTIVE":
   ```sql
   SHOW CORTEX SEARCH SERVICES;
   ```

### CDK Deployment Failures

**Problem:** CDK deployment fails with permission errors.

**Solution:**
1. Verify AWS credentials have sufficient permissions
2. Check IAM Identity Center instance ARN is correct
3. Ensure target region supports all required services

## Logs and Monitoring

- **Q Business Logs:** Check Q Business console for plugin errors
- **Snowflake Logs:** Query history in Snowflake console  
- **CloudWatch Logs:** CDK deployment logs
- **CloudTrail:** API call logs for debugging

## Getting Help

If you continue to experience issues:

1. Check the [GitHub Issues](https://github.com/william-screen/sample-snowflake-plugin-for-amazon-q-business/issues)
2. Review AWS documentation for [Amazon Q Business](https://docs.aws.amazon.com/amazonq/)
3. Consult [Snowflake Cortex Search documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)
