-- Snowflake Setup SQL for DEMODEVELOPER account (YVCDOIW-PFC31944)
-- Execute these commands in your Snowflake console after CDK deployment

-- Step 1: Set role and create warehouse
USE ROLE ACCOUNTADMIN;
CREATE OR REPLACE WAREHOUSE HOL_WH WITH 
    WAREHOUSE_SIZE='X-SMALL' 
    AUTO_SUSPEND=60 
    AUTO_RESUME=TRUE 
    INITIALLY_SUSPENDED=TRUE;

-- Step 2: Create database and stage
CREATE OR REPLACE DATABASE PUMP_DB;
USE DATABASE PUMP_DB;
USE WAREHOUSE HOL_WH;

CREATE STAGE DOCS 
    DIRECTORY = (ENABLE = true) 
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- Step 3: Create table for parsed documents
-- Note: You'll need to upload the PDF files to the DOCS stage first
CREATE OR REPLACE TABLE PUMP_TABLE AS
SELECT 
    '1290IF_PumpHeadMaintenance_TN' as doc,
    SNOWFLAKE.CORTEX.PARSE_DOCUMENT(@PUMP_DB.PUBLIC.DOCS, '1290IF_PumpHeadMaintenance_TN.pdf', {'mode': 'LAYOUT'}) as pump_maint_text;

-- Add second document
INSERT INTO PUMP_TABLE (doc, pump_maint_text)
SELECT 'PumpWorks 610', 
       SNOWFLAKE.CORTEX.PARSE_DOCUMENT(@PUMP_DB.PUBLIC.DOCS, 'PumpWorks 610 PWI pump_Maintenance.pdf', {'mode': 'LAYOUT'});

-- Step 4: Create chunked table for search
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
   )) c;

-- Verify chunked data
SELECT COUNT(*) as chunk_count, DOC FROM PUMP_TABLE_CHUNK GROUP BY DOC;

-- Step 5: Create Cortex Search Service
CREATE OR REPLACE CORTEX SEARCH SERVICE PUMP_SEARCH_SERVICE
  ON CHUNK_TEXT
  ATTRIBUTES DOC
  WAREHOUSE = HOL_WH
  TARGET_LAG = '30 day'
  AS (
    SELECT CHUNK_TEXT as CHUNK_TEXT, DOC FROM PUMP_TABLE_CHUNK
  );

-- Step 6: Create OAuth integration for Q Business
-- Note: Replace <Q_BUSINESS_URL> with your actual Q Business application URL from CDK output
CREATE OR REPLACE SECURITY INTEGRATION Q_AUTH_HOL
  TYPE = OAUTH
  ENABLED = TRUE
  OAUTH_ISSUE_REFRESH_TOKENS = TRUE
  OAUTH_REFRESH_TOKEN_VALIDITY = 3600
  OAUTH_CLIENT = CUSTOM
  OAUTH_CLIENT_TYPE = CONFIDENTIAL
  OAUTH_REDIRECT_URI = '<Q_BUSINESS_URL>/oauth/callback';

-- Step 7: Grant permissions
GRANT USAGE ON DATABASE PUMP_DB TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA PUBLIC TO ROLE PUBLIC;
GRANT USAGE ON CORTEX SEARCH SERVICE PUMP_SEARCH_SERVICE TO ROLE PUBLIC;

-- Step 8: Get OAuth credentials for Q Business plugin
DESC INTEGRATION Q_AUTH_HOL;
SELECT SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('Q_AUTH_HOL');

-- Test the search service
SELECT * FROM TABLE(PUMP_DB.PUBLIC.PUMP_SEARCH_SERVICE.SEARCH('pump maintenance', 5));
