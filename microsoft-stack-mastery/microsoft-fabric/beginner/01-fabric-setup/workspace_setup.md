# Microsoft Fabric Workspace Setup Guide

This guide walks you through creating and configuring a Microsoft Fabric workspace using both the Azure portal and programmatically with Python.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Create Workspace via Azure Portal](#create-workspace-via-azure-portal)
3. [Create Workspace Programmatically](#create-workspace-programmatically)
4. [Configure Workspace Settings](#configure-workspace-settings)
5. [Assign Users and Permissions](#assign-users-and-permissions)
6. [Best Practices](#best-practices)

## Prerequisites

Before creating a workspace, ensure you have:

- **Azure Subscription**: Active Azure subscription
- **Fabric Capacity**: F2 or higher (or Trial capacity)
- **Permissions**: Fabric Administrator or Capacity Administrator role
- **License**: Fabric license or Power BI Premium capacity

## Create Workspace via Azure Portal

### Step 1: Access Microsoft Fabric

1. Navigate to [Microsoft Fabric Portal](https://app.fabric.microsoft.com/)
2. Sign in with your organizational account
3. Ensure you have the appropriate license and permissions

### Step 2: Create a New Workspace

1. Click on **Workspaces** in the left navigation pane
2. Click **+ New workspace**
3. Configure the workspace:

   ```
   Name: my-fabric-workspace
   Description: Workspace for data engineering and analytics
   Advanced settings:
     - License mode: Fabric capacity (or Trial)
     - Capacity: Select your Fabric capacity
   ```

4. Click **Apply** to create the workspace

### Step 3: Verify Workspace Creation

1. The workspace should now appear in your workspace list
2. Click on the workspace to open it
3. You should see an empty workspace with options to create items

## Create Workspace Programmatically

### Using Microsoft Fabric REST API

```python
import requests
from azure.identity import DefaultAzureCredential
import os

def create_fabric_workspace(workspace_name, capacity_id=None):
    """
    Create a Microsoft Fabric workspace programmatically.
    
    Args:
        workspace_name (str): Name of the workspace to create
        capacity_id (str, optional): Fabric capacity ID to assign
    
    Returns:
        dict: Workspace details
    """
    # Get access token
    credential = DefaultAzureCredential()
    token = credential.get_token("https://api.fabric.microsoft.com/.default")
    
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json"
    }
    
    # Prepare request body
    body = {
        "displayName": workspace_name,
        "description": f"Workspace for {workspace_name}"
    }
    
    if capacity_id:
        body["capacityId"] = capacity_id
    
    # Create workspace
    url = "https://api.fabric.microsoft.com/v1/workspaces"
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code == 201:
        print(f"✅ Workspace '{workspace_name}' created successfully!")
        return response.json()
    else:
        print(f"❌ Failed to create workspace: {response.status_code}")
        print(response.text)
        return None

# Example usage
if __name__ == "__main__":
    workspace = create_fabric_workspace(
        workspace_name="my-data-workspace",
        capacity_id=os.getenv("CAPACITY_ID")
    )
    print(workspace)
```

### Using Azure CLI (for Power BI workspaces)

```bash
# Login to Azure
az login

# Create a Power BI workspace (compatible with Fabric)
az rest --method post \
  --uri "https://api.powerbi.com/v1.0/myorg/groups" \
  --headers "Content-Type=application/json" \
  --body '{"name":"my-fabric-workspace"}'
```

## Configure Workspace Settings

### 1. Assign to Capacity

**Via Portal:**
1. Navigate to workspace settings
2. Click **Premium** tab
3. Select **Capacity assignment**
4. Choose your Fabric capacity
5. Click **Save**

**Via API:**
```python
def assign_workspace_to_capacity(workspace_id, capacity_id):
    """Assign workspace to a Fabric capacity."""
    credential = DefaultAzureCredential()
    token = credential.get_token("https://api.fabric.microsoft.com/.default")
    
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}"
    body = {"capacityId": capacity_id}
    
    response = requests.patch(url, headers=headers, json=body)
    return response.status_code == 200
```

### 2. Configure Git Integration (Optional)

Enable version control for workspace items:

1. Navigate to **Workspace settings** → **Git integration**
2. Click **Connect to repository**
3. Select your Git provider (Azure DevOps, GitHub)
4. Configure:
   - Organization/Account
   - Project/Repository
   - Branch
   - Folder
5. Click **Connect**

### 3. Set Data Retention Policies

Configure how long data is retained:

1. Go to **Workspace settings** → **Data retention**
2. Set retention period (7-365 days)
3. Configure auto-delete policies
4. Click **Save**

## Assign Users and Permissions

### Workspace Roles

Microsoft Fabric workspaces support four roles:

| Role | Permissions |
|------|-------------|
| **Admin** | Full control including managing access and deleting workspace |
| **Member** | Create, edit, publish items; cannot manage workspace settings |
| **Contributor** | Create and edit items; cannot publish or manage settings |
| **Viewer** | Read-only access to workspace items |

### Add Users via Portal

1. Open the workspace
2. Click **Manage access** (or Settings → Access)
3. Click **+ Add people or groups**
4. Enter email addresses or group names
5. Select role from dropdown
6. Click **Add**

### Add Users Programmatically

```python
def add_workspace_user(workspace_id, user_email, role="Member"):
    """
    Add a user to a workspace with specified role.
    
    Args:
        workspace_id (str): Workspace ID
        user_email (str): User email address
        role (str): Admin, Member, Contributor, or Viewer
    
    Returns:
        bool: Success status
    """
    credential = DefaultAzureCredential()
    token = credential.get_token("https://api.fabric.microsoft.com/.default")
    
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "identifier": user_email,
        "groupUserAccessRight": role,
        "principalType": "User"
    }
    
    url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/users"
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code in [200, 201]:
        print(f"✅ User {user_email} added as {role}")
        return True
    else:
        print(f"❌ Failed to add user: {response.text}")
        return False
```

## Workspace Organization Best Practices

### 1. Naming Conventions

Use clear, consistent naming patterns:

```
Environment-Team-Purpose
Examples:
  - prod-finance-reporting
  - dev-dataeng-lakehouse
  - test-analytics-experiments
```

### 2. Workspace Structure

Organize workspaces by:
- **Environment**: Development, Test, Production
- **Team/Department**: Finance, Marketing, Engineering
- **Purpose**: Analytics, Reporting, Data Engineering

Example structure:
```
├── prod-sales-analytics
│   ├── Lakehouses
│   ├── Warehouses
│   ├── Semantic Models
│   └── Reports
├── dev-sales-analytics
│   ├── Lakehouses (for development)
│   └── Notebooks (for experimentation)
└── test-sales-analytics
    └── Validation artifacts
```

### 3. Capacity Planning

- **Development/Test**: Share a lower-tier capacity (F2)
- **Production**: Dedicated higher-tier capacity (F8+)
- **Auto-scaling**: Enable for production workloads
- **Monitoring**: Set up alerts for capacity usage

### 4. Access Control

```
Principle of Least Privilege:
├── Admins: 2-3 people maximum
├── Members: Team leads, senior developers
├── Contributors: Regular developers, analysts
└── Viewers: Business users, stakeholders
```

### 5. Workspace Governance

Implement governance policies:

```yaml
Workspace Governance:
  - Naming Standard: Enforced via Azure Policy
  - Capacity Assignment: Required before use
  - Git Integration: Mandatory for production
  - Data Classification: Label sensitive workspaces
  - Retention Policy: Set based on data type
  - Audit Logging: Enable for all workspaces
```

## Troubleshooting

### Issue: Cannot Create Workspace

**Symptoms**: "You don't have permission to create workspaces"

**Solution**:
- Verify you have Fabric license
- Check you're assigned Fabric Administrator role
- Ensure tenant settings allow workspace creation

### Issue: Cannot Assign to Capacity

**Symptoms**: "Capacity not available" error

**Solution**:
- Verify capacity is running (not paused)
- Check capacity has available resources
- Ensure you're Capacity Administrator

### Issue: Users Cannot Access Workspace

**Symptoms**: Users don't see workspace in their list

**Solution**:
- Verify users have appropriate Fabric license
- Check role assignment is correct
- Ensure workspace is in active capacity

## Verification Checklist

After workspace setup, verify:

- [ ] Workspace appears in workspace list
- [ ] Workspace assigned to active capacity
- [ ] Appropriate users have access
- [ ] Naming follows organizational standards
- [ ] Git integration configured (if required)
- [ ] Data retention policies set
- [ ] Can create items (lakehouse, warehouse, notebook)

## Next Steps

Now that your workspace is configured:

1. **Create a Lakehouse**: Store and process data
2. **Create a Warehouse**: Build analytical models
3. **Create Notebooks**: Develop data transformations
4. **Set up Pipelines**: Orchestrate data workflows
5. **Create Reports**: Build visualizations

## Additional Resources

- [Workspace Documentation](https://learn.microsoft.com/en-us/fabric/get-started/workspaces)
- [Fabric REST API - Workspaces](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces)
- [Capacity Management](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)
- [Git Integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration)
