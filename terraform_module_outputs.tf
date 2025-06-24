# terraform/modules/database/outputs.tf
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
