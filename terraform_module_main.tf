# terraform/modules/database/main.tf
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
