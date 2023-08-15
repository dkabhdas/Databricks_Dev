# Bring your Own Bucket (BYOB)

!!! warning "BE AWARE"
    * **YOU ARE RESPONSIBLE FOR THE DATA IN YOUR ACCOUNTS, WHAT IS BEING INGESTED, & SHARED**
    * **When creating the S3 bucket: DO NOT MAKE IT PUBLIC**
    * **Be aware of data regulations: PII, GDPR, etc.**

!!! info "**Information**"
    * This is intended to be used after completing the [Onboarding Process](https://baseplate.legogroup.io/docs/default/component/self-service-core-data-platform/registration)
    * This process is intended for individual product teams **(do not share your account with other product teams)**
    * This can be used for DEV/QA/PROD - or any other environment you deem necessary for your usage purposes


## **Purpose**

* Demonstrate how to ingest data using an AWS S3 bucket from an AWS Account your team owns

## **Prerequisite**
* Complete the [Onboarding Process](https://baseplate.legogroup.io/docs/default/component/self-service-core-data-platform/registration)

## **Create AWS Account**

!!! info "**Note**"
    If you already have an account this step may not be necessary

    Skip to [Create AWS Bucket](#create-aws-bucket)

??? summary "**Create AWS Account - Procedure**"
    1. Locate your product in [BasePlate](https://baseplate.legogroup.io/products?filters%5Bkind%5D=product){:target="_blank"}
    ![BasePlate Product Search](../img/create_aws_account_baseplate_product_search.png)
    2. Click "Cloud" Tab
    ![BasePlate Product CloudTab](../img/create_aws_account_baseplate_cloud_tab_select.png)
    3. Click "Create"
    ![Baseplate AWS Create](../img/create_aws_account_baseplate_create_aws_account.png)
    4. Fill in all Required information including: Account Owner, Technical Owners and Click "Next"
    5. Fill in cost center and budgets threshholds and click "Next"
    6. Fill in account justifications and contact information and click "Submit"

## **Create AWS Bucket**
!!! warning "PUBLIC SETTING"
    * **DO NOT DISABLE THE "BLOCK ALL PUBLIC ACCESS" SETTING**
    * Disabling this will make data in that bucket accessible to the world

??? summary "**Create Bucket - AWS UI Procedure**"
    1. Open [Azure Apps](https://myapps.microsoft.com/){:target="_blank"}
    2. Use the search to find the desired AWS Account and select it
    3. Login to the appropriate AWS Account
    4. Navigate to S3
    5. Click "Create Bucket"
    6. Provide a meaningful "Bucket Name" - ex. lego-s3-example (Must be unique across AWS)
    7. Set "Region" to "EU (Ireland) eu-west-1"
    8. "Enable" Bucket Versioning
    9. Leave all other settings at default
    10. Click "Create Bucket"

??? summary "**Create Bucket - AWS CLI Procedure**"
    1. Follow this guide to authenticate with SSO to AWS via CLI
       1. https://gitlab.legogroup.io/dataoffice/public/dope-user-support/-/blob/main/docs/saml2aws.md
    2. Once authenticated do the following:
       1. Decide on a bucket name (must be a unique name as AWS allows only one bucket with that name to exist across all of S3)
    !!! info "**Code**"
        **REPLACE:**

        **BUCKET_NAME** with a bucket name of your choosing

        **ROLE_FROM_IDPACCOUNT_COLUMN** with the desired AWS account you would like the bucket to be in
    
        <pre><code>\# Create bucket
        aws s3 mb s3://**BUCKET_NAME** --region eu-west-1 --profile **ROLE_FROM_IDPACCOUNT_COLUMN**    
        \# Enable Bucket Versioning
        aws s3api put-bucket-versioning --bucket **BUCKET_NAME** --versioning-configuration Status=Enabled --profile **ROLE_FROM_IDPACCOUNT_COLUMN** 
        </code></pre>

## **Create Role**

??? summary "**Create Role - AWS UI Procedure**"
    1. Open [Azure Apps](https://myapps.microsoft.com/){:target="_blank"}
    2. Use the search to find the desired AWS Account and select it
    3. Login to the appropriate AWS Account
    4. Navigate to IAM
    5. Click "Roles" in left menu bar
    6. Click "Create role"
    7. Select "Custom trust policy"
    8. Add the following into the space provided
        
        !!! info "Code"
            * DO NOT CHANGE THIS POLICY
            * A second principal will be added in a later step
            <pre><code>{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": [
                                "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL"
                            ]
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "StringEquals": {
                                "sts:ExternalId": "b4b72722-686c-4cd0-8369-fe76b7d632f9"
                            }
                        }
                    }
                ]
            }
            </code></pre>
    9. Click "Next"
    10. Click "Create Policy" (will open page in new tab)
    11. Click "Next"
    12. Role Name: SSCDP-**CHANGE_ME_TO_SOMETHING_MEANINGFUL**
    13. Click "Create Role"
    14. Search for the role you just created
    15. Open it
    16. Click "Trust relationships"
    17. Copy the ARN for the Role
    18. Update the trust policy principal
        
        !!! info "**Code**"
            **REPLACE:**

            **SELF_ROLE_ARN** with the copied role ARN
    
            <pre><code>        "Principal": {
                        "AWS": [
                            "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL",
                            "**SELF_ROLE_ARN**"
                        ]
                    },
            </code></pre>
    19.  Click "Update Policy"
    20.  Click "Permissions"
    21.  Click "Add permissions" --> "Create inline policy"
    22.  Switch from **Visual** to **JSON**
    23.  When the **Specify permissions** screen opens switch from **Visual** to **JSON**
    24.  Copy in the following code block

        !!! info  "**Code**"
            **REPLACE:**

            **BUCKET_ARN** with the ARN of the bucket created (ex. arn:aws:s3:::lego-example-bucket)

            **SELF_ROLE_ARN** with the ARN of the ROLE you just created
            <pre><code>{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:DeleteObject",
                            "s3:ListBucket",
                            "s3:GetBucketLocation",
                            "s3:GetLifecycleConfiguration",
                            "s3:PutLifecycleConfiguration"
                        ],
                        "Resource": [
                            "**BUCKET_ARN**/\*",
                            "**BUCKET_ARN**"
                        ],
                        "Effect": "Allow"
                    },
                    {
                        "Action": [
                            "sts:AssumeRole"
                        ],
                        "Resource": [
                            "**SELF_ROLE_ARN**"
                        ],
                        "Effect": "Allow"
                    }
                ]
            }
            </code></pre>
    25. Click **Next**
    26. Provide a policy name
    27. Click **Create Policy**

??? summary "**Create Role - AWS CLI Procdure** (WIP)"

## **Databricks: Create Storage Credentials & Location**

!!! warning "THIS REQUIRES ADMIN PRIVILEGES IN DATABRICKS"
!!! info "You should already have a **CATALOG** created as part of the Onboarding Process"

??? summary "Create Storage Credentials & Location - NON ADMINS"
    1. Fill in this [**request form**](https://legogroup.sharepoint.com/sites/dataplatform-ingestion/SitePages/Request-Storage-Credential-and-External-Location.aspx?OR=Teams-HL&CT=1691758509297&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIyOC8yMzA3MDMwNzM0NiIsIkhhc0ZlZGVyYXRlZFVzZXIiOmZhbHNlfQ%3D%3D){:target="_blank"} with the following information:
       1. The Role ARN from [Create Role](#create-role)
       2. The S3 bucket name from [Create AWS Bucket](#create-aws-bucket)
       3. The Product ID/Name (ID preferred, but can also use the name)
       4. The environment (Dev/QA/Prod, or some other not listed)$$
    2. We will contact you within 2-3 days to establish the configuration

??? summary "Create Storage Credentials & Location Procedure - ADMINS ONLY"
    1. Login to desired Databricks environment **(Links open in new tab)**
       1. [SSC-DEV Databricks](https://lego-ssc-dev.cloud.databricks.com/){:target="_blank"}
       2. [SSC-QA Databricks](https://lego-ssc-qa.cloud.databricks.com/){:target="_blank"}
       3. [SSC-PROD Databricks](https://lego-ssc-prod.cloud.databricks.com/){:target="_blank"}
    2. In left menu bar click **Data**
    3. Add Storage Credentials

        !!! note "**Skip to step 4 if you already have a storage credential saved**"
        1. Click **External Data** (toward bottom left)
        2. Select **Storage Credentials**
        3. Click **Create Credential**
        4. Provide a name for the storage credential
        5. Copy in the **SELF_ROLE_ARN** from previous steps
        6. **Optional**: Select read only if you only want the credential to be able to read from the volume and not write
    4. Add External Locations
       1. Click **External Locations**
       2. Click **Create location**
       3. Select **Manual**
       4. Click **Next**
       5. Provide a name for the external location in Databricks **(usually based on bucket name including the environment it's in)**
       6. Provide the S3 url (ex. s3://this-is-my-bucket-url-name)
       7. Select the storage credential created in **Step 3**
       8. **Optional**: Select read only if you want the storage location to be able to read only from Databricks
       9. Click **Create**
       10. Click **Test Connection** to ensure the credential has desired access

## **Add Data**
??? summary "Add Data - Procedure"
    1. Ensure there is data in the S3 bucket first (you can drag and drop a structured file into the bucket through the UI - CSV, JSON, AVRO, PARQUET)
    2. In Databricks select **Data** from menu on left
    3. Click **+Add** button (toward top right of page) --> **Add data**
    4. Select **Amazon S3** (will be under **Native Integrations**)
    5. From the drop down select the appropriate previously created **External location**
    6. Select the file(s) or folder(s) you would like to ingest
    7. Click **Preview table**
    8. In the first dropdown select the appropriate product **Catalog**
    9. In the second dropdown select the appropriate **Schema** for the data (or create a new one)
    10. In the third field provide a name for the table of data
    11. In **advanced attributes** select the appropriate data type (you can also have Databricks auto detect the file type)
        1. Close out of the window (hit **X** in top right of box)
    12. Click **Create table**
    13. Data is ingested - review and repeat as needed

## **Review Data**

!!! info "**NOTE:**"
    Ingested data can be reviewed via **Notebook**
    
    -or-

    via **Data** section by navigating to the:

    CATALOG --> SCHEMA --> TABLE created in the previous steps

!!! info "**EXAMPLE Notebook**"
    **REPLACE:**

    **CATALOG_NAME** with the Catalog in Databricks

    **SCHEMA_NAME** with the level below Catalog

    **TABLE_NAME** replace the table with the desired table to search
    <pre><code>%sql
    USE CATALOG \`**CATALOG_NAME**\`;
    USE SCHEMA \`**SCHEMA_NAME**\`;
    SELECT * FROM \`**TABLE_NAME**\`
    </code></pre>
