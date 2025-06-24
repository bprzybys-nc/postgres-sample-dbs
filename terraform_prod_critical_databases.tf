# terraform/environments/prod/critical_databases.tf
# Logic-Heavy Database Scenarios for Production Environment
# These databases have complex business logic and require manual review for decommissioning

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.1"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group for Production Critical Databases
resource "azurerm_resource_group" "prod_critical_databases" {
  name     = "rg-databases-prod-critical"
  location = "East US"

  tags = {
    Environment = "Production"
    Purpose     = "Critical Business Operations"
    Owner       = "Database Administration Team"
    LastUsed    = "2025-06-24"  # Current/Recent usage
    Criticality = "CRITICAL"
    Project     = "Core Business Systems"
    ComplianceLevel = "SOX"
  }
}

# Random password for database administrator
resource "random_password" "prod_db_admin_password" {
  length  = 24
  special = true
}

# Logic-Heavy Scenario: Employees Database (Payroll System)
resource "azurerm_postgresql_flexible_server" "employees" {
  name                   = "psql-employees-prod"
  resource_group_name    = azurerm_resource_group.prod_critical_databases.name
  location              = azurerm_resource_group.prod_critical_databases.location
  version               = "14"
  delegated_subnet_id   = azurerm_subnet.prod_database_subnet.id
  private_dns_zone_id   = azurerm_private_dns_zone.prod_database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.prod_db_admin_password.result

  storage_mb = 1048576  # 1TB for large dataset
  sku_name   = "GP_Standard_D4s_v3"  # High performance

  backup_retention_days        = 35
  geo_redundant_backup_enabled = true
  high_availability_enabled    = true

  tags = {
    Environment = "Production"
    Purpose     = "Payroll & HR System"
    Owner       = "hr-team@company.com"
    LastUsed    = "2025-06-24"  # Active usage
    Criticality = "CRITICAL"
    Scenario    = "LOGIC_HEAVY"
    DataSize    = "Large"
    BusinessImpact = "Multi-million dollar payroll operations"
    RequiresManualReview = "true"
    ComplianceRequirement = "SOX, GDPR"
  }

  depends_on = [azurerm_private_dns_zone_virtual_network_link.prod_database_dns_link]
}

resource "azurerm_postgresql_flexible_server_database" "employees_db" {
  name      = "employees"
  server_id = azurerm_postgresql_flexible_server.employees.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Logic-Heavy Scenario: Lego Database (Business Intelligence)
resource "azurerm_postgresql_flexible_server" "lego" {
  name                   = "psql-lego-prod"
  resource_group_name    = azurerm_resource_group.prod_critical_databases.name
  location              = azurerm_resource_group.prod_critical_databases.location
  version               = "14"
  delegated_subnet_id   = azurerm_subnet.prod_database_subnet.id
  private_dns_zone_id   = azurerm_private_dns_zone.prod_database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.prod_db_admin_password.result

  storage_mb = 524288  # 512GB for analytics
  sku_name   = "GP_Standard_D8s_v3"  # High performance for analytics

  backup_retention_days        = 35
  geo_redundant_backup_enabled = true
  high_availability_enabled    = true

  tags = {
    Environment = "Production"
    Purpose     = "Revenue Analytics & Forecasting"
    Owner       = "analytics-team@company.com"
    LastUsed    = "2025-06-24"  # Active usage
    Criticality = "CRITICAL"
    Scenario    = "LOGIC_HEAVY"
    DataSize    = "Medium"
    BusinessImpact = "Executive decision support, revenue forecasting"
    RequiresManualReview = "true"
    ComplianceRequirement = "Financial reporting"
  }

  depends_on = [azurerm_private_dns_zone_virtual_network_link.prod_database_dns_link]
}

resource "azurerm_postgresql_flexible_server_database" "lego_db" {
  name      = "lego"
  server_id = azurerm_postgresql_flexible_server.lego.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Logic-Heavy Scenario: Postgres Air Database (Flight Operations)
resource "azurerm_postgresql_flexible_server" "postgres_air" {
  name                   = "psql-postgres-air-prod"
  resource_group_name    = azurerm_resource_group.prod_critical_databases.name
  location              = azurerm_resource_group.prod_critical_databases.location
  version               = "14"
  delegated_subnet_id   = azurerm_subnet.prod_database_subnet.id
  private_dns_zone_id   = azurerm_private_dns_zone.prod_database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.prod_db_admin_password.result

  storage_mb = 2097152  # 2TB for flight operations
  sku_name   = "GP_Standard_D16s_v3"  # Very high performance

  backup_retention_days        = 35
  geo_redundant_backup_enabled = true
  high_availability_enabled    = true

  tags = {
    Environment = "Production"
    Purpose     = "Flight Operations & Safety"
    Owner       = "operations-team@company.com"
    LastUsed    = "2025-06-24"  # Active usage
    Criticality = "CRITICAL"
    Scenario    = "LOGIC_HEAVY"
    DataSize    = "Very Large"
    BusinessImpact = "Flight safety, regulatory compliance"
    RequiresManualReview = "true"
    ComplianceRequirement = "FAA, EASA regulations"
    SafetyCritical = "true"
  }

  depends_on = [azurerm_private_dns_zone_virtual_network_link.prod_database_dns_link]
}

resource "azurerm_postgresql_flexible_server_database" "postgres_air_db" {
  name      = "postgres_air"
  server_id = azurerm_postgresql_flexible_server.postgres_air.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Production Network Infrastructure
resource "azurerm_virtual_network" "prod_database_vnet" {
  name                = "vnet-databases-prod"
  location            = azurerm_resource_group.prod_critical_databases.location
  resource_group_name = azurerm_resource_group.prod_critical_databases.name
  address_space       = ["10.1.0.0/16"]

  tags = {
    Environment = "Production"
    Purpose     = "Critical Database Network"
  }
}

resource "azurerm_subnet" "prod_database_subnet" {
  name                 = "snet-critical-databases"
  resource_group_name  = azurerm_resource_group.prod_critical_databases.name
  virtual_network_name = azurerm_virtual_network.prod_database_vnet.name
  address_prefixes     = ["10.1.2.0/24"]
  service_endpoints    = ["Microsoft.Storage"]

  delegation {
    name = "fs"
    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}

resource "azurerm_private_dns_zone" "prod_database_dns" {
  name                = "postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.prod_critical_databases.name

  tags = {
    Environment = "Production"
  }
}

resource "azurerm_private_dns_zone_virtual_network_link" "prod_database_dns_link" {
  name                  = "postgres-dns-link-prod"
  private_dns_zone_name = azurerm_private_dns_zone.prod_database_dns.name
  virtual_network_id    = azurerm_virtual_network.prod_database_vnet.id
  resource_group_name   = azurerm_resource_group.prod_critical_databases.name

  tags = {
    Environment = "Production"
  }
}

# Output connection strings (sensitive for production)
output "employees_connection_string" {
  value = "postgresql://${azurerm_postgresql_flexible_server.employees.administrator_login}@${azurerm_postgresql_flexible_server.employees.fqdn}:5432/employees"
  sensitive = true
}

output "lego_connection_string" {
  value = "postgresql://${azurerm_postgresql_flexible_server.lego.administrator_login}@${azurerm_postgresql_flexible_server.lego.fqdn}:5432/lego"
  sensitive = true
}

output "postgres_air_connection_string" {
  value = "postgresql://${azurerm_postgresql_flexible_server.postgres_air.administrator_login}@${azurerm_postgresql_flexible_server.postgres_air.fqdn}:5432/postgres_air"
  sensitive = true
}
