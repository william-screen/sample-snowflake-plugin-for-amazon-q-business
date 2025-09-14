# Replace the AuthConfiguration in your CDK stack with this:
"AuthConfiguration": {
    "OAuth2ClientCredentialConfiguration": {
        "RoleArn": plugin_role.role_arn,
        "SecretArn": snowflake_oauth_secret.secret_arn,
    },
},

# The OAuth URLs should be defined in the OpenAPI schema components.securitySchemes
# NOT in the AuthConfiguration section
