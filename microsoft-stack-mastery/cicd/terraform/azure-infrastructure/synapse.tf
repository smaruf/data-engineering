# Azure Synapse Analytics Workspace
resource "azurerm_synapse_workspace" "main" {
  count                                = var.enable_synapse ? 1 : 0
  name                                 = "${local.resource_prefix}-synapse"
  resource_group_name                  = azurerm_resource_group.main.name
  location                             = azurerm_resource_group.main.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.containers["raw"].id
  sql_administrator_login              = var.synapse_sql_admin_username
  sql_administrator_login_password     = var.synapse_sql_admin_password != null ? var.synapse_sql_admin_password : random_password.synapse_sql_password[0].result

  identity {
    type = "SystemAssigned"
  }

  aad_admin {
    login     = "AzureAD Admin"
    object_id = data.azurerm_client_config.current.object_id
    tenant_id = data.azurerm_client_config.current.tenant_id
  }

  tags = merge(
    local.common_tags,
    {
      Purpose = "Data Warehouse and Analytics"
    }
  )
}

# Random password for Synapse SQL admin
resource "random_password" "synapse_sql_password" {
  count   = var.enable_synapse && var.synapse_sql_admin_password == null ? 1 : 0
  length  = 16
  special = true
}

# Store Synapse SQL password in Key Vault
resource "azurerm_key_vault_secret" "synapse_sql_password" {
  count        = var.enable_synapse ? 1 : 0
  name         = "synapse-sql-admin-password"
  value        = var.synapse_sql_admin_password != null ? var.synapse_sql_admin_password : random_password.synapse_sql_password[0].result
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault.main]
}

# Synapse Firewall Rule - Allow Azure Services
resource "azurerm_synapse_firewall_rule" "allow_azure_services" {
  count                = var.enable_synapse ? 1 : 0
  name                 = "AllowAllWindowsAzureIps"
  synapse_workspace_id = azurerm_synapse_workspace.main[0].id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "0.0.0.0"
}

# Synapse Firewall Rules for allowed IPs
resource "azurerm_synapse_firewall_rule" "allowed_ips" {
  count                = var.enable_synapse ? length(var.allowed_ip_ranges) : 0
  name                 = "AllowedIP-${count.index}"
  synapse_workspace_id = azurerm_synapse_workspace.main[0].id
  start_ip_address     = element(split("/", var.allowed_ip_ranges[count.index]), 0)
  end_ip_address       = element(split("/", var.allowed_ip_ranges[count.index]), 0)
}

# Synapse Spark Pool
resource "azurerm_synapse_spark_pool" "main" {
  count                = var.enable_synapse ? 1 : 0
  name                 = "${var.project_name}spark${var.environment}"
  synapse_workspace_id = azurerm_synapse_workspace.main[0].id
  node_size_family     = "MemoryOptimized"
  node_size            = var.synapse_spark_node_size
  node_count           = var.synapse_spark_autoscale_enabled ? null : var.synapse_spark_node_count

  dynamic "auto_scale" {
    for_each = var.synapse_spark_autoscale_enabled ? [1] : []
    content {
      min_node_count = var.synapse_spark_min_nodes
      max_node_count = var.synapse_spark_max_nodes
    }
  }

  auto_pause {
    delay_in_minutes = 15
  }

  spark_version = var.synapse_spark_version

  library_requirement {
    content  = <<-EOT
      numpy
      pandas
      pyarrow
      delta-spark
      pyspark
    EOT
    filename = "requirements.txt"
  }

  tags = merge(
    local.common_tags,
    {
      Purpose = "Spark Processing"
    }
  )
}

# Synapse SQL Pool (Dedicated)
resource "azurerm_synapse_sql_pool" "main" {
  count                = var.enable_synapse && var.environment == "prod" ? 1 : 0
  name                 = "${var.project_name}sqldw${var.environment}"
  synapse_workspace_id = azurerm_synapse_workspace.main[0].id
  sku_name             = "DW100c"
  create_mode          = "Default"
  storage_account_type = "GRS"

  tags = merge(
    local.common_tags,
    {
      Purpose = "Data Warehouse"
    }
  )
}

# Role Assignment - Synapse to Storage
resource "azurerm_role_assignment" "synapse_storage_blob_contributor" {
  count                = var.enable_synapse ? 1 : 0
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_synapse_workspace.main[0].identity[0].principal_id
}

# Synapse Managed Private Endpoint to Storage
resource "azurerm_synapse_managed_private_endpoint" "datalake" {
  count                = var.enable_synapse && var.enable_private_endpoints ? 1 : 0
  name                 = "pe-to-datalake"
  synapse_workspace_id = azurerm_synapse_workspace.main[0].id
  target_resource_id   = azurerm_storage_account.datalake.id
  subresource_name     = "dfs"
}

# Synapse Integration Runtime
resource "azurerm_synapse_integration_runtime_azure" "main" {
  count                = var.enable_synapse ? 1 : 0
  name                 = "AutoResolveIntegrationRuntime"
  synapse_workspace_id = azurerm_synapse_workspace.main[0].id
  location             = azurerm_resource_group.main.location
}

# Synapse Linked Service to Data Lake
resource "azurerm_synapse_linked_service" "datalake" {
  count                = var.enable_synapse ? 1 : 0
  name                 = "ls_datalake"
  synapse_workspace_id = azurerm_synapse_workspace.main[0].id
  type                 = "AzureBlobFS"

  type_properties_json = jsonencode({
    url = azurerm_storage_account.datalake.primary_dfs_endpoint
  })

  integration_runtime {
    name = azurerm_synapse_integration_runtime_azure.main[0].name
  }
}

# Diagnostic settings for Synapse
resource "azurerm_monitor_diagnostic_setting" "synapse" {
  count                      = var.enable_synapse && var.enable_diagnostic_settings ? 1 : 0
  name                       = "${azurerm_synapse_workspace.main[0].name}-diagnostics"
  target_resource_id         = azurerm_synapse_workspace.main[0].id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "SynapseRbacOperations"
  }

  enabled_log {
    category = "GatewayApiRequests"
  }

  enabled_log {
    category = "SQLSecurityAuditEvents"
  }

  enabled_log {
    category = "BuiltinSqlReqsEnded"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

# Outputs
output "synapse_workspace_id" {
  value       = var.enable_synapse ? azurerm_synapse_workspace.main[0].id : null
  description = "Synapse workspace ID"
}

output "synapse_workspace_name" {
  value       = var.enable_synapse ? azurerm_synapse_workspace.main[0].name : null
  description = "Synapse workspace name"
}

output "synapse_workspace_endpoint" {
  value       = var.enable_synapse ? azurerm_synapse_workspace.main[0].connectivity_endpoints : null
  description = "Synapse workspace endpoints"
}

output "synapse_spark_pool_id" {
  value       = var.enable_synapse ? azurerm_synapse_spark_pool.main[0].id : null
  description = "Synapse Spark pool ID"
}

output "synapse_spark_pool_name" {
  value       = var.enable_synapse ? azurerm_synapse_spark_pool.main[0].name : null
  description = "Synapse Spark pool name"
}

output "synapse_sql_pool_id" {
  value       = var.enable_synapse && var.environment == "prod" ? azurerm_synapse_sql_pool.main[0].id : null
  description = "Synapse SQL pool ID"
}
