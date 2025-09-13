import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export interface SnowflakeQBusinessRagAutomatedStackProps extends cdk.StackProps {
  snowflakeAccount: string;
  snowflakeUser: string;
  identityCenterInstanceArn: string;
}

export class SnowflakeQBusinessRagAutomatedStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: SnowflakeQBusinessRagAutomatedStackProps) {
    super(scope, id, props);

    // Step 1: Create S3 bucket for PDF documents
    const documentsBucket = new s3.Bucket(this, 'DocumentsBucket', {
      bucketName: `snowflake-qbusiness-docs-auto-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // Step 2: Create Secrets Manager secret for Snowflake OAuth
    const snowflakeOAuthSecret = new secretsmanager.Secret(this, 'SnowflakeOAuthSecret', {
      description: 'Snowflake OAuth credentials for Q Business plugin',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          client_id: 'placeholder-will-be-updated-by-script',
          redirect_uri: 'https://placeholder.qbusiness.amazonaws.com/oauth/callback',
        }),
        generateStringKey: 'client_secret',
        excludeCharacters: '"\\/',
      },
    });

    // Step 3: Create IAM role for Q Business
    const qBusinessRole = new iam.Role(this, 'QBusinessRole', {
      assumedBy: new iam.ServicePrincipal('qbusiness.amazonaws.com'),
      inlinePolicies: {
        QBusinessPolicy: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'qbusiness:*',
                'iam:PassRole',
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents',
              ],
              resources: ['*'],
            }),
          ],
        }),
      },
    });

    // Step 4: Create IAM role for Q Business plugin
    const pluginRole = new iam.Role(this, 'QBusinessPluginRole', {
      assumedBy: new iam.ServicePrincipal('qbusiness.amazonaws.com'),
      inlinePolicies: {
        AllowQBusinessToGetSecretValue: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              sid: 'AllowQBusinessToGetSecretValue',
              effect: iam.Effect.ALLOW,
              actions: [
                'secretsmanager:GetSecretValue',
              ],
              resources: [snowflakeOAuthSecret.secretArn],
            }),
          ],
        }),
      },
    });

    // Step 5: Create Q Business Application
    const qBusinessApp = new cdk.CfnResource(this, 'QBusinessApplication', {
      type: 'AWS::QBusiness::Application',
      properties: {
        DisplayName: 'Snowflake-Cortex-RAG-App',
        RoleArn: qBusinessRole.roleArn,
        IdentityCenterInstanceArn: props.identityCenterInstanceArn,
        Description: 'RAG application connecting Amazon Q Business to Snowflake Cortex Search',
      },
    });

    // Step 6: Create Q Business Plugin for Snowflake Cortex
    const cortexPlugin = new cdk.CfnResource(this, 'CortexPlugin', {
      type: 'AWS::QBusiness::Plugin',
      properties: {
        ApplicationId: qBusinessApp.ref,
        DisplayName: 'cortex-pump',
        Type: 'CUSTOM',
        AuthConfiguration: {
          OAuth2ClientCredentialConfiguration: {
            RoleArn: pluginRole.roleArn,
            SecretArn: snowflakeOAuthSecret.secretArn,
            AuthorizationUrl: `https://${props.snowflakeAccount}.snowflakecomputing.com/oauth/authorize`,
            TokenUrl: `https://${props.snowflakeAccount}.snowflakecomputing.com/oauth/token-request`,
          },
        },
        CustomPluginConfiguration: {
          Description: 'Submit a query to the Cortex Search service in order to answer questions specifically about Pumps or other mechanical parts or repair or maintenance information',
          ApiSchemaType: 'OPEN_API_V3',
          ApiSchema: {
            Payload: JSON.stringify({
              openapi: '3.0.0',
              info: {
                title: 'Cortex Search API',
                version: '2.0.0',
              },
              servers: [
                {
                  url: `https://${props.snowflakeAccount}.snowflakecomputing.com`,
                },
              ],
              paths: {
                '/api/v2/databases/pump_db/schemas/public/cortex-search-services/PUMP_SEARCH_SERVICE:query': {
                  post: {
                    parameters: [
                      {
                        in: 'header',
                        description: 'Customer Snowflake OAuth header',
                        name: 'X-Snowflake-Authorization-Token-Type',
                        schema: {
                          type: 'string',
                          enum: ['OAUTH'],
                        },
                        required: true,
                      },
                    ],
                    summary: 'Query the Cortex Search service',
                    description: 'Submit a query to the Cortex Search service in order to answer questions specifically about Pumps or other mechanical parts or repair or maintenance information',
                    requestBody: {
                      required: true,
                      content: {
                        'application/json': {
                          schema: {
                            $ref: '#/components/schemas/QueryRequest',
                          },
                        },
                      },
                    },
                    responses: {
                      '200': {
                        description: 'Successful response',
                        content: {
                          'application/json': {
                            schema: {
                              $ref: '#/components/schemas/QueryResponse',
                            },
                          },
                        },
                      },
                    },
                    security: [
                      {
                        oauth2: [],
                      },
                    ],
                  },
                },
              },
              components: {
                schemas: {
                  QueryRequest: {
                    type: 'object',
                    required: ['query'],
                    properties: {
                      query: {
                        type: 'string',
                        description: 'The search query',
                      },
                      limit: {
                        type: 'integer',
                        description: 'The maximum number of results to return',
                        example: 5,
                      },
                    },
                  },
                  QueryResponse: {
                    type: 'object',
                    description: 'Search results.',
                    properties: {
                      results: {
                        type: 'array',
                        description: 'List of result rows.',
                        items: {
                          type: 'object',
                          additionalProperties: true,
                          description: 'Map of column names to bytes.',
                        },
                      },
                      request_id: {
                        type: 'string',
                        description: 'ID of the request.',
                      },
                    },
                    required: ['results', 'request_id'],
                  },
                },
                securitySchemes: {
                  oauth2: {
                    type: 'oauth2',
                    flows: {
                      authorizationCode: {
                        authorizationUrl: `https://${props.snowflakeAccount}.snowflakecomputing.com/oauth/authorize`,
                        tokenUrl: `https://${props.snowflakeAccount}.snowflakecomputing.com/oauth/token-request`,
                        scopes: {
                          refresh_token: 'Refresh the OAuth token',
                          'session:role:PUBLIC': 'The Snowflake role for the integration',
                        },
                      },
                    },
                  },
                },
              },
            }),
          },
        },
      },
    });

    // Ensure the Q Business Application is fully created before the plugin
    cortexPlugin.addDependency(qBusinessApp);

    // Outputs
    new cdk.CfnOutput(this, 'SUCCESS', {
      value: '🎉 AUTOMATED DEPLOYMENT SUCCESSFUL!',
      description: 'Your automated Snowflake + Q Business infrastructure is ready!',
    });

    new cdk.CfnOutput(this, 'QBusinessApplicationId', {
      value: qBusinessApp.ref,
      description: 'Amazon Q Business Application ID',
    });

    new cdk.CfnOutput(this, 'QBusinessApplicationUrl', {
      value: `https://console.aws.amazon.com/q/business/applications/${qBusinessApp.ref}`,
      description: '🔗 Amazon Q Business Application Console URL',
    });

    new cdk.CfnOutput(this, 'CortexPluginId', {
      value: cortexPlugin.ref,
      description: 'Q Business Cortex Plugin ID',
    });

    new cdk.CfnOutput(this, 'DocumentsBucketName', {
      value: documentsBucket.bucketName,
      description: '📁 S3 bucket for PDF documents',
    });

    new cdk.CfnOutput(this, 'SnowflakeOAuthSecretArn', {
      value: snowflakeOAuthSecret.secretArn,
      description: 'Snowflake OAuth secret ARN (will be updated by automation script)',
    });

    new cdk.CfnOutput(this, 'SnowflakeAccount', {
      value: props.snowflakeAccount,
      description: 'Your Snowflake account identifier',
    });

    new cdk.CfnOutput(this, 'AutomationScript', {
      value: './automate-snowflake-setup.sh',
      description: '🚀 Run this script to complete Snowflake automation',
    });
  }
}
