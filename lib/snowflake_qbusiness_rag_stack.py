import json
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    CfnOutput,
    CfnResource,
    RemovalPolicy,
    Duration,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_s3 as s3,
)
from constructs import Construct


class SnowflakeQBusinessRagStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        snowflake_account: str,
        snowflake_user: str,
        identity_center_instance_arn: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Step 1: Create S3 bucket for PDF documents
        documents_bucket = s3.Bucket(
            self,
            "DocumentsBucket",
            bucket_name=f"snowflake-qbusiness-docs-auto-{self.region}-{self.account}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Step 2: Create Secrets Manager secret for Snowflake OAuth
        snowflake_oauth_secret = secretsmanager.Secret(
            self,
            "SnowflakeOAuthSecret",
            description="Snowflake OAuth credentials for Q Business plugin",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({
                    "client_id": "placeholder-will-be-updated-by-script",
                    "redirect_uri": "https://placeholder.qbusiness.amazonaws.com/oauth/callback"
                }),
                generate_string_key="client_secret",
                exclude_characters='"\\/',
            ),
        )

        # Step 3: Create IAM role for Q Business
        qbusiness_role = iam.Role(
            self,
            "QBusinessRole",
            assumed_by=iam.ServicePrincipal("qbusiness.amazonaws.com"),
            inline_policies={
                "QBusinessPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "qbusiness:*",
                                "iam:PassRole",
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=["*"],
                        ),
                    ]
                )
            },
        )

        # Step 4: Create IAM role for Q Business plugin
        plugin_role = iam.Role(
            self,
            "QBusinessPluginRole",
            assumed_by=iam.ServicePrincipal("qbusiness.amazonaws.com"),
            inline_policies={
                "AllowQBusinessToGetSecretValue": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            sid="AllowQBusinessToGetSecretValue",
                            effect=iam.Effect.ALLOW,
                            actions=["secretsmanager:GetSecretValue"],
                            resources=[snowflake_oauth_secret.secret_arn],
                        ),
                    ]
                )
            },
        )

        # Step 4.5: Create IAM role for Q Business Web Experience (BEFORE app creation)
        web_experience_role = iam.Role(
            self,
            "QBusinessWebExperienceRole",
            assumed_by=iam.ServicePrincipal("application.qbusiness.amazonaws.com"),
        )

        # Step 5: Create Q Business Application
        qbusiness_app = CfnResource(
            self,
            "QBusinessApplication",
            type="AWS::QBusiness::Application",
            properties={
                "DisplayName": "Snowflake-Cortex-RAG-App",
                "RoleArn": qbusiness_role.role_arn,
                "IdentityCenterInstanceArn": identity_center_instance_arn,
                "Description": "RAG application connecting Amazon Q Business to Snowflake Cortex Search",
            },
        )

        # Step 5.5: Add policies to Web Experience role (after app creation for ARN reference)
        web_experience_role.add_to_policy(
            iam.PolicyStatement(
                sid="QBusinessConversationPermissions",
                effect=iam.Effect.ALLOW,
                actions=[
                    "qbusiness:Chat",
                    "qbusiness:ChatSync",
                    "qbusiness:ListMessages",
                    "qbusiness:ListConversations",
                    "qbusiness:DeleteConversation",
                    "qbusiness:PutFeedback",
                    "qbusiness:GetWebExperience",
                    "qbusiness:GetApplication",
                    "qbusiness:ListPlugins",
                    "qbusiness:GetChatControlsConfiguration",
                    "qbusiness:ListRetrievers",
                    "qbusiness:ListPluginActions",
                    "qbusiness:ListAttachments",
                    "qbusiness:DeleteAttachment",
                    "qbusiness:GetMedia",
                    "qbusiness:GetDocumentContent",
                    "qbusiness:CreateConversation",
                    "qbusiness:GetConversation",
                    "qbusiness:UpdateConversation",
                ],
                resources=[
                    f"arn:aws:qbusiness:{self.region}:{self.account}:application/{qbusiness_app.ref}",
                ],
            )
        )
        
        web_experience_role.add_to_policy(
            iam.PolicyStatement(
                sid="QBusinessPluginDiscoveryPermissions",
                effect=iam.Effect.ALLOW,
                actions=[
                    "qbusiness:ListPluginTypeMetadata",
                    "qbusiness:ListPluginTypeActions",
                ],
                resources=["*"],
            )
        )
        
        web_experience_role.add_to_policy(
            iam.PolicyStatement(
                sid="QBusinessRetrieverPermission",
                effect=iam.Effect.ALLOW,
                actions=[
                    "qbusiness:GetRetriever",
                ],
                resources=[
                    f"arn:aws:qbusiness:{self.region}:{self.account}:application/{qbusiness_app.ref}",
                    f"arn:aws:qbusiness:{self.region}:{self.account}:application/{qbusiness_app.ref}/retriever/*",
                ],
            )
        )
        
        web_experience_role.add_to_policy(
            iam.PolicyStatement(
                sid="QBusinessAutoSubscriptionPermission",
                effect=iam.Effect.ALLOW,
                actions=[
                    "user-subscriptions:CreateClaim",
                ],
                resources=["*"],
                conditions={
                    "Bool": {
                        "user-subscriptions:CreateForSelf": "true"
                    },
                    "StringEquals": {
                        "aws:CalledViaLast": "qbusiness.amazonaws.com"
                    }
                }
            )
        )
        
        # Add trust policy conditions for the web experience role
        web_experience_role.assume_role_policy.add_statements(
            iam.PolicyStatement(
                sid="QBusinessTrustPolicy",
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("application.qbusiness.amazonaws.com")],
                actions=["sts:AssumeRole", "sts:SetContext"],
                conditions={
                    "StringEquals": {
                        "aws:SourceAccount": self.account
                    },
                    "ArnEquals": {
                        "aws:SourceArn": f"arn:aws:qbusiness:{self.region}:{self.account}:application/{qbusiness_app.ref}"
                    }
                }
            )
        )

        # Step 6: Create Q Business Plugin for Snowflake Cortex
        cortex_plugin = CfnResource(
            self,
            "CortexPlugin",
            type="AWS::QBusiness::Plugin",
            properties={
                "ApplicationId": qbusiness_app.ref,
                "DisplayName": "cortex-pump",
                "Type": "CUSTOM",
                "AuthConfiguration": {
                    "OAuth2ClientCredentialConfiguration": {
                        "RoleArn": plugin_role.role_arn,
                        "SecretArn": snowflake_oauth_secret.secret_arn,
                    },
                },
                "CustomPluginConfiguration": {
                    "Description": "Submit a query to the Cortex Search service in order to answer questions specifically about Pumps or other mechanical parts or repair or maintenance information",
                    "ApiSchemaType": "OPEN_API_V3",
                    "ApiSchema": {
                        "Payload": f"""openapi: 3.0.0
info:
  title: Cortex Search API
  version: 2.0.0
servers:
  - url: https://{snowflake_account}.snowflakecomputing.com
paths:
  /api/v2/databases/pump_db/schemas/public/cortex-search-services/PUMP_SEARCH_SERVICE:query:
    post:
      parameters:
      - in: header
        description: Customer Snowflake OAuth header
        name: X-Snowflake-Authorization-Token-Type
        schema:
          type: string
          enum: ["OAUTH"]
        required: true
      summary: Query the Cortex Search service
      description: Submit a query to the Cortex Search service in order to answer questions specifically about Pumps or other mechanical parts or repair or maintenance information
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QueryRequest'
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QueryResponse'
      security:
        - oauth2: []
components:
  schemas:
    QueryRequest:
      type: object
      required:
        - query
      properties:
        query:
          type: string
          description: The search query
        limit:
          type: integer
          description: The maximum number of results to return
          example: 5
    QueryResponse:
      type: object
      description: Search results.
      properties:
        results:
          type: array
          description: List of result rows.
          items:
            type: object
            additionalProperties: true
            description: Map of column names to bytes.
        request_id:
          type: string
          description: ID of the request.
      required:
      - results
      - request_id
  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://{snowflake_account}.snowflakecomputing.com/oauth/authorize
          tokenUrl: https://{snowflake_account}.snowflakecomputing.com/oauth/token-request
          scopes:
            refresh_token: Refresh the OAuth token
            session:role:PUBLIC: The Snowflake role for the integration"""
                    },
                },
            },
        )

        # Ensure the Q Business Application is fully created before the plugin
        cortex_plugin.add_dependency(qbusiness_app)

        # Step 7: Create Q Business Web Experience
        web_experience = CfnResource(
            self,
            "QBusinessWebExperience",
            type="AWS::QBusiness::WebExperience",
            properties={
                "ApplicationId": qbusiness_app.ref,
                "RoleArn": web_experience_role.role_arn,
                "Title": "Snowflake Cortex RAG Assistant",
                "Subtitle": "Ask questions about pump maintenance and mechanical parts",
                "WelcomeMessage": "Welcome! I can help you find information about pump maintenance, mechanical parts, and repair procedures using Snowflake Cortex Search.",
                "SamplePromptsControlMode": "ENABLED",
            },
        )

        # Ensure the Web Experience is created after the application
        web_experience.add_dependency(qbusiness_app)

        # Outputs
        CfnOutput(
            self,
            "SUCCESS",
            value="🎉 AUTOMATED DEPLOYMENT SUCCESSFUL!",
            description="Your automated Snowflake + Q Business infrastructure is ready!",
        )

        CfnOutput(
            self,
            "QBusinessApplicationId",
            value=qbusiness_app.ref,
            description="Amazon Q Business Application ID",
        )

        CfnOutput(
            self,
            "QBusinessApplicationUrl",
            value=f"https://console.aws.amazon.com/q/business/applications/{qbusiness_app.ref}",
            description="🔗 Amazon Q Business Application Console URL",
        )

        CfnOutput(
            self,
            "CortexPluginId",
            value=cortex_plugin.ref,
            description="Q Business Cortex Plugin ID",
        )

        CfnOutput(
            self,
            "WebExperienceId",
            value=web_experience.ref,
            description="🌐 Q Business Web Experience ID",
        )

        CfnOutput(
            self,
            "WebExperienceUrl",
            value=web_experience.get_att("DefaultEndpoint").to_string(),
            description="🚀 Q Business Web Experience URL - Access your chat interface here!",
        )

        CfnOutput(
            self,
            "DocumentsBucketName",
            value=documents_bucket.bucket_name,
            description="📁 S3 bucket for PDF documents",
        )

        CfnOutput(
            self,
            "SnowflakeOAuthSecretArn",
            value=snowflake_oauth_secret.secret_arn,
            description="Snowflake OAuth secret ARN (will be updated by automation script)",
        )

        CfnOutput(
            self,
            "SnowflakeAccount",
            value=snowflake_account,
            description="Your Snowflake account identifier",
        )

        CfnOutput(
            self,
            "AutomationScript",
            value="./automate-snowflake-setup.sh",
            description="🚀 Run this script to complete Snowflake automation",
        )
