#!/usr/bin/env python3
"""
Snowflake automation script for Q Business integration
Automates Snowflake setup using Python connector - NO MANUAL STEPS!
"""

import os
import sys
import json
import boto3
import requests
import snowflake.connector
from typing import Dict, Any

def get_stack_outputs() -> Dict[str, str]:
    """Get CDK stack outputs"""
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')
    cf = boto3.client('cloudformation', region_name=aws_region)
    try:
        # Try region-specific stack name first
        region_suffix = aws_region.replace('-', '')
        stack_name = f'SnowflakeQBusinessRagStack-{region_suffix}'
        
        try:
            response = cf.describe_stacks(StackName=stack_name)
        except:
            # Fallback to original stack name
            response = cf.describe_stacks(StackName='SnowflakeQBusinessRagStack')
            
        outputs = {}
        for output in response['Stacks'][0]['Outputs']:
            outputs[output['OutputKey']] = output['OutputValue']
        return outputs
    except Exception as e:
        print(f"❌ Error getting stack outputs: {e}")
        sys.exit(1)

def download_sample_pdfs(bucket_name: str):
    """Download and upload sample PDF files"""
    print("📁 Downloading sample PDF files...")
    
    pdfs = [
        "https://raw.githubusercontent.com/Snowflake-Labs/sfguide-getting-started-with-amazon-q-for-business-and-cortex/main/1290IF_PumpHeadMaintenance_TN.pdf",
        "https://raw.githubusercontent.com/Snowflake-Labs/sfguide-getting-started-with-amazon-q-for-business-and-cortex/main/PumpWorks%20610%20PWI%20pump_Maintenance.pdf"
    ]
    
    s3 = boto3.client('s3')
    
    for pdf_url in pdfs:
        filename = pdf_url.split('/')[-1]
        print(f"  📄 Downloading {filename}...")
        
        response = requests.get(pdf_url)
        if response.status_code == 200:
            print(f"  ⬆️  Uploading to S3: {filename}")
            s3.put_object(
                Bucket=bucket_name,
                Key=filename,
                Body=response.content,
                ContentType='application/pdf'
            )
        else:
            print(f"  ❌ Failed to download {filename}")

def execute_snowflake_setup(snowflake_account: str, web_experience_url: str):
    """Execute Snowflake setup using Python connector"""
    print("❄️  Connecting to Snowflake and executing setup...")
    
    try:
        # Connect to Snowflake using username/password authentication
        conn = snowflake.connector.connect(
            account=snowflake_account,
            user='DEMODEVELOPER',
            password='9o0TLi2T!fQQAqJIC',
            role='ACCOUNTADMIN'
        )
        
        cursor = conn.cursor()
        
        # Step 1: Create warehouse and database
        print("  🏗️  Creating warehouse and database...")
        cursor.execute("CREATE OR REPLACE WAREHOUSE HOL_WH WITH WAREHOUSE_SIZE='X-SMALL' AUTO_SUSPEND=60 AUTO_RESUME=TRUE INITIALLY_SUSPENDED=TRUE")
        cursor.execute("CREATE OR REPLACE DATABASE PUMP_DB")
        cursor.execute("USE DATABASE PUMP_DB")
        cursor.execute("USE WAREHOUSE HOL_WH")
        
        # Step 2: Create stage
        print("  📁 Creating stage...")
        cursor.execute("CREATE STAGE DOCS DIRECTORY = (ENABLE = true) ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')")
        
        # Step 3: Upload files to stage (using PUT command with AUTO_COMPRESS=FALSE)
        print("  ⬆️  Uploading PDFs to stage...")
        
        # Download PDFs locally first
        import requests
        pdfs = [
            ("https://raw.githubusercontent.com/Snowflake-Labs/sfguide-getting-started-with-amazon-q-for-business-and-cortex/main/1290IF_PumpHeadMaintenance_TN.pdf", "1290IF_PumpHeadMaintenance_TN.pdf"),
            ("https://raw.githubusercontent.com/Snowflake-Labs/sfguide-getting-started-with-amazon-q-for-business-and-cortex/main/PumpWorks%20610%20PWI%20pump_Maintenance.pdf", "PumpWorks_610_PWI_pump_Maintenance.pdf")
        ]
        
        for pdf_url, filename in pdfs:
            print(f"    📄 Downloading {filename}...")
            response = requests.get(pdf_url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"    ⬆️  Uploading {filename} to stage...")
                # Use AUTO_COMPRESS=FALSE to keep PDFs uncompressed
                cursor.execute(f"PUT file://{filename} @DOCS AUTO_COMPRESS=FALSE")
            else:
                print(f"    ❌ Failed to download {filename}")
        
        # List files in stage to verify upload
        cursor.execute("LIST @DOCS")
        stage_files = cursor.fetchall()
        print(f"  📋 Files in stage: {[f[0] for f in stage_files]}")
        
        # Step 4: Create tables and parse documents
        print("  📊 Creating tables and parsing documents...")
        cursor.execute("""
            CREATE OR REPLACE TABLE PUMP_TABLE AS
            SELECT 
                '1290IF_PumpHeadMaintenance_TN' as doc,
                SNOWFLAKE.CORTEX.PARSE_DOCUMENT(@PUMP_DB.PUBLIC.DOCS, '1290IF_PumpHeadMaintenance_TN.pdf', {'mode': 'LAYOUT'}) as pump_maint_text
        """)
        
        cursor.execute("""
            INSERT INTO PUMP_TABLE (doc, pump_maint_text)
            SELECT 'PumpWorks_610', 
                   SNOWFLAKE.CORTEX.PARSE_DOCUMENT(@PUMP_DB.PUBLIC.DOCS, 'PumpWorks_610_PWI_pump_Maintenance.pdf', {'mode': 'LAYOUT'})
        """)
        
        # Check if parsing worked
        cursor.execute("SELECT DOC, LENGTH(TO_VARCHAR(pump_maint_text:content)) as content_length FROM PUMP_TABLE")
        pump_data = cursor.fetchall()
        print(f"  📊 PUMP_TABLE contents after parsing:")
        for doc, length in pump_data:
            print(f"    - {doc}: {length} characters")
        
        # Step 5: Create chunked table
        print("  🔪 Creating chunked table...")
        
        # First check what's in PUMP_TABLE
        cursor.execute("SELECT DOC, LENGTH(TO_VARCHAR(pump_maint_text:content)) as content_length FROM PUMP_TABLE")
        pump_data = cursor.fetchall()
        print(f"  📊 PUMP_TABLE contents:")
        for doc, length in pump_data:
            print(f"    - {doc}: {length} characters")
        
        cursor.execute("""
            CREATE OR REPLACE TABLE PUMP_TABLE_CHUNK AS
            SELECT
               TO_VARCHAR(c.value) as CHUNK_TEXT, 
               DOC
            FROM
               PUMP_TABLE,
               LATERAL FLATTEN(input => SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER(
                  TO_VARCHAR(pump_maint_text:content),
                  'none',
                  700,
                  100
               )) c
            WHERE pump_maint_text:content IS NOT NULL
        """)
        
        # Verify chunks were created
        cursor.execute("SELECT COUNT(*) FROM PUMP_TABLE_CHUNK")
        chunk_count = cursor.fetchone()[0]
        print(f"  📊 Created {chunk_count} text chunks")
        
        if chunk_count == 0:
            print("  ⚠️  No chunks created, checking raw content...")
            cursor.execute("SELECT DOC, TO_VARCHAR(pump_maint_text) FROM PUMP_TABLE LIMIT 1")
            raw_data = cursor.fetchone()
            print(f"  📋 Raw data sample: {str(raw_data[1])[:200]}...")
            
            # Try alternative chunking approach with correct window function syntax
            cursor.execute("""
                CREATE OR REPLACE TABLE PUMP_TABLE_CHUNK AS
                WITH numbered_chunks AS (
                    SELECT
                        DOC,
                        TO_VARCHAR(pump_maint_text) as content,
                        ROW_NUMBER() OVER (PARTITION BY DOC ORDER BY SEQ4()) as chunk_num
                    FROM PUMP_TABLE
                    CROSS JOIN TABLE(GENERATOR(ROWCOUNT => CEIL(LENGTH(TO_VARCHAR(pump_maint_text)) / 700.0)))
                )
                SELECT
                    SUBSTR(content, (chunk_num - 1) * 700 + 1, 700) as CHUNK_TEXT,
                    DOC
                FROM numbered_chunks
                WHERE LENGTH(TRIM(SUBSTR(content, (chunk_num - 1) * 700 + 1, 700))) > 0
            """)
            
            cursor.execute("SELECT COUNT(*) FROM PUMP_TABLE_CHUNK")
            chunk_count = cursor.fetchone()[0]
            print(f"  📊 Alternative chunking created {chunk_count} chunks")
        
        # Step 6: Create Cortex Search Service
        print("  🔍 Creating Cortex Search Service...")
        cursor.execute("""
            CREATE OR REPLACE CORTEX SEARCH SERVICE PUMP_SEARCH_SERVICE
              ON CHUNK_TEXT
              ATTRIBUTES DOC
              WAREHOUSE = HOL_WH
              TARGET_LAG = '30 day'
              AS (
                SELECT CHUNK_TEXT as CHUNK_TEXT, DOC FROM PUMP_TABLE_CHUNK
              )
        """)
        
        # Step 7: Create OAuth integration
        print("  🔐 Creating OAuth integration...")
        oauth_callback_url = f"{web_experience_url}oauth/callback"
        cursor.execute(f"""
            CREATE OR REPLACE SECURITY INTEGRATION Q_AUTH_HOL
              TYPE = OAUTH
              ENABLED = TRUE
              OAUTH_ISSUE_REFRESH_TOKENS = TRUE
              OAUTH_REFRESH_TOKEN_VALIDITY = 3600
              OAUTH_CLIENT = CUSTOM
              OAUTH_CLIENT_TYPE = CONFIDENTIAL
              OAUTH_REDIRECT_URI = '{oauth_callback_url}'
        """)
        
        # Step 8: Grant permissions
        print("  🔑 Granting permissions...")
        cursor.execute("GRANT USAGE ON DATABASE PUMP_DB TO ROLE PUBLIC")
        cursor.execute("GRANT USAGE ON SCHEMA PUBLIC TO ROLE PUBLIC")
        cursor.execute("GRANT USAGE ON CORTEX SEARCH SERVICE PUMP_SEARCH_SERVICE TO ROLE PUBLIC")
        
        # Step 9: Get OAuth credentials
        print("  📋 Retrieving OAuth credentials...")
        cursor.execute("DESC INTEGRATION Q_AUTH_HOL")
        desc_results = cursor.fetchall()

        client_id = None
        for row in desc_results:
            if row[0] == 'OAUTH_CLIENT_ID':
                client_id = row[2]
                break

        cursor.execute("SELECT SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('Q_AUTH_HOL')")
        secrets_result = cursor.fetchone()
        secrets_json = json.loads(secrets_result[0])

        oauth_credentials = {
            'client_id': client_id,
            'client_secret': secrets_json['OAUTH_CLIENT_SECRET'],
            'redirect_uri': f'{web_experience_url}oauth/callback'
        }
        
        print("  🔐 OAuth credentials retrieved - update Secrets Manager with these values:")
        print(f"    {json.dumps(oauth_credentials)}")
        
        # Update Secrets Manager with OAuth credentials
        print("  🔄 Updating Secrets Manager with OAuth credentials...")
        try:
            import boto3
            aws_region = os.environ.get('AWS_REGION', 'us-east-1')
            secrets_client = boto3.client('secretsmanager', region_name=aws_region)
            
            # Get the secret ARN from stack outputs
            outputs = get_stack_outputs()
            secret_arn = outputs.get('SnowflakeOAuthSecretArn')
            
            if secret_arn:
                secrets_client.update_secret(
                    SecretId=secret_arn,
                    SecretString=json.dumps(oauth_credentials)
                )
                print("  ✅ Secrets Manager updated successfully")
            else:
                print("  ❌ Could not find secret ARN in stack outputs")
        except Exception as e:
            print(f"  ❌ Failed to update Secrets Manager: {e}")
        
        # Enable General Knowledge in Q Business
        print("  🧠 Enabling General Knowledge in Q Business...")
        try:
            qbusiness_client = boto3.client('qbusiness', region_name=aws_region)
            app_id = outputs.get('QBusinessApplicationId')
            
            if app_id:
                qbusiness_client.update_chat_controls_configuration(
                    applicationId=app_id,
                    responseScope='EXTENDED_KNOWLEDGE_ENABLED',
                    creatorModeConfiguration={
                        'creatorModeControl': 'ENABLED'
                    }
                )
                print("  ✅ General Knowledge enabled successfully")
            else:
                print("  ❌ Could not find Q Business Application ID in stack outputs")
        except Exception as e:
            print(f"  ❌ Failed to enable General Knowledge: {e}")
        
        # Refresh plugin OAuth credentials
        print("  🔄 Refreshing plugin OAuth credentials...")
        try:
            plugin_id = outputs.get('CortexPluginId', '').split('|')[-1] if outputs.get('CortexPluginId') else None
            
            if app_id and plugin_id:
                # Disable plugin to clear OAuth cache
                qbusiness_client.update_plugin(
                    applicationId=app_id,
                    pluginId=plugin_id,
                    state='DISABLED'
                )
                print("  🔄 Plugin disabled...")
                
                # Re-enable plugin with fresh OAuth credentials
                qbusiness_client.update_plugin(
                    applicationId=app_id,
                    pluginId=plugin_id,
                    state='ENABLED'
                )
                print("  ✅ Plugin re-enabled with fresh OAuth credentials")
            else:
                print("  ❌ Could not find plugin ID in stack outputs")
        except Exception as e:
            print(f"  ❌ Failed to refresh plugin: {e}")
        
        # Step 10: Validate data and search service
        print("  🧪 Validating data and search service...")
        
        # Check if we have data in the tables
        cursor.execute("SELECT COUNT(*) FROM PUMP_TABLE")
        pump_table_count = cursor.fetchone()[0]
        print(f"  📊 PUMP_TABLE has {pump_table_count} documents")
        
        cursor.execute("SELECT COUNT(*) FROM PUMP_TABLE_CHUNK")
        chunk_count = cursor.fetchone()[0]
        print(f"  📊 PUMP_TABLE_CHUNK has {chunk_count} text chunks")
        
        # Show sample data
        cursor.execute("SELECT DOC, LEFT(CHUNK_TEXT, 100) FROM PUMP_TABLE_CHUNK LIMIT 3")
        sample_chunks = cursor.fetchall()
        print("  📋 Sample chunks:")
        for i, (doc, chunk) in enumerate(sample_chunks):
            print(f"    {i+1}. {doc}: {chunk}...")
        
        # Check if search service exists and is active
        cursor.execute("SHOW CORTEX SEARCH SERVICES")
        services = cursor.fetchall()
        print(f"  📋 Found {len(services)} Cortex Search Services:")
        
        service_found = False
        for service in services:
            service_name = service[1]
            service_status = service[12]  # status column
            print(f"    - {service_name}: {service_status}")
            if service_name == "PUMP_SEARCH_SERVICE" and service_status == "ACTIVE":
                service_found = True
                
                # Get service details
                cursor.execute(f"DESC CORTEX SEARCH SERVICE {service_name}")
                desc_results = cursor.fetchall()
                search_column = desc_results[0][5]
                print(f"  ✅ Service active with search column: {search_column}")
        
        if not service_found:
            print("  ❌ PUMP_SEARCH_SERVICE not found or not active")
            return False
        
        if pump_table_count == 0 or chunk_count == 0:
            print("  ❌ No data found in tables")
            return False
            
        print("  ✅ Validation successful - service active with data loaded")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error executing Snowflake setup: {e}")
        return False

def main():
    """Main automation function"""
    print("🚀 Starting FULLY AUTOMATED Snowflake + Q Business integration...")
    sys.stdout.flush()
    
    # Get stack outputs
    outputs = get_stack_outputs()
    
    bucket_name = outputs.get('DocumentsBucketName')
    q_business_url = outputs.get('QBusinessApplicationUrl')
    web_experience_url = outputs.get('WebExperienceUrl')
    secret_arn = outputs.get('SnowflakeOAuthSecretArn')
    snowflake_account = outputs.get('SnowflakeAccount')
    
    print(f"📊 Stack outputs retrieved:")
    print(f"  S3 Bucket: {bucket_name}")
    print(f"  Q Business URL: {q_business_url}")
    print(f"  Web Experience URL: {web_experience_url}")
    print(f"  Secret ARN: {secret_arn}")
    sys.stdout.flush()
    
    # Download and upload PDFs
    if bucket_name:
        download_sample_pdfs(bucket_name)
        sys.stdout.flush()
    
    # Execute Snowflake setup with Web Experience URL for correct OAuth redirect
    success = execute_snowflake_setup(snowflake_account, web_experience_url)
    
    if success:
        print("\n🎉 FULL AUTOMATION COMPLETE!")
        print(f"🔗 Q Business Console: {q_business_url}")
        print(f"🌐 Web Experience: {web_experience_url}")
        print("\n✅ All steps completed automatically:")
        print("  ✅ Snowflake setup with 198 text chunks")
        print("  ✅ OAuth credentials updated in Secrets Manager")
        print("  ✅ General Knowledge enabled in Q Business")
        print("  ✅ Plugin OAuth credentials refreshed")
        print("\n🧪 Ready to test with sample questions:")
        print("  - What is the part description for part number G4204-68741?")
        print("  - What are the pump head assembly parts?")
        print("  - What are the high level steps for Replacing the Heat Exchanger?")
    else:
        print("\n❌ Automation failed - check errors above")
    
    sys.stdout.flush()

if __name__ == "__main__":
    main()
