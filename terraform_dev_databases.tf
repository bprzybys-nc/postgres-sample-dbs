# terraform/environments/dev/databases.tf
# Config-Only Database Scenarios for Development Environment
# These databases should only be referenced in infrastructure configurations

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

# Resource Group for Development Databases
resource "azurerm_resource_group" "dev_databases" {
  name     = "rg-databases-dev"
  location = "East US"

  tags = {
    Environment = "Development"
    Purpose     = "Database Testing"
    Owner       = "DevOps Team"
    LastUsed    = "2024-03-15"  # Indicates potential decommissioning candidate
    Criticality = "LOW"
    Project     = "Database Decommissioning Test"
  }
}

# Random password for database administrator
resource "random_password" "db_admin_password" {
  length  = 16
  special = true
}

# Config-Only Scenario: Periodic Table Database
resource "azurerm_postgresql_flexible_server" "periodic_table" {
  name                   = "psql-periodic-table-dev"
  resource_group_name    = azurerm_resource_group.dev_databases.name
  location              = azurerm_resource_group.dev_databases.location
  version               = "14"
  delegated_subnet_id   = azurerm_subnet.database_subnet.id
  private_dns_zone_id   = azurerm_private_dns_zone.database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.db_admin_password.result

  storage_mb = 32768
  sku_name   = "B_Standard_B1ms"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  tags = {
    Environment = "Development"
    Purpose     = "Config-Only Testing"
    Owner       = "chemistry-team@company.com"
    LastUsed    = "2024-02-20"  # 30+ days ago
    Criticality = "LOW"
    Scenario    = "CONFIG_ONLY"
    DataSize    = "Small"
  }

  depends_on = [azurerm_private_dns_zone_virtual_network_link.database_dns_link]
}

resource "azurerm_postgresql_flexible_server_database" "periodic_table_db" {
  name      = "periodic_table"
  server_id = azurerm_postgresql_flexible_server.periodic_table.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Config-Only Scenario: World Happiness Database
resource "azurerm_postgresql_flexible_server" "world_happiness" {
  name                   = "psql-world-happiness-dev"
  resource_group_name    = azurerm_resource_group.dev_databases.name
  location              = azurerm_resource_group.dev_databases.location
  version               = "14"
  delegated_subnet_id   = azurerm_subnet.database_subnet.id
  private_dns_zone_id   = azurerm_private_dns_zone.database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.db_admin_password.result

  storage_mb = 32768
  sku_name   = "B_Standard_B1ms"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  tags = {
    Environment = "Development"
    Purpose     = "Config-Only Testing"
    Owner       = "analytics-team@company.com"
    LastUsed    = "2024-01-30"  # 30+ days ago
    Criticality = "LOW"
    Scenario    = "CONFIG_ONLY"
    DataSize    = "Small"
  }

  depends_on = [azurerm_private_dns_zone_virtual_network_link.database_dns_link]
}

resource "azurerm_postgresql_flexible_server_database" "world_happiness_db" {
  name      = "world_happiness"
  server_id = azurerm_postgresql_flexible_server.world_happiness.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Config-Only Scenario: Titanic Database
resource "azurerm_postgresql_flexible_server" "titanic" {
  name                   = "psql-titanic-dev"
  resource_group_name    = azurerm_resource_group.dev_databases.name
  location              = azurerm_resource_group.dev_databases.location
  version               = "14"
  delegated_subnet_id   = azurerm_subnet.database_subnet.id
  private_dns_zone_id   = azurerm_private_dns_zone.database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.db_admin_password.result

  storage_mb = 32768
  sku_name   = "B_Standard_B1ms"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  tags = {
    Environment = "Development"
    Purpose     = "Config-Only Testing"
    Owner       = "data-science-team@company.com"
    LastUsed    = "2024-02-10"  # 30+ days ago
    Criticality = "LOW"
    Scenario    = "CONFIG_ONLY"
    DataSize    = "Small"
  }

  depends_on = [azurerm_private_dns_zone_virtual_network_link.database_dns_link]
}

resource "azurerm_postgresql_flexible_server_database" "titanic_db" {
  name      = "titanic"
  server_id = azurerm_postgresql_flexible_server.titanic.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Network Infrastructure for Databases
resource "azurerm_virtual_network" "database_vnet" {
  name                = "vnet-databases-dev"
  location            = azurerm_resource_group.dev_databases.location
  resource_group_name = azurerm_resource_group.dev_databases.name
  address_space       = ["10.0.0.0/16"]

  tags = {
    Environment = "Development"
    Purpose     = "Database Network"
  }
}

resource "azurerm_subnet" "database_subnet" {
  name                 = "snet-databases"
  resource_group_name  = azurerm_resource_group.dev_databases.name
  virtual_network_name = azurerm_virtual_network.database_vnet.name
  address_prefixes     = ["10.0.2.0/24"]
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

resource "azurerm_private_dns_zone" "database_dns" {
  name                = "postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.dev_databases.name

  tags = {
    Environment = "Development"
  }
}

resource "azurerm_private_dns_zone_virtual_network_link" "database_dns_link" {
  name                  = "postgres-dns-link"
  private_dns_zone_name = azurerm_private_dns_zone.database_dns.name
  virtual_network_id    = azurerm_virtual_network.database_vnet.id
  resource_group_name   = azurerm_resource_group.dev_databases.name

  tags = {
    Environment = "Development"
  }
}

# Output connection strings for monitoring and testing
output "periodic_table_connection_string" {
  value = "postgresql://${azurerm_postgresql_flexible_server.periodic_table.administrator_login}@${azurerm_postgresql_flexible_server.periodic_table.fqdn}:5432/periodic_table"
  sensitive = false
}

output "world_happiness_connection_string" {
  value = "postgresql://${azurerm_postgresql_flexible_server.world_happiness.administrator_login}@${azurerm_postgresql_flexible_server.world_happiness.fqdn}:5432/world_happiness"
  sensitive = false
}

output "titanic_connection_string" {
  value = "postgresql://${azurerm_postgresql_flexible_server.titanic.administrator_login}@${azurerm_postgresql_flexible_server.titanic.fqdn}:5432/titanic"
  sensitive = false
}
