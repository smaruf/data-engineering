# Security Best Practices for Data Engineering

## Table of Contents
1. [Authentication and Authorization](#authentication-and-authorization)
2. [Data Encryption](#data-encryption)
3. [Network Security](#network-security)
4. [Secrets Management](#secrets-management)
5. [Compliance and Governance](#compliance-and-governance)

---

## Authentication and Authorization

### Azure Active Directory Integration

```python
# Use Azure AD for all authentication (no passwords in code!)

# 1. Service Principal (for applications)
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"  # From Key Vault, never hardcoded
)

# 2. Managed Identity (recommended for Azure resources)
from azure.identity import DefaultAzureCredential

# Automatically uses managed identity if available
credential = DefaultAzureCredential()

# 3. User-assigned Managed Identity
from azure.identity import ManagedIdentityCredential

credential = ManagedIdentityCredential(client_id="user-assigned-identity-id")
```

### Role-Based Access Control (RBAC)

```bash
# Principle of Least Privilege: Grant minimum necessary permissions

# Storage Account - Read Only
az role assignment create \
    --assignee <service-principal-id> \
    --role "Storage Blob Data Reader" \
    --scope "/subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account>"

# Storage Account - Read/Write
az role assignment create \
    --assignee <service-principal-id> \
    --role "Storage Blob Data Contributor" \
    --scope "/subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account>"

# Synapse - SQL Admin
az role assignment create \
    --assignee <user-or-group-id> \
    --role "Synapse SQL Administrator" \
    --scope "/subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.Synapse/workspaces/<workspace>"

# Use groups for easier management
az ad group create --display-name "DataEngineers" --mail-nickname "DataEngineers"
az ad group member add --group "DataEngineers" --member-id <user-id>
az role assignment create --assignee <group-id> --role "Contributor" --scope <resource-scope>
```

### Access Control Lists (ACLs) for ADLS Gen2

```bash
# Set ACL on directory
az storage fs access set \
    --path "bronze/" \
    --account-name <storage-account> \
    --acl "user:<user-id>:r-x,group:<group-id>:rwx,other::---"

# Set default ACL (inherited by new files)
az storage fs access set \
    --path "bronze/" \
    --account-name <storage-account> \
    --acl "default:user:<user-id>:r-x,default:group:<group-id>:rwx"

# Recursive ACL update
az storage fs access update-recursive \
    --path "bronze/" \
    --account-name <storage-account> \
    --acl "user:<user-id>:rwx"
```

---

## Data Encryption

### Encryption at Rest

```python
# All Azure storage is encrypted at rest by default (Microsoft-managed keys)

# Customer-Managed Keys (CMK) for additional control
az storage account update \
    --name <storage-account> \
    --resource-group <rg> \
    --encryption-key-source Microsoft.Keyvault \
    --encryption-key-vault <key-vault-uri> \
    --encryption-key-name <key-name>

# SQL Database Transparent Data Encryption (TDE)
# Enabled by default on Azure SQL
ALTER DATABASE MyDatabase SET ENCRYPTION ON;

# Check encryption status
SELECT 
    db_name(database_id) AS DatabaseName,
    encryption_state,
    encryption_state_desc = CASE encryption_state
        WHEN 0 THEN 'No database encryption key present, no encryption'
        WHEN 1 THEN 'Unencrypted'
        WHEN 2 THEN 'Encryption in progress'
        WHEN 3 THEN 'Encrypted'
        WHEN 4 THEN 'Key change in progress'
        WHEN 5 THEN 'Decryption in progress'
    END
FROM sys.dm_database_encryption_keys;
```

### Encryption in Transit

```python
# Always use HTTPS/TLS

# Azure Storage (enforce HTTPS)
az storage account update \
    --name <storage-account> \
    --resource-group <rg> \
    --https-only true

# SQL Database (enforce SSL)
from sqlalchemy import create_engine

connection_string = (
    "mssql+pyodbc://user:password@server.database.windows.net/database"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&Encrypt=yes"  # Force encryption
    "&TrustServerCertificate=no"  # Validate certificate
)
engine = create_engine(connection_string)

# Databricks (HTTPS enforced by default)
spark.conf.set("spark.hadoop.fs.azure.ssl.channel.mode", "Default_JSSE")
```

### Column-Level Encryption (Always Encrypted)

```sql
-- Azure SQL Database Always Encrypted
-- Encrypt sensitive columns

-- 1. Create Column Master Key (in Azure Key Vault)
CREATE COLUMN MASTER KEY MyCMK
WITH (
    KEY_STORE_PROVIDER_NAME = 'AZURE_KEY_VAULT',
    KEY_PATH = 'https://myvault.vault.azure.net/keys/mykey/version'
);

-- 2. Create Column Encryption Key
CREATE COLUMN ENCRYPTION KEY MyCEK
WITH VALUES (
    COLUMN_MASTER_KEY = MyCMK,
    ALGORITHM = 'RSA_OAEP',
    ENCRYPTED_VALUE = 0x...
);

-- 3. Create table with encrypted columns
CREATE TABLE Employees (
    EmployeeID INT PRIMARY KEY,
    Name VARCHAR(100),
    SSN VARCHAR(11) ENCRYPTED WITH (
        COLUMN_ENCRYPTION_KEY = MyCEK,
        ENCRYPTION_TYPE = Deterministic,  -- For equality comparison
        ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256'
    ),
    Salary DECIMAL(10,2) ENCRYPTED WITH (
        COLUMN_ENCRYPTION_KEY = MyCEK,
        ENCRYPTION_TYPE = Randomized,  -- More secure, no comparison
        ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256'
    )
);
```

---

## Network Security

### Virtual Network Service Endpoints

```bash
# Restrict storage access to specific VNets

# 1. Enable service endpoint on subnet
az network vnet subnet update \
    --resource-group <rg> \
    --vnet-name <vnet> \
    --name <subnet> \
    --service-endpoints Microsoft.Storage

# 2. Configure storage firewall
az storage account update \
    --name <storage-account> \
    --resource-group <rg> \
    --default-action Deny

# 3. Add VNet rule
az storage account network-rule add \
    --account-name <storage-account> \
    --resource-group <rg> \
    --vnet-name <vnet> \
    --subnet <subnet>
```

### Private Endpoints

```bash
# Private endpoint for Azure SQL
az network private-endpoint create \
    --name sql-private-endpoint \
    --resource-group <rg> \
    --vnet-name <vnet> \
    --subnet <subnet> \
    --private-connection-resource-id <sql-server-id> \
    --group-id sqlServer \
    --connection-name sqlConnection

# Private DNS zone
az network private-dns zone create \
    --resource-group <rg> \
    --name privatelink.database.windows.net

# Link to VNet
az network private-dns link vnet create \
    --resource-group <rg> \
    --zone-name privatelink.database.windows.net \
    --name DNSLink \
    --virtual-network <vnet> \
    --registration-enabled false
```

### Firewall Rules

```python
# IP whitelisting for Azure services

# SQL Database firewall
az sql server firewall-rule create \
    --resource-group <rg> \
    --server <server-name> \
    --name AllowMyIP \
    --start-ip-address 203.0.113.1 \
    --end-ip-address 203.0.113.255

# Storage firewall
az storage account network-rule add \
    --account-name <storage-account> \
    --resource-group <rg> \
    --ip-address 203.0.113.1

# Allow Azure services
az storage account update \
    --name <storage-account> \
    --resource-group <rg> \
    --bypass AzureServices
```

---

## Secrets Management

### Azure Key Vault

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# Store secrets in Key Vault (never in code!)
key_vault_url = "https://myvault.vault.azure.net"
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Set secret
secret_client.set_secret("database-password", "SuperSecretPassword123!")

# Get secret
secret = secret_client.get_secret("database-password")
password = secret.value

# Use in connection string
connection_string = f"Server=myserver;Database=mydb;User=admin;Password={password}"

# ❌ NEVER do this:
# password = "SuperSecretPassword123!"  # Hardcoded secret!
```

### Databricks Secrets

```bash
# Create secret scope (backed by Key Vault)
databricks secrets create-scope --scope my-scope --backend-type AZURE_KEYVAULT \
    --resource-id /subscriptions/.../vaults/myvault \
    --dns-name https://myvault.vault.azure.net

# Or Databricks-backed scope
databricks secrets create-scope --scope my-scope

# Store secret
databricks secrets put --scope my-scope --key storage-account-key

# Use in notebook
storage_key = dbutils.secrets.get(scope="my-scope", key="storage-account-key")

spark.conf.set(
    f"fs.azure.account.key.{storage_account}.dfs.core.windows.net",
    storage_key
)
```

### Environment Variables (for development only)

```python
import os
from dotenv import load_dotenv

# Load from .env file (never commit .env to git!)
load_dotenv()

DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
STORAGE_KEY = os.getenv("STORAGE_KEY")

# .env file (add to .gitignore!)
# DATABASE_PASSWORD=dev_password
# STORAGE_KEY=dev_storage_key

# .gitignore
# .env
# *.key
# *.pem
# config/secrets.json
```

---

## Row-Level and Column-Level Security

### Row-Level Security (RLS)

```sql
-- Restrict users to see only their own data

-- 1. Create security predicate function
CREATE FUNCTION dbo.fn_SecurityPredicate(@UserId AS NVARCHAR(256))
    RETURNS TABLE
WITH SCHEMABINDING
AS
    RETURN SELECT 1 AS fn_SecurityPredicate_result
    WHERE @UserId = USER_NAME() OR IS_MEMBER('DataAdmins') = 1;

-- 2. Create security policy
CREATE SECURITY POLICY dbo.UserDataFilter
ADD FILTER PREDICATE dbo.fn_SecurityPredicate(UserId)
ON dbo.Orders
WITH (STATE = ON);

-- 3. Test
-- User 'john@company.com' queries:
SELECT * FROM Orders;
-- Automatically filtered to show only records where UserId = 'john@company.com'

-- Multi-tenant example
CREATE FUNCTION dbo.fn_TenantFilter(@TenantId AS INT)
    RETURNS TABLE
WITH SCHEMABINDING
AS
    RETURN SELECT 1 AS fn_TenantFilter_result
    WHERE @TenantId = CAST(SESSION_CONTEXT(N'TenantId') AS INT)
        OR IS_MEMBER('SystemAdmins') = 1;

-- Set session context in application
EXEC sp_set_session_context @key = N'TenantId', @value = 123;
```

### Column-Level Security

```sql
-- Grant permissions on specific columns only

-- Sensitive columns: SSN, Salary
CREATE TABLE Employees (
    EmployeeID INT,
    Name VARCHAR(100),
    Department VARCHAR(50),
    SSN VARCHAR(11),
    Salary DECIMAL(10,2)
);

-- Grant access to non-sensitive columns
GRANT SELECT ON Employees(EmployeeID, Name, Department) TO RegularUsers;

-- HR can see all columns
GRANT SELECT ON Employees TO HRRole;

-- Test as RegularUser
SELECT * FROM Employees;
-- ERROR: Cannot access SSN and Salary columns

SELECT EmployeeID, Name, Department FROM Employees;
-- SUCCESS
```

### Dynamic Data Masking

```sql
-- Mask sensitive data based on user permissions

CREATE TABLE Customers (
    CustomerID INT,
    Name VARCHAR(100),
    Email VARCHAR(100) MASKED WITH (FUNCTION = 'email()'),
    Phone VARCHAR(20) MASKED WITH (FUNCTION = 'partial(1,"XXX-XXX-",4)'),
    CreditCard VARCHAR(20) MASKED WITH (FUNCTION = 'partial(0,"XXXX-XXXX-XXXX-",4)'),
    SSN VARCHAR(11) MASKED WITH (FUNCTION = 'default()')
);

-- Regular user sees masked data:
-- Email: jXXX@XXXX.com
-- Phone: 5XXX-XXX-1234
-- CreditCard: XXXX-XXXX-XXXX-5678
-- SSN: XXXX

-- Grant unmask permission
GRANT UNMASK TO DataAnalysts;

-- User in DataAnalysts group sees unmasked data
```

---

## Data Classification and Sensitivity Labels

### Microsoft Information Protection

```python
# Label data based on sensitivity
# - Public: No restrictions
# - Internal: Company employees only
# - Confidential: Specific teams only
# - Restricted: Highest security

# SQL Database automatic classification
# Azure automatically discovers and recommends classifications

# View classification recommendations
SELECT 
    schema_name,
    table_name,
    column_name,
    information_type,
    sensitivity_label,
    rank
FROM sys.sensitivity_classifications;

# Apply classification
ADD SENSITIVITY CLASSIFICATION TO
    dbo.Customers.SSN
WITH (
    LABEL = 'Highly Confidential',
    INFORMATION_TYPE = 'National Identification Number'
);

# Purview for data catalog and lineage
# - Automatic scanning and classification
# - Data lineage tracking
# - Compliance reporting
```

---

## Audit and Monitoring

### Azure SQL Auditing

```sql
-- Enable auditing at server level
-- Logs to storage account or Log Analytics

-- View audit logs
SELECT 
    event_time,
    action_name,
    succeeded,
    server_principal_name,
    database_name,
    statement
FROM sys.fn_get_audit_file(
    'https://mystorageaccount.blob.core.windows.net/sqldbauditlogs/**',
    DEFAULT,
    DEFAULT
)
WHERE database_name = 'MyDatabase'
    AND event_time > DATEADD(day, -7, GETUTCDATE())
ORDER BY event_time DESC;
```

### Azure Monitor and Log Analytics

```python
# Send logs to Log Analytics workspace

# Query audit logs with KQL
audit_query = """
AzureDiagnostics
| where ResourceType == "SQLSERVERS"
| where Category == "SQLSecurityAuditEvents"
| where TimeGenerated > ago(24h)
| where action_name_s == "DATABASE ROLE MEMBER CHANGE"
| project TimeGenerated, server_principal_name_s, statement_s
"""

# Set up alerts for suspicious activity
alert_rule = """
AzureDiagnostics
| where ResourceType == "STORAGEACCOUNTS"
| where Category == "StorageRead"
| where CallerIpAddress !in ("203.0.113.0/24")  # Whitelist
| summarize FailedAttempts = count() by CallerIpAddress, bin(TimeGenerated, 5m)
| where FailedAttempts > 100  # Threshold
"""
```

---

## Compliance Frameworks

### GDPR Compliance

```python
# 1. Data Minimization
# - Collect only necessary data
# - Delete data when no longer needed

# 2. Right to be Forgotten
def delete_user_data(user_id):
    """Delete all user data (GDPR compliance)"""
    
    # Soft delete with retention period
    spark.sql(f"""
        UPDATE users 
        SET deleted = true, deletion_date = current_timestamp()
        WHERE user_id = '{user_id}'
    """)
    
    # Schedule hard delete after 30 days
    spark.sql(f"""
        DELETE FROM users 
        WHERE user_id = '{user_id}' 
        AND deletion_date < date_sub(current_date(), 30)
    """)

# 3. Data Portability
def export_user_data(user_id, output_path):
    """Export user data (GDPR compliance)"""
    user_data = spark.sql(f"""
        SELECT * FROM users WHERE user_id = '{user_id}'
    """)
    
    user_data.write.format("json").save(output_path)

# 4. Data Residency
# - Store EU data in EU regions only
# - Use ADLS Gen2 with EU data centers
# - Configure Synapse in EU region
```

### HIPAA Compliance

```python
# Healthcare data requires:
# 1. Encryption at rest and in transit (covered above)
# 2. Access controls and audit logs
# 3. Business Associate Agreement (BAA) with Azure
# 4. No shared resources (dedicated infrastructure)

# Enable HIPAA features
az sql server create \
    --name myserver \
    --resource-group myrg \
    --location eastus \
    --admin-user myadmin \
    --admin-password mypassword \
    --minimal-tls-version 1.2 \
    --public-network-access Disabled  # Private endpoint only
```

---

## Security Checklist

### Authentication & Authorization
- [ ] Use Azure AD for all authentication
- [ ] Implement RBAC with least privilege
- [ ] Use managed identities (no passwords in code)
- [ ] Configure ACLs for ADLS Gen2
- [ ] Enable MFA for user accounts

### Encryption
- [ ] Verify encryption at rest (TDE, SSE)
- [ ] Enforce HTTPS/TLS for all connections
- [ ] Use customer-managed keys for sensitive data
- [ ] Implement Always Encrypted for PII columns
- [ ] Encrypt backups

### Network Security
- [ ] Configure virtual network service endpoints
- [ ] Use private endpoints for Azure services
- [ ] Implement firewall rules (IP whitelisting)
- [ ] Disable public access where possible
- [ ] Use VPN or ExpressRoute for on-premises connectivity

### Secrets Management
- [ ] Store all secrets in Azure Key Vault
- [ ] Never commit secrets to Git
- [ ] Rotate secrets regularly
- [ ] Use separate Key Vaults for dev/prod
- [ ] Monitor secret access logs

### Data Protection
- [ ] Implement row-level security
- [ ] Apply column-level security
- [ ] Use dynamic data masking
- [ ] Classify data by sensitivity
- [ ] Enable auditing and logging

### Compliance
- [ ] Document data retention policies
- [ ] Implement GDPR requirements (if applicable)
- [ ] Enable audit logs for all services
- [ ] Set up alerts for security events
- [ ] Regular security assessments
- [ ] Backup and disaster recovery plans

---

## Incident Response Plan

### Security Incident Checklist

1. **Detection**
   - Monitor Azure Security Center alerts
   - Review Log Analytics for anomalies
   - Check failed authentication attempts

2. **Containment**
   - Revoke compromised credentials immediately
   - Block suspicious IP addresses
   - Disable affected accounts

3. **Investigation**
   - Review audit logs
   - Identify affected data/systems
   - Determine root cause

4. **Remediation**
   - Patch vulnerabilities
   - Rotate all secrets
   - Update security policies

5. **Recovery**
   - Restore from clean backups if needed
   - Verify system integrity
   - Resume normal operations

6. **Lessons Learned**
   - Document incident
   - Update security procedures
   - Conduct training

---

**Remember**: Security is not a one-time setup, but an ongoing process. Regular reviews and updates are essential.
