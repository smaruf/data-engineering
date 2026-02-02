# General Variables
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "msstack"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "Data Engineering Team"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "Engineering"
}

# Network Variables
variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_prefixes" {
  description = "Subnet prefixes"
  type = object({
    data     = string
    compute  = string
    fabric   = string
    synapse  = string
  })
  default = {
    data    = "10.0.1.0/24"
    compute = "10.0.2.0/24"
    fabric  = "10.0.3.0/24"
    synapse = "10.0.4.0/24"
  }
}

variable "allowed_ip_ranges" {
  description = "List of allowed IP ranges for network access"
  type        = list(string)
  default     = []
}

# Storage Variables
variable "storage_account_tier" {
  description = "Storage account tier"
  type        = string
  default     = "Standard"
}

variable "storage_replication_type" {
  description = "Storage account replication type"
  type        = string
  default     = "LRS"
  validation {
    condition     = contains(["LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"], var.storage_replication_type)
    error_message = "Must be a valid replication type."
  }
}

variable "enable_hierarchical_namespace" {
  description = "Enable Data Lake Gen2"
  type        = bool
  default     = true
}

variable "data_lake_containers" {
  description = "List of Data Lake containers to create"
  type        = list(string)
  default = [
    "raw",
    "bronze",
    "silver",
    "gold",
    "archive"
  ]
}

# Synapse Variables
variable "enable_synapse" {
  description = "Enable Azure Synapse Analytics"
  type        = bool
  default     = true
}

variable "synapse_sql_admin_username" {
  description = "Synapse SQL admin username"
  type        = string
  default     = "sqladmin"
}

variable "synapse_sql_admin_password" {
  description = "Synapse SQL admin password"
  type        = string
  sensitive   = true
  default     = null
}

variable "synapse_spark_version" {
  description = "Spark version for Synapse"
  type        = string
  default     = "3.4"
}

variable "synapse_spark_node_size" {
  description = "Spark pool node size"
  type        = string
  default     = "Small"
  validation {
    condition     = contains(["Small", "Medium", "Large", "XLarge", "XXLarge"], var.synapse_spark_node_size)
    error_message = "Must be a valid node size."
  }
}

variable "synapse_spark_node_count" {
  description = "Number of Spark pool nodes"
  type        = number
  default     = 3
}

variable "synapse_spark_autoscale_enabled" {
  description = "Enable Spark pool autoscaling"
  type        = bool
  default     = true
}

variable "synapse_spark_min_nodes" {
  description = "Minimum number of Spark nodes"
  type        = number
  default     = 3
}

variable "synapse_spark_max_nodes" {
  description = "Maximum number of Spark nodes"
  type        = number
  default     = 10
}

# Fabric Variables
variable "enable_fabric" {
  description = "Enable Microsoft Fabric capacity"
  type        = bool
  default     = false
}

variable "fabric_capacity_sku" {
  description = "Fabric capacity SKU"
  type        = string
  default     = "F2"
  validation {
    condition     = can(regex("^F[2468]$|^F16$|^F32$|^F64$", var.fabric_capacity_sku))
    error_message = "Must be a valid Fabric SKU (F2, F4, F8, F16, F32, F64)."
  }
}

variable "fabric_capacity_admins" {
  description = "List of Fabric capacity admin object IDs"
  type        = list(string)
  default     = []
}

# Database Variables
variable "enable_sql_database" {
  description = "Enable Azure SQL Database"
  type        = bool
  default     = false
}

variable "sql_database_sku" {
  description = "SQL Database SKU"
  type        = string
  default     = "S0"
}

variable "sql_database_max_size_gb" {
  description = "SQL Database max size in GB"
  type        = number
  default     = 250
}

# Monitoring Variables
variable "log_analytics_sku" {
  description = "Log Analytics workspace SKU"
  type        = string
  default     = "PerGB2018"
}

variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 30
}

variable "enable_diagnostic_settings" {
  description = "Enable diagnostic settings for resources"
  type        = bool
  default     = true
}

# Security Variables
variable "enable_private_endpoints" {
  description = "Enable private endpoints for resources"
  type        = bool
  default     = false
}

variable "enable_managed_identity" {
  description = "Enable managed identity for resources"
  type        = bool
  default     = true
}

# Backup Variables
variable "enable_backup" {
  description = "Enable backup for resources"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

# Data Factory Variables
variable "enable_data_factory" {
  description = "Enable Azure Data Factory"
  type        = bool
  default     = true
}

variable "adf_github_integration" {
  description = "Enable GitHub integration for ADF"
  type        = bool
  default     = false
}

variable "adf_github_account" {
  description = "GitHub account name for ADF"
  type        = string
  default     = ""
}

variable "adf_github_repo" {
  description = "GitHub repository name for ADF"
  type        = string
  default     = ""
}

# Databricks Variables
variable "enable_databricks" {
  description = "Enable Azure Databricks"
  type        = bool
  default     = false
}

variable "databricks_sku" {
  description = "Databricks workspace SKU"
  type        = string
  default     = "standard"
  validation {
    condition     = contains(["standard", "premium"], var.databricks_sku)
    error_message = "Must be standard or premium."
  }
}

# Event Hub Variables
variable "enable_event_hub" {
  description = "Enable Event Hub namespace"
  type        = bool
  default     = false
}

variable "event_hub_sku" {
  description = "Event Hub namespace SKU"
  type        = string
  default     = "Standard"
  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.event_hub_sku)
    error_message = "Must be Basic, Standard, or Premium."
  }
}

variable "event_hub_capacity" {
  description = "Event Hub throughput units"
  type        = number
  default     = 1
}

# Stream Analytics Variables
variable "enable_stream_analytics" {
  description = "Enable Stream Analytics job"
  type        = bool
  default     = false
}

variable "stream_analytics_units" {
  description = "Stream Analytics streaming units"
  type        = number
  default     = 3
}
