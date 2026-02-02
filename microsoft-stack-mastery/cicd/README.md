# CI/CD Pipeline Configuration

This directory contains comprehensive CI/CD pipeline configurations for the Microsoft Stack Mastery project, supporting multiple platforms and deployment targets.

## 📁 Directory Structure

```
cicd/
├── gitlab-ci/              # GitLab CI/CD configurations
│   ├── .gitlab-ci.yml      # Main pipeline configuration
│   ├── build-jobs.yml      # Build job definitions
│   └── deploy-jobs.yml     # Deployment job definitions
├── azure-devops/           # Azure DevOps Pipelines
│   ├── azure-pipelines.yml # Main pipeline orchestrator
│   ├── build-pipeline.yml  # Build stage definitions
│   ├── test-pipeline.yml   # Test stage definitions
│   └── deploy-pipeline.yml # Deployment stage definitions
├── github-actions/         # GitHub Actions Workflows
│   ├── ci-workflow.yml     # Continuous Integration
│   ├── deploy-fabric.yml   # Microsoft Fabric deployment
│   └── quality-checks.yml  # Code quality & security
└── terraform/              # Infrastructure as Code
    └── azure-infrastructure/
        ├── main.tf         # Main Terraform configuration
        ├── variables.tf    # Input variables
        ├── storage.tf      # Azure Storage resources
        ├── synapse.tf      # Synapse workspace resources
        └── fabric.tf       # Fabric capacity resources
```

## 🚀 Quick Start

### Prerequisites

- **Azure Subscription** with appropriate permissions
- **Service Principal** for authentication
- **Required Secrets** configured in your CI/CD platform
- **Terraform** >= 1.5.0 (for infrastructure deployment)

### Required Secrets

Configure these secrets in your CI/CD platform:

#### Azure Credentials
- `AZURE_CLIENT_ID` - Service Principal application ID
- `AZURE_CLIENT_SECRET` - Service Principal password
- `AZURE_TENANT_ID` - Azure AD tenant ID
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID

#### Fabric Credentials
- `DEV_FABRIC_WORKSPACE` - Development workspace name
- `STAGING_FABRIC_WORKSPACE` - Staging workspace name
- `PROD_FABRIC_WORKSPACE` - Production workspace name

#### Resource Groups
- `DEV_RESOURCE_GROUP` - Development resource group name
- `STAGING_RESOURCE_GROUP` - Staging resource group name
- `PROD_RESOURCE_GROUP` - Production resource group name

#### Optional
- `SONAR_TOKEN` - SonarCloud token for code analysis
- `TEAMS_WEBHOOK_URL` - Microsoft Teams webhook for notifications
- `DATABRICKS_HOST` - Databricks workspace URL
- `DATABRICKS_TOKEN` - Databricks access token

## 🔧 GitLab CI/CD

### Pipeline Stages

1. **Validate** - Code formatting and linting
2. **Build** - Compile Java & Python projects
3. **Test** - Unit, integration, and performance tests
4. **Security** - Dependency checks, secret scanning, container scanning
5. **Deploy** - Deploy to Azure and Microsoft Fabric
6. **Post-Deploy** - Smoke tests and health checks

### Usage

```yaml
# Copy .gitlab-ci.yml to your repository root
cp cicd/gitlab-ci/.gitlab-ci.yml .gitlab-ci.yml

# Ensure include paths are correct
include:
  - local: 'cicd/gitlab-ci/build-jobs.yml'
  - local: 'cicd/gitlab-ci/deploy-jobs.yml'
```

### Running Pipelines

- **Automatic**: Triggers on push to `main`, `develop` branches
- **Manual**: Use GitLab UI to trigger specific jobs
- **Merge Requests**: Runs validation and tests automatically

### Key Features

- ✅ Multi-language support (Java, Python, Spark)
- ✅ Parallel job execution
- ✅ Artifact caching for faster builds
- ✅ Docker image building and pushing
- ✅ Terraform infrastructure deployment
- ✅ Environment-specific deployments (dev, staging, prod)

## 🔷 Azure DevOps Pipelines

### Pipeline Structure

```yaml
azure-pipelines.yml           # Main orchestrator
  ├── build-pipeline.yml      # Build Java, Python, Spark, Docker
  ├── test-pipeline.yml       # All test stages
  └── deploy-pipeline.yml     # Multi-environment deployment
```

### Usage

1. **Import Pipeline**:
   - Go to Azure DevOps → Pipelines → New Pipeline
   - Select your repository
   - Choose "Existing Azure Pipelines YAML file"
   - Select `cicd/azure-devops/azure-pipelines.yml`

2. **Configure Variable Groups**:
   ```bash
   # Create variable groups
   az pipelines variable-group create \
     --name azure-credentials \
     --variables \
       AZURE_CLIENT_ID=<value> \
       AZURE_CLIENT_SECRET=<value> \
       AZURE_TENANT_ID=<value> \
       AZURE_SUBSCRIPTION_ID=<value>

   az pipelines variable-group create \
     --name fabric-credentials \
     --variables \
       DEV_FABRIC_WORKSPACE=<value> \
       PROD_FABRIC_WORKSPACE=<value>
   ```

### Key Features

- ✅ Template-based modular design
- ✅ Service connections for secure authentication
- ✅ Multi-stage deployments with approvals
- ✅ Test result publishing
- ✅ Code coverage reporting
- ✅ SonarCloud integration
- ✅ Automated notifications (Teams, Email)

## 🐙 GitHub Actions

### Workflows

1. **CI Workflow** (`ci-workflow.yml`)
   - Runs on: Push, Pull Request
   - Jobs: Validate, Build Java/Python/Spark, Integration Tests, Docker Build

2. **Deploy Fabric** (`deploy-fabric.yml`)
   - Runs on: Workflow Dispatch, Push to main
   - Jobs: Deploy notebooks, pipelines, semantic models, lakehouses

3. **Quality Checks** (`quality-checks.yml`)
   - Runs on: PR, Push, Weekly schedule
   - Jobs: Security scanning, linting, CodeQL, SonarCloud

### Usage

```bash
# Copy workflows to .github/workflows/
mkdir -p .github/workflows
cp cicd/github-actions/*.yml .github/workflows/

# Configure secrets in GitHub repository settings
gh secret set AZURE_CREDENTIALS --body "$(cat azure-credentials.json)"
gh secret set DEV_FABRIC_WORKSPACE --body "dev-workspace"
```

### Key Features

- ✅ Matrix builds for multiple versions
- ✅ Dependency caching
- ✅ SARIF security reports
- ✅ Codecov integration
- ✅ Manual workflow triggers with inputs
- ✅ Automatic rollback on failure
- ✅ GitHub Container Registry integration

## 🏗️ Terraform Infrastructure

### Resources Deployed

#### Core Infrastructure
- Resource Group
- Virtual Network with subnets
- Key Vault for secrets
- Log Analytics Workspace
- Application Insights

#### Storage
- Data Lake Gen2 Storage Account
  - Containers: raw, bronze, silver, gold, archive
- General Purpose Storage Account
  - Containers: artifacts, logs, backups
- Private Endpoints (optional)

#### Analytics
- **Azure Synapse Analytics** (optional)
  - Workspace with AAD admin
  - Spark Pool with autoscaling
  - SQL Pool (production only)
  - Linked services and integration runtimes

- **Microsoft Fabric** (optional)
  - Fabric Capacity (F2-F64)
  - Azure Data Factory for integration
  - Event Hub for real-time analytics
  - Stream Analytics jobs

### Usage

#### Initialize Backend

```bash
# Create Terraform state storage
az group create --name terraform-state-rg --location eastus

az storage account create \
  --name tfstatemicrosoftstack \
  --resource-group terraform-state-rg \
  --location eastus \
  --sku Standard_LRS

az storage container create \
  --name tfstate \
  --account-name tfstatemicrosoftstack
```

#### Deploy Infrastructure

```bash
cd cicd/terraform/azure-infrastructure

# Initialize Terraform
terraform init

# Create workspace for environment
terraform workspace new dev
terraform workspace select dev

# Plan deployment
terraform plan \
  -var="environment=dev" \
  -var="enable_synapse=true" \
  -var="enable_fabric=false" \
  -out=tfplan

# Apply deployment
terraform apply tfplan
```

#### Environment-Specific Configurations

**Development**:
```bash
terraform apply \
  -var="environment=dev" \
  -var="enable_synapse=true" \
  -var="enable_fabric=false" \
  -var="synapse_spark_autoscale_enabled=true" \
  -var="synapse_spark_min_nodes=3" \
  -var="synapse_spark_max_nodes=5"
```

**Staging**:
```bash
terraform apply \
  -var="environment=staging" \
  -var="enable_synapse=true" \
  -var="enable_fabric=true" \
  -var="fabric_capacity_sku=F2" \
  -var="storage_replication_type=GRS"
```

**Production**:
```bash
terraform apply \
  -var="environment=prod" \
  -var="enable_synapse=true" \
  -var="enable_fabric=true" \
  -var="fabric_capacity_sku=F4" \
  -var="storage_replication_type=GZRS" \
  -var="enable_private_endpoints=true" \
  -var="enable_backup=true"
```

### Key Features

- ✅ Multi-environment support with workspaces
- ✅ Modular resource organization
- ✅ Comprehensive tagging strategy
- ✅ Diagnostic settings and monitoring
- ✅ RBAC and managed identities
- ✅ Network security with private endpoints
- ✅ Backup and retention policies

## 🔒 Security Best Practices

### Secrets Management

- Store all credentials in **Azure Key Vault**
- Use **Managed Identities** where possible
- Rotate secrets regularly
- Never commit secrets to version control

### Network Security

- Enable **Private Endpoints** for production
- Configure **Network Security Groups**
- Use **Azure Firewall** for outbound traffic
- Restrict IP ranges with `allowed_ip_ranges` variable

### Compliance

- Enable **diagnostic settings** for all resources
- Use **Azure Policy** for governance
- Implement **RBAC** with least privilege
- Enable **Azure Defender** for threat protection

## 📊 Monitoring and Observability

### Application Insights

All deployments include Application Insights for:
- Performance monitoring
- Dependency tracking
- Exception logging
- Custom metrics

### Log Analytics

Centralized logging for:
- Pipeline execution logs
- Resource diagnostics
- Security audit logs
- Performance metrics

### Alerts

Configure alerts for:
- High CPU/Memory usage
- Failed deployments
- Security violations
- Cost thresholds

## 🧪 Testing Strategy

### Unit Tests
- Python: `pytest` with coverage
- Java: JUnit with JaCoCo

### Integration Tests
- Database connectivity
- API endpoint validation
- Service integration

### Security Tests
- Dependency scanning (OWASP, Safety)
- Secret detection (TruffleHog)
- Container scanning (Trivy)
- Static analysis (Bandit, SonarCloud)

### Performance Tests
- Load testing with Locust
- Benchmark tests with pytest-benchmark

## 🔄 Deployment Strategies

### Blue-Green Deployment

Supported in Azure App Service with deployment slots:
```yaml
- task: AzureAppServiceManage@0
  inputs:
    SourceSlot: 'staging'
    SwapWithProduction: true
```

### Canary Deployment

Progressive rollout with traffic splitting:
```yaml
traffic_routing:
  - production: 90%
  - canary: 10%
```

### Rollback Strategy

Automated rollback on failure:
- GitHub Actions: Automatic revert to previous commit
- Azure DevOps: Manual rollback with approval
- GitLab CI: Destroy and redeploy previous version

## 📚 Additional Resources

### Documentation
- [Azure DevOps Pipelines](https://docs.microsoft.com/azure/devops/pipelines/)
- [GitHub Actions](https://docs.github.com/actions)
- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

### Microsoft Fabric
- [Fabric Documentation](https://learn.microsoft.com/fabric/)
- [Fabric REST API](https://learn.microsoft.com/rest/api/fabric/)
- [Fabric SDK](https://pypi.org/project/msfabricpysdkcore/)

### Azure Synapse
- [Synapse Documentation](https://learn.microsoft.com/azure/synapse-analytics/)
- [Synapse CI/CD](https://learn.microsoft.com/azure/synapse-analytics/cicd/continuous-integration-delivery)

## 🤝 Contributing

When adding new CI/CD configurations:

1. Test in a feature branch first
2. Follow existing patterns and conventions
3. Add appropriate error handling
4. Update this README with changes
5. Include example usage

## 📝 License

This CI/CD configuration is part of the Microsoft Stack Mastery project.

## 🆘 Support

For issues or questions:
- Create an issue in the repository
- Contact the Data Engineering team
- Consult platform-specific documentation

---

**Last Updated**: 2024
**Maintained By**: Data Engineering Team
