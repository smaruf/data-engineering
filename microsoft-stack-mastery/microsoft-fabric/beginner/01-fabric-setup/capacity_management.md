# Microsoft Fabric Capacity Management Guide

This guide covers Microsoft Fabric capacity planning, management, monitoring, and optimization.

## Table of Contents
1. [Understanding Fabric Capacity](#understanding-fabric-capacity)
2. [Capacity SKUs and Pricing](#capacity-skus-and-pricing)
3. [Creating and Managing Capacities](#creating-and-managing-capacities)
4. [Monitoring and Optimization](#monitoring-and-optimization)
5. [Best Practices](#best-practices)

## Understanding Fabric Capacity

### What is Fabric Capacity?

Microsoft Fabric capacity is the compute and storage resources allocated to run Fabric workloads. All Fabric items (lakehouses, warehouses, notebooks, etc.) run within a capacity.

### Capacity Architecture

```
┌─────────────────────────────────────────────────┐
│            Fabric Capacity (F64)                │
├─────────────────────────────────────────────────┤
│  Compute Units (CUs): 64                        │
│  OneLake Storage: Pooled across capacity        │
├──────────────┬──────────────┬──────────────────┤
│  Workspace A │  Workspace B │  Workspace C     │
│  (10 CUs)    │  (30 CUs)    │  (24 CUs)        │
├──────────────┴──────────────┴──────────────────┤
│  Auto-scaling: +20% (12.8 CUs) when needed     │
└─────────────────────────────────────────────────┘
```

### Capacity Units (CUs)

Fabric uses Capacity Units to measure compute resources:

- **1 CU** = Standardized compute resource
- Different operations consume CUs at different rates
- CUs are pooled and shared across all workspaces in capacity

## Capacity SKUs and Pricing

### Fabric Capacity SKUs

| SKU | Capacity Units (CUs) | v-Cores | RAM (GB) | Price/Month (USD)* |
|-----|---------------------|---------|----------|-------------------|
| F2  | 2                   | 2       | 16       | ~$262 |
| F4  | 4                   | 4       | 32       | ~$524 |
| F8  | 8                   | 8       | 64       | ~$1,048 |
| F16 | 16                  | 16      | 128      | ~$2,097 |
| F32 | 32                  | 32      | 256      | ~$4,194 |
| F64 | 64                  | 64      | 512      | ~$8,388 |
| F128| 128                 | 128     | 1,024    | ~$16,777 |
| F256| 256                 | 256     | 2,048    | ~$33,554 |
| F512| 512                 | 512     | 4,096    | ~$67,108 |

*Prices are approximate and vary by region. Check Azure pricing for exact costs.

### Trial Capacity

Microsoft offers a **60-day trial capacity** for evaluation:

- **Duration**: 60 days from activation
- **Capacity**: Equivalent to F64 SKU
- **Limitations**: 
  - One trial per organization
  - Cannot be paused/resumed
  - Expires automatically after 60 days
- **Perfect for**: Learning, POCs, evaluations

### Power BI Premium Capacity

Existing Power BI Premium capacities can run Fabric workloads:

| P SKU | Equivalent F SKU | v-Cores |
|-------|------------------|---------|
| P1    | F64             | 8       |
| P2    | F128            | 16      |
| P3    | F256            | 32      |
| P4    | F512            | 64      |
| P5    | -               | 128     |

## Creating and Managing Capacities

### Create Capacity via Azure Portal

#### Step 1: Navigate to Fabric Capacity

1. Go to [Azure Portal](https://portal.azure.com/)
2. Search for "Fabric Capacity" or "Microsoft Fabric"
3. Click **+ Create**

#### Step 2: Configure Capacity

```yaml
Basics:
  Subscription: Your Azure subscription
  Resource Group: Create new or select existing
  Capacity Name: fabric-prod-capacity-001
  Region: East US 2
  Size: F8 (8 Capacity Units)

Advanced:
  Auto-scale: Enabled
  Maximum auto-scale: 20% (9.6 CUs total)
  
Tags:
  Environment: Production
  CostCenter: IT-Analytics
  Owner: data-engineering-team

Review + Create: Verify settings and create
```

#### Step 3: Wait for Deployment

Deployment typically takes 5-10 minutes.

### Create Capacity via Azure CLI

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "Your Subscription Name"

# Create resource group (if needed)
az group create \
  --name rg-fabric-prod \
  --location eastus2

# Create Fabric capacity
az fabric capacity create \
  --resource-group rg-fabric-prod \
  --capacity-name fabric-prod-capacity-001 \
  --location eastus2 \
  --sku-name F8 \
  --administration-members "admin@company.com" \
  --tags Environment=Production CostCenter=IT-Analytics
```

### Create Capacity via Python

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.fabric import FabricManagementClient
from azure.mgmt.fabric.models import Capacity, CapacitySku

def create_fabric_capacity(
    subscription_id,
    resource_group,
    capacity_name,
    location,
    sku_name="F8",
    admin_members=None
):
    """
    Create a Microsoft Fabric capacity.
    
    Args:
        subscription_id (str): Azure subscription ID
        resource_group (str): Resource group name
        capacity_name (str): Capacity name
        location (str): Azure region
        sku_name (str): SKU (F2, F4, F8, etc.)
        admin_members (list): List of admin emails
    """
    # Authenticate
    credential = DefaultAzureCredential()
    client = FabricManagementClient(credential, subscription_id)
    
    # Prepare capacity configuration
    capacity = Capacity(
        location=location,
        sku=CapacitySku(name=sku_name, tier="Fabric"),
        properties={
            "administration": {
                "members": admin_members or []
            }
        },
        tags={
            "Environment": "Production",
            "ManagedBy": "Infrastructure-Team"
        }
    )
    
    # Create capacity
    poller = client.capacities.begin_create_or_update(
        resource_group_name=resource_group,
        capacity_name=capacity_name,
        capacity=capacity
    )
    
    result = poller.result()
    print(f"✅ Capacity '{capacity_name}' created successfully!")
    return result
```

### Manage Capacity States

#### Pause Capacity

Pause to stop billing (workloads become unavailable):

```bash
# Via Azure CLI
az fabric capacity update \
  --resource-group rg-fabric-prod \
  --capacity-name fabric-prod-capacity-001 \
  --state Paused
```

```python
# Via Python
def pause_capacity(subscription_id, resource_group, capacity_name):
    """Pause a Fabric capacity to stop billing."""
    credential = DefaultAzureCredential()
    client = FabricManagementClient(credential, subscription_id)
    
    poller = client.capacities.begin_suspend(
        resource_group_name=resource_group,
        capacity_name=capacity_name
    )
    
    poller.result()
    print(f"✅ Capacity '{capacity_name}' paused")
```

#### Resume Capacity

```bash
# Via Azure CLI
az fabric capacity update \
  --resource-group rg-fabric-prod \
  --capacity-name fabric-prod-capacity-001 \
  --state Active
```

```python
# Via Python
def resume_capacity(subscription_id, resource_group, capacity_name):
    """Resume a paused Fabric capacity."""
    credential = DefaultAzureCredential()
    client = FabricManagementClient(credential, subscription_id)
    
    poller = client.capacities.begin_resume(
        resource_group_name=resource_group,
        capacity_name=capacity_name
    )
    
    poller.result()
    print(f"✅ Capacity '{capacity_name}' resumed")
```

#### Scale Capacity

```bash
# Scale to F16
az fabric capacity update \
  --resource-group rg-fabric-prod \
  --capacity-name fabric-prod-capacity-001 \
  --sku-name F16
```

## Monitoring and Optimization

### Monitoring in Azure Portal

1. Navigate to your Fabric capacity in Azure Portal
2. Select **Metrics** to view:
   - **CPU Percentage**: Compute utilization
   - **Memory Percentage**: Memory utilization
   - **Active Capacity Units**: CUs in use
   - **Queued Requests**: Workloads waiting for resources

### Monitoring in Fabric Portal

1. Go to [Fabric Admin Portal](https://app.fabric.microsoft.com/admin)
2. Select **Capacity settings**
3. Choose your capacity
4. View **Capacity Metrics**:
   - CU consumption by workspace
   - CU consumption by operation type
   - Peak usage times

### Key Metrics to Monitor

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU Percentage | > 80% | Consider scaling up |
| Memory Percentage | > 85% | Review workload efficiency |
| CU Utilization | > 90% | Enable auto-scale or scale up |
| Throttling Events | > 0 | Immediate attention needed |
| Auto-scale Triggers | Frequent | Permanently scale up |

### Cost Optimization Strategies

#### 1. Right-Sizing

```python
def analyze_capacity_usage(capacity_id):
    """
    Analyze capacity usage to recommend right-sizing.
    
    Returns sizing recommendations based on historical usage.
    """
    # Pseudo-code for analysis
    metrics = get_capacity_metrics(capacity_id, days=30)
    
    avg_cpu = metrics['cpu_percentage'].mean()
    max_cpu = metrics['cpu_percentage'].max()
    p95_cpu = metrics['cpu_percentage'].quantile(0.95)
    
    if p95_cpu < 50:
        return "Consider scaling down to save costs"
    elif p95_cpu > 85:
        return "Consider scaling up to improve performance"
    else:
        return "Current capacity is appropriately sized"
```

#### 2. Auto-Scaling Configuration

Enable auto-scaling for variable workloads:

```python
def configure_autoscale(capacity_id, max_scale_percentage=20):
    """
    Configure auto-scaling for a Fabric capacity.
    
    Args:
        capacity_id (str): Capacity ID
        max_scale_percentage (int): Max % to auto-scale (default 20%)
    """
    # Auto-scaling adds temporary CUs during peak usage
    # You're billed for the additional CUs used
    
    config = {
        "autoScale": {
            "enabled": True,
            "maxScaleOut": max_scale_percentage
        }
    }
    
    return config
```

#### 3. Pause/Resume Schedules

Automate pause/resume for non-production environments:

```python
import schedule
import time
from datetime import datetime

def pause_resume_schedule(
    subscription_id,
    resource_group,
    capacity_name
):
    """
    Schedule capacity pause during non-business hours.
    
    Pauses capacity at 8 PM, resumes at 6 AM on weekdays.
    """
    def pause_job():
        if datetime.now().weekday() < 5:  # Monday-Friday
            pause_capacity(subscription_id, resource_group, capacity_name)
            print("Capacity paused for the night")
    
    def resume_job():
        if datetime.now().weekday() < 5:  # Monday-Friday
            resume_capacity(subscription_id, resource_group, capacity_name)
            print("Capacity resumed for business hours")
    
    # Schedule jobs
    schedule.every().day.at("20:00").do(pause_job)
    schedule.every().day.at("06:00").do(resume_job)
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)
```

## Best Practices

### 1. Capacity Planning

```yaml
Capacity Planning Checklist:
  ✓ Estimate workload requirements (CUs needed)
  ✓ Plan for growth (20-30% headroom)
  ✓ Identify peak usage times
  ✓ Determine acceptable performance SLAs
  ✓ Budget for auto-scaling costs
  ✓ Plan DR/HA strategy
```

### 2. Environment Strategy

```
Development: F2-F4 (shared, pausable)
  └─ Used for development and testing
  └─ Paused outside business hours

Test/QA: F4-F8 (shared)
  └─ Pre-production validation
  └─ Paused when not in use

Production: F16+ (dedicated, always-on)
  └─ Business-critical workloads
  └─ Auto-scaling enabled
  └─ 24/7 availability
```

### 3. Workspace Assignment

```python
# Assign workspaces to appropriate capacities
workspace_capacity_mapping = {
    "prod-finance-reporting": "fabric-prod-f64",
    "prod-sales-analytics": "fabric-prod-f64",
    "dev-data-engineering": "fabric-dev-f4",
    "test-bi-reports": "fabric-test-f8"
}
```

### 4. Monitoring and Alerts

Set up Azure Monitor alerts:

```yaml
Alerts:
  - Name: High CPU Usage
    Metric: CPU Percentage
    Threshold: > 85%
    Duration: 15 minutes
    Action: Email admin, auto-scale
  
  - Name: Memory Pressure
    Metric: Memory Percentage
    Threshold: > 90%
    Duration: 10 minutes
    Action: Email admin
  
  - Name: Throttling Detected
    Metric: Throttling Events
    Threshold: > 0
    Duration: 5 minutes
    Action: Page on-call, email admin
```

### 5. Cost Management

```python
def estimate_monthly_cost(sku_name, hours_per_month=730):
    """
    Estimate monthly cost for a Fabric capacity.
    
    Args:
        sku_name (str): SKU name (F2, F4, F8, etc.)
        hours_per_month (int): Hours capacity is active
    
    Returns:
        float: Estimated monthly cost in USD
    """
    # Approximate hourly costs
    sku_hourly_cost = {
        "F2": 0.36,
        "F4": 0.72,
        "F8": 1.44,
        "F16": 2.88,
        "F32": 5.75,
        "F64": 11.51,
        "F128": 23.01,
        "F256": 46.03,
        "F512": 92.05
    }
    
    hourly_cost = sku_hourly_cost.get(sku_name, 0)
    monthly_cost = hourly_cost * hours_per_month
    
    print(f"SKU: {sku_name}")
    print(f"Hourly Cost: ${hourly_cost:.2f}")
    print(f"Hours/Month: {hours_per_month}")
    print(f"Monthly Cost: ${monthly_cost:.2f}")
    
    return monthly_cost
```

## Troubleshooting

### Issue: Capacity at 100% Utilization

**Symptoms**: Slow performance, queued operations

**Solutions**:
1. Enable auto-scaling for immediate relief
2. Scale up to larger SKU
3. Optimize workloads (reduce CU consumption)
4. Distribute workloads across multiple capacities

### Issue: High Costs

**Symptoms**: Unexpected Azure bills

**Solutions**:
1. Review capacity utilization metrics
2. Pause non-production capacities when not in use
3. Right-size capacities based on actual usage
4. Implement automated pause/resume schedules
5. Optimize inefficient workloads

### Issue: Throttling Errors

**Symptoms**: "Capacity limit exceeded" errors

**Solutions**:
1. Immediately enable auto-scaling
2. Review operations consuming high CUs
3. Spread operations across time
4. Scale to larger capacity

## Additional Resources

- [Fabric Capacity Documentation](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)
- [Capacity Metrics](https://learn.microsoft.com/en-us/fabric/enterprise/metrics-app)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
- [Capacity Planning Guide](https://learn.microsoft.com/en-us/fabric/enterprise/plan-capacity)
