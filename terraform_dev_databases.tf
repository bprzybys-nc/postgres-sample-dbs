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


resource "azurerm_postgresql_flexible_server" "world_happiness" {
  name                   = "psql-world-happiness-dev"
  resource_group_name    = azurerm_resource_group.dev_databases.name
  location              = azurerm_resource_group.dev_databases.location
  version                = "13"
  sku_name               = "Standard_D2s_v3"
  storage_mb             = 32768 # 32 GB
  backup_retention_days  = 7
  geo_redundant_backup_enabled = false
  zone                   = "1"
  delegated_subnet_id    = azurerm_subnet.database_subnet.id
  private_dns_zone_id    = azurerm_private_dns_zone.database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.db_admin_password.result
  public_network_access_enabled = false

  tags = {
    DatabaseName = "world_happiness"
    Scenario     = "CONFIG_ONLY"
    Criticality  = "LOW"
  }
}

resource "azurerm_postgresql_flexible_server_database" "world_happiness_db" {
  name      = "world_happiness"
  server_id = azurerm_postgresql_flexible_server.world_happiness.id
  charset   = "UTF8"
  collation = "en_US.UTF8"
}

resource "azurerm_postgresql_flexible_server" "titanic" {
  name                   = "psql-titanic-dev"
  resource_group_name    = azurerm_resource_group.dev_databases.name
  location              = azurerm_resource_group.dev_databases.location
  version                = "13"
  sku_name               = "Standard_D2s_v3"
  storage_mb             = 32768 # 32 GB
  backup_retention_days  = 7
  geo_redundant_backup_enabled = false
  zone                   = "1"
  delegated_subnet_id    = azurerm_subnet.database_subnet.id
  private_dns_zone_id    = azurerm_private_dns_zone.database_dns.id
  administrator_login    = "dbadmin"
  administrator_password = random_password.db_admin_password.result
  public_network_access_enabled = false

  tags = {
    DatabaseName = "titanic"
    Scenario     = "CONFIG_ONLY"
    Criticality  = "LOW"
  }
}

resource "azurerm_postgresql_flexible_server_database" "titanic_db" {
  name      = "titanic"
  server_id = azurerm_postgresql_flexible_server.titanic.id
  charset   = "UTF8"
  collation = "en_US.UTF8"
}

# Virtual Network and Subnet for Private Endpoint
resource "azurerm_virtual_network" "database_vnet" {
  name                = "vnet-databases-dev"
  location            = azurerm_resource_group.dev_databases.location
  resource_group_name = azurerm_resource_group.dev_databases.name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "database_subnet" {
  name                 = "subnet-databases-dev"
  resource_group_name  = azurerm_resource_group.dev_databases.name
  virtual_network_name = azurerm_virtual_network.database_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
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


output "world_happiness_connection_string" {
  value = "postgresql://${azurerm_postgresql_flexible_server.world_happiness.administrator_login}@${azurerm_postgresql_flexible_server.world_happiness.fqdn}:5432/world_happiness"
  sensitive = false
}

output "titanic_connection_string" {
  value = "postgresql://${azurerm_postgresql_flexible_server.titanic.administrator_login}@${azurerm_postgresql_flexible_server.titanic.fqdn}:5432/titanic"
  sensitive = false
}
