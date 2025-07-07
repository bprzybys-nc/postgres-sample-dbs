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
  version                = "13"
  sku_name               = "Standard_D4s_v3"
  storage_mb             = 65536 # 64 GB
  backup_retention_days  = 35
  geo_redundant_backup_enabled = true
  zone                   = "1"
  delegated_subnet_id    = azurerm_subnet.prod_database_subnet.id
  private_dns_zone_id    = azurerm_private_dns_zone.prod_database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.prod_db_admin_password.result
  public_network_access_enabled = false

  tags = {
    DatabaseName = "employees"
    Scenario     = "LOGIC_HEAVY"
    Criticality  = "HIGH"
  }
}

resource "azurerm_postgresql_flexible_server_database" "employees_db" {
  name      = "employees"
  server_id = azurerm_postgresql_flexible_server.employees.id
  charset   = "UTF8"
  collation = "en_US.UTF8"
}

# Logic-Heavy Scenario: LEGO Database (Business Intelligence)
resource "azurerm_postgresql_flexible_server" "lego" {
  name                   = "psql-lego-prod"
  resource_group_name    = azurerm_resource_group.prod_critical_databases.name
  location              = azurerm_resource_group.prod_critical_databases.location
  version                = "13"
  sku_name               = "Standard_D4s_v3"
  storage_mb             = 65536 # 64 GB
  backup_retention_days  = 35
  geo_redundant_backup_enabled = true
  zone                   = "1"
  delegated_subnet_id    = azurerm_subnet.prod_database_subnet.id
  private_dns_zone_id    = azurerm_private_dns_zone.prod_database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.prod_db_admin_password.result
  public_network_access_enabled = false

  tags = {
    DatabaseName = "lego"
    Scenario     = "LOGIC_HEAVY"
    Criticality  = "HIGH"
  }
}

resource "azurerm_postgresql_flexible_server_database" "lego_db" {
  name      = "lego"
  server_id = azurerm_postgresql_flexible_server.lego.id
  charset   = "UTF8"
  collation = "en_US.UTF8"
}

# Logic-Heavy Scenario: Postgres Air Database (Airline Operations)
resource "azurerm_postgresql_flexible_server" "postgres_air" {
  name                   = "psql-postgres-air-prod"
  resource_group_name    = azurerm_resource_group.prod_critical_databases.name
  location              = azurerm_resource_group.prod_critical_databases.location
  version                = "13"
  sku_name               = "Standard_D4s_v3"
  storage_mb             = 65536 # 64 GB
  backup_retention_days  = 35
  geo_redundant_backup_enabled = true
  zone                   = "1"
  delegated_subnet_id    = azurerm_subnet.prod_database_subnet.id
  private_dns_zone_id    = azurerm_private_dns_zone.prod_database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.prod_db_admin_password.result
  public_network_access_enabled = false

  tags = {
    DatabaseName = "postgres_air"
    Scenario     = "LOGIC_HEAVY"
    Criticality  = "HIGH"
  }
}

resource "azurerm_postgresql_flexible_server_database" "postgres_air_db" {
  name      = "postgres_air"
  server_id = azurerm_postgresql_flexible_server.postgres_air.id
  charset   = "UTF8"
  collation = "en_US.UTF8"
}

# Virtual Network and Subnet for Private Endpoint
resource "azurerm_virtual_network" "prod_database_vnet" {
  name                = "vnet-databases-prod"
  location            = azurerm_resource_group.prod_critical_databases.location
  resource_group_name = azurerm_resource_group.prod_critical_databases.name
  address_space       = ["10.10.0.0/16"]
}

resource "azurerm_subnet" "prod_database_subnet" {
  name                 = "subnet-databases-prod"
  resource_group_name  = azurerm_resource_group.prod_critical_databases.name
  virtual_network_name = azurerm_virtual_network.prod_database_vnet.name
  address_prefixes     = ["10.10.1.0/24"]
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
