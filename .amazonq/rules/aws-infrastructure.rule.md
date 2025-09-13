# AWS Infrastructure

## Purpose
This rule ensures proper AWS CDK infrastructure deployment and resource management for the multimedia RAG system.

## Instructions
- ALWAYS use AWS CDK v2 with TypeScript for all infrastructure code (ID: CDK_V2_TYPESCRIPT)
- MUST deploy all resources to us-west-2 region only (ID: US_WEST_2_REGION)
- ALWAYS create resources from scratch, never reference existing resources (ID: CREATE_FROM_SCRATCH)
- MUST use OpenSearch Serverless for vector storage, NOT regular OpenSearch (ID: OPENSEARCH_SERVERLESS)
- ALWAYS use amazon.titan-embed-text-v2:0 for embedding model (ID: TITAN_EMBEDDING_MODEL)
- MUST tag all resources with Project: multimedia-rag and Environment: ${stage} (ID: RESOURCE_TAGGING)
- ALWAYS implement least-privilege IAM policies with no wildcards (ID: LEAST_PRIVILEGE_IAM)
- MUST enable versioning on all S3 buckets (ID: S3_VERSIONING)
- ALWAYS use S3 managed encryption for buckets (ID: S3_ENCRYPTION)
- MUST create separate CDK stacks for different environments (dev, staging, prod) (ID: ENVIRONMENT_STACKS)

## Priority
Critical

## Error Handling
- If CDK deployment fails, check for proper AWS credentials and region configuration
- If resource creation fails due to limits, suggest alternative configurations
- If IAM permissions are insufficient, provide specific policy requirements
- If region-specific resources are unavailable, document the limitation and suggest alternatives
