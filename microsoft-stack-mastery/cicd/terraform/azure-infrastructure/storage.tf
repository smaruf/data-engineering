# Azure Storage Account for Data Lake Gen2
resource "azurerm_storage_account" "datalake" {
  name                     = "${var.project_name}${var.environment}dl${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_replication_type
  account_kind             = "StorageV2"
  is_hns_enabled           = var.enable_hierarchical_namespace

  blob_properties {
    versioning_enabled = true
    change_feed_enabled = true

    delete_retention_policy {
      days = var.backup_retention_days
    }

    container_delete_retention_policy {
      days = var.backup_retention_days
    }
  }

  network_rules {
    default_action             = var.environment == "prod" ? "Deny" : "Allow"
    ip_rules                   = var.allowed_ip_ranges
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = var.enable_private_endpoints ? [azurerm_subnet.data.id] : []
  }

  identity {
    type = "SystemAssigned"
  }

  tags = merge(
    local.common_tags,
    {
      Purpose = "Data Lake Storage"
    }
  )
}

# Data Lake Gen2 Containers
resource "azurerm_storage_data_lake_gen2_filesystem" "containers" {
  for_each           = toset(var.data_lake_containers)
  name               = each.value
  storage_account_id = azurerm_storage_account.datalake.id

  properties = {
    environment = var.environment
  }
}

# Storage Account for general purpose
resource "azurerm_storage_account" "general" {
  name                     = "${var.project_name}${var.environment}sa${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_replication_type
  account_kind             = "StorageV2"

  blob_properties {
    delete_retention_policy {
      days = 7
    }
  }

  identity {
    type = "SystemAssigned"
  }

  tags = merge(
    local.common_tags,
    {
      Purpose = "General Storage"
    }
  )
}

# Blob containers for general storage
resource "azurerm_storage_container" "artifacts" {
  name                  = "artifacts"
  storage_account_name  = azurerm_storage_account.general.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "logs" {
  name                  = "logs"
  storage_account_name  = azurerm_storage_account.general.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "backups" {
  name                  = "backups"
  storage_account_name  = azurerm_storage_account.general.name
  container_access_type = "private"
}

# Private endpoint for Data Lake (if enabled)
resource "azurerm_private_endpoint" "datalake_blob" {
  count               = var.enable_private_endpoints ? 1 : 0
  name                = "${azurerm_storage_account.datalake.name}-blob-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.data.id

  private_service_connection {
    name                           = "${azurerm_storage_account.datalake.name}-blob-psc"
    private_connection_resource_id = azurerm_storage_account.datalake.id
    is_manual_connection           = false
    subresource_names              = ["blob"]
  }

  tags = local.common_tags
}

resource "azurerm_private_endpoint" "datalake_dfs" {
  count               = var.enable_private_endpoints ? 1 : 0
  name                = "${azurerm_storage_account.datalake.name}-dfs-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.data.id

  private_service_connection {
    name                           = "${azurerm_storage_account.datalake.name}-dfs-psc"
    private_connection_resource_id = azurerm_storage_account.datalake.id
    is_manual_connection           = false
    subresource_names              = ["dfs"]
  }

  tags = local.common_tags
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "${local.resource_prefix}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = var.vnet_address_space

  tags = local.common_tags
}

# Subnets
resource "azurerm_subnet" "data" {
  name                 = "data-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_prefixes.data]

  service_endpoints = [
    "Microsoft.Storage",
    "Microsoft.Sql",
    "Microsoft.KeyVault"
  ]
}

resource "azurerm_subnet" "compute" {
  name                 = "compute-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_prefixes.compute]
}

resource "azurerm_subnet" "fabric" {
  name                 = "fabric-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_prefixes.fabric]
}

resource "azurerm_subnet" "synapse" {
  name                 = "synapse-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_prefixes.synapse]
}

# Diagnostic settings for storage accounts
resource "azurerm_monitor_diagnostic_setting" "datalake" {
  count                      = var.enable_diagnostic_settings ? 1 : 0
  name                       = "${azurerm_storage_account.datalake.name}-diagnostics"
  target_resource_id         = "${azurerm_storage_account.datalake.id}/blobServices/default"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "StorageRead"
  }

  enabled_log {
    category = "StorageWrite"
  }

  enabled_log {
    category = "StorageDelete"
  }

  metric {
    category = "Transaction"
    enabled  = true
  }

  metric {
    category = "Capacity"
    enabled  = true
  }
}

# Outputs
output "datalake_storage_account_id" {
  value       = azurerm_storage_account.datalake.id
  description = "Data Lake storage account ID"
}

output "datalake_storage_account_name" {
  value       = azurerm_storage_account.datalake.name
  description = "Data Lake storage account name"
}

output "datalake_primary_blob_endpoint" {
  value       = azurerm_storage_account.datalake.primary_blob_endpoint
  description = "Data Lake primary blob endpoint"
}

output "datalake_primary_dfs_endpoint" {
  value       = azurerm_storage_account.datalake.primary_dfs_endpoint
  description = "Data Lake primary DFS endpoint"
}

output "general_storage_account_id" {
  value       = azurerm_storage_account.general.id
  description = "General storage account ID"
}

output "general_storage_account_name" {
  value       = azurerm_storage_account.general.name
  description = "General storage account name"
}

output "vnet_id" {
  value       = azurerm_virtual_network.main.id
  description = "Virtual network ID"
}

output "vnet_name" {
  value       = azurerm_virtual_network.main.name
  description = "Virtual network name"
}
