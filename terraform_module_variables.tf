# terraform/modules/database/variables.tf
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
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", var.owner_email))
    error_message = "Owner email must be a valid email address."
  }
}

variable "last_used_date" {
  description = "Last used date in YYYY-MM-DD format"
  type        = string
  validation {
    condition     = can(regex("^\d{4}-\d{2}-\d{2}$", var.last_used_date))
    error_message = "Last used date must be in YYYY-MM-DD format."
  }
}
