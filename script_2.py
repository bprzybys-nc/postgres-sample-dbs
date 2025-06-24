# Create the reusable database module
terraform_module_config = """# terraform/modules/database/main.tf
# Reusable PostgreSQL Database Module for Azure

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

variable "database_name" {
  description = "Name of the PostgreSQL database"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure location"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "criticality" {
  description = "Database criticality level (LOW, MEDIUM, CRITICAL)"
  type        = string
  default     = "LOW"
}

variable "scenario_type" {
  description = "Scenario type (CONFIG_ONLY, MIXED, LOGIC_HEAVY)"
  type        = string
}

variable "owner_email" {
  description = "Owner team email"
  type        = string
}

variable "last_used_date" {
  description = "Last used date (YYYY-MM-DD)"
  type        = string
}

variable "storage_mb" {
  description = "Storage size in MB"
  type        = number
  default     = 32768
}

variable "sku_name" {
  description = "SKU name for the database"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "backup_retention_days" {
  description = "Backup retention in days"
  type        = number
  default     = 7
}

variable "high_availability" {
  description = "Enable high availability"
  type        = bool
  default     = false
}

variable "delegated_subnet_id" {
  description = "Delegated subnet ID"
  type        = string
}

variable "private_dns_zone_id" {
  description = "Private DNS zone ID"
  type        = string
}

variable "administrator_login" {
  description = "Administrator login"
  type        = string
  default     = "dbadmin"
}

variable "administrator_password" {
  description = "Administrator password"
  type        = string
  sensitive   = true
}

variable "additional_tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "database" {
  name                   = "psql-${var.database_name}-${var.environment}"
  resource_group_name    = var.resource_group_name
  location              = var.location
  version               = "14"
  delegated_subnet_id   = var.delegated_subnet_id
  private_dns_zone_id   = var.private_dns_zone_id
  administrator_login    = var.administrator_login
  administrator_password = var.administrator_password

  storage_mb = var.storage_mb
  sku_name   = var.sku_name

  backup_retention_days        = var.backup_retention_days
  geo_redundant_backup_enabled = var.criticality == "CRITICAL" ? true : false
  high_availability_enabled    = var.high_availability

  tags = merge({
    Environment       = var.environment
    Criticality      = var.criticality
    Scenario         = var.scenario_type
    Owner            = var.owner_email
    LastUsed         = var.last_used_date
    ManagedBy        = "Terraform"
    DatabaseType     = "PostgreSQL"
    DecommissioningCandidate = var.last_used_date < "2025-05-01" ? "true" : "false"
  }, var.additional_tags)
}

# Database within the server
resource "azurerm_postgresql_flexible_server_database" "database" {
  name      = var.database_name
  server_id = azurerm_postgresql_flexible_server.database.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Outputs
output "server_id" {
  value = azurerm_postgresql_flexible_server.database.id
}

output "server_fqdn" {
  value = azurerm_postgresql_flexible_server.database.fqdn
}

output "database_name" {
  value = azurerm_postgresql_flexible_server_database.database.name
}

output "connection_string" {
  value = "postgresql://${var.administrator_login}@${azurerm_postgresql_flexible_server.database.fqdn}:5432/${var.database_name}"
  sensitive = var.environment == "prod"
}

output "server_tags" {
  value = azurerm_postgresql_flexible_server.database.tags
}
"""

# Create the module variables file
terraform_module_variables = """# terraform/modules/database/variables.tf
# Variables for the reusable database module

variable "database_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9_]*$", var.database_name))
    error_message = "Database name must start with a letter and contain only lowercase letters, numbers, and underscores."
  }
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure location"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "criticality" {
  description = "Database criticality level"
  type        = string
  default     = "LOW"
  validation {
    condition     = contains(["LOW", "MEDIUM", "CRITICAL"], var.criticality)
    error_message = "Criticality must be one of: LOW, MEDIUM, CRITICAL."
  }
}

variable "scenario_type" {
  description = "Scenario type for decommissioning testing"
  type        = string
  validation {
    condition     = contains(["CONFIG_ONLY", "MIXED", "LOGIC_HEAVY"], var.scenario_type)
    error_message = "Scenario type must be one of: CONFIG_ONLY, MIXED, LOGIC_HEAVY."
  }
}

variable "owner_email" {
  description = "Owner team email address"
  type        = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.owner_email))
    error_message = "Owner email must be a valid email address."
  }
}

variable "last_used_date" {
  description = "Last used date in YYYY-MM-DD format"
  type        = string
  validation {
    condition     = can(regex("^\\d{4}-\\d{2}-\\d{2}$", var.last_used_date))
    error_message = "Last used date must be in YYYY-MM-DD format."
  }
}
"""

# Create the module outputs file
terraform_module_outputs = """# terraform/modules/database/outputs.tf
# Outputs for the reusable database module

output "server_id" {
  description = "ID of the PostgreSQL server"
  value       = azurerm_postgresql_flexible_server.database.id
}

output "server_fqdn" {
  description = "FQDN of the PostgreSQL server"
  value       = azurerm_postgresql_flexible_server.database.fqdn
}

output "database_name" {
  description = "Name of the database"
  value       = azurerm_postgresql_flexible_server_database.database.name
}

output "connection_string" {
  description = "Connection string for the database"
  value       = "postgresql://${var.administrator_login}@${azurerm_postgresql_flexible_server.database.fqdn}:5432/${var.database_name}"
  sensitive   = var.environment == "prod"
}

output "server_tags" {
  description = "Tags applied to the server"
  value       = azurerm_postgresql_flexible_server.database.tags
}

output "decommissioning_info" {
  description = "Information relevant for decommissioning decisions"
  value = {
    scenario_type = var.scenario_type
    criticality   = var.criticality
    owner_email   = var.owner_email
    last_used     = var.last_used_date
    environment   = var.environment
    requires_manual_review = var.scenario_type == "LOGIC_HEAVY" ? true : false
  }
}
"""

# Save the module files
with open("terraform_module_main.tf", "w") as f:
    f.write(terraform_module_config)

with open("terraform_module_variables.tf", "w") as f:
    f.write(terraform_module_variables)

with open("terraform_module_outputs.tf", "w") as f:
    f.write(terraform_module_outputs)

print("✅ Created reusable Terraform database module")
print("Files created:")
print("  - terraform/modules/database/main.tf")
print("  - terraform/modules/database/variables.tf")
print("  - terraform/modules/database/outputs.tf")
print("Features: Validation, decommissioning flags, environment-specific configs")
