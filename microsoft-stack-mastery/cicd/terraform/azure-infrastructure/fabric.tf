# Microsoft Fabric Capacity
# Note: As of this writing, Fabric capacity resources in Terraform are still in preview
# This configuration uses the azurerm_fabric_capacity resource which may require provider updates

resource "azurerm_fabric_capacity" "main" {
  count               = var.enable_fabric ? 1 : 0
  name                = "${local.resource_prefix}-fabric"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  sku {
    name = var.fabric_capacity_sku
    tier = "Fabric"
  }

  administration {
    members = concat(
      [data.azurerm_client_config.current.object_id],
      var.fabric_capacity_admins
    )
  }

  tags = merge(
    local.common_tags,
    {
      Purpose = "Microsoft Fabric Capacity"
    }
  )
}

# Azure Data Factory for Fabric integration
resource "azurerm_data_factory" "fabric" {
  count                            = var.enable_fabric && var.enable_data_factory ? 1 : 0
  name                             = "${local.resource_prefix}-adf-fabric"
  location                         = azurerm_resource_group.main.location
  resource_group_name              = azurerm_resource_group.main.name
  managed_virtual_network_enabled  = var.enable_private_endpoints
  public_network_enabled           = var.environment != "prod"

  identity {
    type = "SystemAssigned"
  }

  dynamic "github_configuration" {
    for_each = var.adf_github_integration ? [1] : []
    content {
      account_name    = var.adf_github_account
      branch_name     = var.environment == "prod" ? "main" : "develop"
      git_url         = "https://github.com"
      repository_name = var.adf_github_repo
      root_folder     = "/adf"
    }
  }

  tags = merge(
    local.common_tags,
    {
      Purpose = "Data Integration for Fabric"
    }
  )
}

# ADF Linked Service to Data Lake
resource "azurerm_data_factory_linked_service_data_lake_storage_gen2" "main" {
  count               = var.enable_fabric && var.enable_data_factory ? 1 : 0
  name                = "ls_datalake"
  data_factory_id     = azurerm_data_factory.fabric[0].id
  url                 = azurerm_storage_account.datalake.primary_dfs_endpoint
  use_managed_identity = true
}

# Role assignment for ADF to access storage
resource "azurerm_role_assignment" "adf_storage_blob_contributor" {
  count                = var.enable_fabric && var.enable_data_factory ? 1 : 0
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.fabric[0].identity[0].principal_id
}

# Power BI Embedded Capacity (alternative if full Fabric not available)
resource "azurerm_powerbi_embedded" "main" {
  count               = var.enable_fabric && var.fabric_capacity_sku == "F2" ? 0 : 0 # Disabled by default
  name                = "${local.resource_prefix}-pbiembedded"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "A1"

  administrators = concat(
    [data.azurerm_client_config.current.object_id],
    var.fabric_capacity_admins
  )

  tags = merge(
    local.common_tags,
    {
      Purpose = "Power BI Embedded"
    }
  )
}

# Event Hub for Fabric Real-Time Analytics
resource "azurerm_eventhub_namespace" "fabric" {
  count               = var.enable_fabric && var.enable_event_hub ? 1 : 0
  name                = "${local.resource_prefix}-ehns-fabric"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = var.event_hub_sku
  capacity            = var.event_hub_capacity

  identity {
    type = "SystemAssigned"
  }

  tags = merge(
    local.common_tags,
    {
      Purpose = "Real-Time Data Streaming"
    }
  )
}

resource "azurerm_eventhub" "fabric_events" {
  count               = var.enable_fabric && var.enable_event_hub ? 1 : 0
  name                = "fabric-events"
  namespace_name      = azurerm_eventhub_namespace.fabric[0].name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = 4
  message_retention   = 7
}

# Stream Analytics for Fabric
resource "azurerm_stream_analytics_job" "fabric" {
  count                                  = var.enable_fabric && var.enable_stream_analytics ? 1 : 0
  name                                   = "${local.resource_prefix}-asa-fabric"
  resource_group_name                    = azurerm_resource_group.main.name
  location                               = azurerm_resource_group.main.location
  compatibility_level                    = "1.2"
  data_locale                            = "en-US"
  events_late_arrival_max_delay_in_seconds = 60
  events_out_of_order_max_delay_in_seconds = 50
  events_out_of_order_policy             = "Adjust"
  output_error_policy                    = "Drop"
  streaming_units                        = var.stream_analytics_units

  identity {
    type = "SystemAssigned"
  }

  transformation_query = <<QUERY
    SELECT
        *
    INTO
        [FabricLakehouse]
    FROM
        [EventHubInput]
  QUERY

  tags = merge(
    local.common_tags,
    {
      Purpose = "Stream Processing"
    }
  )
}

# Diagnostic settings for Fabric resources
resource "azurerm_monitor_diagnostic_setting" "fabric_adf" {
  count                      = var.enable_fabric && var.enable_data_factory && var.enable_diagnostic_settings ? 1 : 0
  name                       = "${azurerm_data_factory.fabric[0].name}-diagnostics"
  target_resource_id         = azurerm_data_factory.fabric[0].id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "ActivityRuns"
  }

  enabled_log {
    category = "PipelineRuns"
  }

  enabled_log {
    category = "TriggerRuns"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

resource "azurerm_monitor_diagnostic_setting" "fabric_eventhub" {
  count                      = var.enable_fabric && var.enable_event_hub && var.enable_diagnostic_settings ? 1 : 0
  name                       = "${azurerm_eventhub_namespace.fabric[0].name}-diagnostics"
  target_resource_id         = azurerm_eventhub_namespace.fabric[0].id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "ArchiveLogs"
  }

  enabled_log {
    category = "OperationalLogs"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

# Outputs
output "fabric_capacity_id" {
  value       = var.enable_fabric ? azurerm_fabric_capacity.main[0].id : null
  description = "Fabric capacity ID"
}

output "fabric_capacity_name" {
  value       = var.enable_fabric ? azurerm_fabric_capacity.main[0].name : null
  description = "Fabric capacity name"
}

output "adf_id" {
  value       = var.enable_fabric && var.enable_data_factory ? azurerm_data_factory.fabric[0].id : null
  description = "Azure Data Factory ID"
}

output "adf_name" {
  value       = var.enable_fabric && var.enable_data_factory ? azurerm_data_factory.fabric[0].name : null
  description = "Azure Data Factory name"
}

output "eventhub_namespace_id" {
  value       = var.enable_fabric && var.enable_event_hub ? azurerm_eventhub_namespace.fabric[0].id : null
  description = "Event Hub namespace ID"
}

output "eventhub_namespace_name" {
  value       = var.enable_fabric && var.enable_event_hub ? azurerm_eventhub_namespace.fabric[0].name : null
  description = "Event Hub namespace name"
}

output "stream_analytics_job_id" {
  value       = var.enable_fabric && var.enable_stream_analytics ? azurerm_stream_analytics_job.fabric[0].id : null
  description = "Stream Analytics job ID"
}
