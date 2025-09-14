import aws_cdk as core
import aws_cdk.assertions as assertions
from lib.snowflake_qbusiness_rag_stack import SnowflakeQBusinessRagStack


def test_stack_creation():
    """Test that the CDK stack can be created without errors."""
    app = core.App()
    stack = SnowflakeQBusinessRagStack(
        app,
        "TestStack",
        snowflake_account="test-account",
        snowflake_user="test-user",
        identity_center_instance_arn="arn:aws:sso:::instance/ssoins-test",
    )
    
    template = assertions.Template.from_stack(stack)
    
    # Verify Q Business application is created
    template.has_resource_properties("AWS::QBusiness::Application", {
        "DisplayName": "Snowflake Cortex Search RAG"
    })
    
    # Verify S3 bucket is created
    template.has_resource("AWS::S3::Bucket", {})
    
    # Verify Secrets Manager secret is created
    template.has_resource("AWS::SecretsManager::Secret", {})
