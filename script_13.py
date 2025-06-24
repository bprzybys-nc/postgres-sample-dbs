# Create comprehensive deployment guide
deployment_guide = """# Database Decommissioning Test Scenarios - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the enhanced postgres-sample-dbs repository with database decommissioning test scenarios. The implementation creates realistic enterprise patterns for testing automated database decommissioning workflows.

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/bprzybys-nc/postgres-sample-dbs.git
cd postgres-sample-dbs

# 2. Validate scenario implementation
python test_scenarios_validation.py

# 3. Deploy scenarios (choose environment)
./scripts/deploy-scenarios.sh dev
```

## Repository Structure

```
postgres-sample-dbs-enhanced/
├── terraform/
│   ├── environments/
│   │   ├── dev/databases.tf           # Config-Only scenarios
│   │   └── prod/critical_databases.tf # Logic-Heavy scenarios
│   └── modules/database/              # Reusable database module
├── src/
│   ├── config/database_connections.py # Mixed scenario configs
│   ├── services/database_service.py   # Service layer (Mixed)
│   ├── business/                      # Critical business logic
│   └── analytics/                     # Revenue analytics
├── helm-charts/                       # Kubernetes deployments
├── monitoring/database-monitors/      # Datadog configurations
├── docs/database-ownership.md         # Owner documentation
└── test_scenarios_validation.py      # Validation script
```

## Deployment Prerequisites

### Required Tools
- **Terraform** >= 1.5.0
- **Azure CLI** >= 2.40.0
- **Helm** >= 3.12.0
- **Docker** >= 20.10.0
- **Python** >= 3.8.0

### Azure Requirements
- Azure subscription with Database Administrator role
- Resource group creation permissions
- Network configuration permissions
- PostgreSQL Flexible Server quota availability

### Environment Variables
```bash
# Azure Configuration
export ARM_CLIENT_ID="your-client-id"
export ARM_CLIENT_SECRET="your-client-secret"
export ARM_SUBSCRIPTION_ID="your-subscription-id"
export ARM_TENANT_ID="your-tenant-id"

# Database Passwords (generate secure passwords)
export DB_ADMIN_PASSWORD="$(openssl rand -base64 32)"
export POSTGRES_PASSWORD="$(openssl rand -base64 32)"

# Monitoring Configuration
export DATADOG_API_KEY="your-datadog-api-key"
export DATADOG_APP_KEY="your-datadog-app-key"
```

## Scenario-Specific Deployment

### 1. Config-Only Scenarios (LOW Risk)
Deploy databases with infrastructure configurations only.

**Databases:** periodic_table, world_happiness, titanic

```bash
# Deploy development environment
cd terraform/environments/dev
terraform init
terraform plan -var="admin_password=${DB_ADMIN_PASSWORD}"
terraform apply -auto-approve

# Verify deployment
az postgres flexible-server list --resource-group rg-databases-dev
```

**Expected Infrastructure:**
- Azure PostgreSQL Flexible Servers (B_Standard_B1ms)
- Virtual network with delegated subnet
- Private DNS zone configuration
- Basic monitoring setup

### 2. Mixed Scenarios (MEDIUM Risk)
Deploy with service layer configurations.

**Databases:** pagila, chinook, netflix

```bash
# Deploy staging environment with mixed scenarios
terraform -chdir=terraform/environments/staging init
terraform -chdir=terraform/environments/staging apply \
  -var="environment=staging" \
  -var="admin_password=${DB_ADMIN_PASSWORD}"

# Deploy service layer
docker-compose -f docker-compose.staging.yml up -d

# Test service connections
python -c "
from src.services.database_service import MixedScenarioServiceFactory
import asyncio
asyncio.run(MixedScenarioServiceFactory.health_check_all())
"
```

**Expected Infrastructure:**
- Medium-performance PostgreSQL servers
- Service layer containers
- Connection pooling configuration
- Enhanced monitoring

### 3. Logic-Heavy Scenarios (CRITICAL)
Deploy production-grade critical systems.

**Databases:** employees, lego, postgres_air

```bash
# Deploy production environment (requires approval)
cd terraform/environments/prod
terraform init
terraform plan -var="admin_password=${DB_ADMIN_PASSWORD}"

# IMPORTANT: Review plan before applying
terraform apply

# Deploy business applications
kubectl apply -f k8s/critical-systems/
helm upgrade --install employees-system helm-charts/employees/
helm upgrade --install lego-analytics helm-charts/lego/
helm upgrade --install postgres-air helm-charts/postgres_air/
```

**Expected Infrastructure:**
- High-performance PostgreSQL servers (GP_Standard_D4s_v3+)
- High availability with read replicas
- Complex business logic applications
- Comprehensive monitoring and alerting

## Environment-Specific Configurations

### Development Environment
```bash
# Minimal resources for testing
export ENVIRONMENT="dev"
export POSTGRES_SKU="B_Standard_B1ms"
export STORAGE_SIZE="20Gi"
export BACKUP_ENABLED="false"
```

### Staging Environment
```bash
# Medium resources for integration testing
export ENVIRONMENT="staging"
export POSTGRES_SKU="GP_Standard_D2s_v3"
export STORAGE_SIZE="50Gi"
export BACKUP_ENABLED="true"
```

### Production Environment
```bash
# Full resources for critical systems
export ENVIRONMENT="prod"
export POSTGRES_SKU="GP_Standard_D4s_v3"
export STORAGE_SIZE="100Gi"
export BACKUP_ENABLED="true"
export HIGH_AVAILABILITY="true"
```

## Monitoring Deployment

### Datadog Integration
```bash
# Deploy monitoring configurations
for db in periodic_table world_happiness titanic pagila chinook netflix employees lego postgres_air; do
  kubectl apply -f monitoring/database-monitors/${db}_monitor.yaml
done

# Create Datadog dashboards
curl -X POST "https://api.datadoghq.com/api/v1/dashboard" \\
  -H "Content-Type: application/json" \\
  -H "DD-API-KEY: ${DATADOG_API_KEY}" \\
  -H "DD-APPLICATION-KEY: ${DATADOG_APP_KEY}" \\
  -d @monitoring/dashboards/database-decommissioning-dashboard.json
```

### Alert Configuration
```bash
# Configure 30+ day connection alerts
python scripts/setup-monitoring.py \\
  --environment production \\
  --threshold-days 30 \\
  --notification-channels "#database-team,database-oncall@company.com"
```

## Validation and Testing

### Scenario Validation
```bash
# Run comprehensive validation
python test_scenarios_validation.py

# Check specific scenario
python test_scenarios_validation.py --database employees --scenario logic_heavy
```

### Connection Testing
```bash
# Test config-only databases (should have no app connections)
python scripts/test-connections.py --scenario config_only

# Test mixed scenarios (should have service layer only)
python scripts/test-connections.py --scenario mixed

# Test logic-heavy scenarios (should have business logic)
python scripts/test-connections.py --scenario logic_heavy
```

### Decommissioning Workflow Testing
```bash
# Simulate unused database detection
python scripts/simulate-unused-database.py --database periodic_table --days 35

# Test alert generation
python scripts/test-alerts.py --database world_happiness

# Test GitHub issue creation
python scripts/test-github-integration.py --database titanic
```

## Health Checks and Monitoring

### Database Health
```bash
# Check all database health
kubectl get pods -l app=postgresql -A

# Check specific database
az postgres flexible-server show \\
  --resource-group rg-databases-dev \\
  --name psql-periodic-table-dev
```

### Application Health
```bash
# Check service layer health
curl -f http://localhost:8080/health/pagila
curl -f http://localhost:8080/health/chinook
curl -f http://localhost:8080/health/netflix

# Check business logic health
kubectl logs -l app=employees-payroll
kubectl logs -l app=lego-analytics
```

### Monitoring Health
```bash
# Check Datadog metrics
curl -G "https://api.datadoghq.com/api/v1/query" \\
  -H "DD-API-KEY: ${DATADOG_API_KEY}" \\
  -H "DD-APPLICATION-KEY: ${DATADOG_APP_KEY}" \\
  -d "query=avg:postgresql.connections.active{*}"
```

## Troubleshooting

### Common Issues

#### 1. Terraform Deployment Failures
```bash
# Check Azure permissions
az account show
az role assignment list --assignee $(az account show --query user.name -o tsv)

# Validate resource quotas
az postgres flexible-server list-skus --location eastus

# Debug Terraform
export TF_LOG=DEBUG
terraform apply
```

#### 2. Database Connection Issues
```bash
# Check network connectivity
az postgres flexible-server list --resource-group rg-databases-dev

# Test direct connection
psql "postgresql://dbadmin@psql-periodic-table-dev.postgres.database.azure.com:5432/periodic_table?sslmode=require"

# Check firewall rules
az postgres flexible-server firewall-rule list \\
  --resource-group rg-databases-dev \\
  --name psql-periodic-table-dev
```

#### 3. Application Deployment Issues
```bash
# Check container logs
docker logs postgres-sample-dbs_service_1

# Check Kubernetes deployments
kubectl describe deployment employees-payroll
kubectl get events --sort-by=.metadata.creationTimestamp

# Check service endpoints
kubectl get endpoints -A | grep postgres
```

#### 4. Monitoring Issues
```bash
# Check Datadog agent
kubectl logs -l app=datadog-agent -n monitoring

# Validate metrics
kubectl port-forward svc/postgres-exporter 9187:9187
curl http://localhost:9187/metrics | grep postgres
```

## Security Considerations

### Network Security
- All databases deployed in private subnets
- Network security groups restrict access
- SSL/TLS encryption enforced
- Private DNS zones for internal resolution

### Access Control
- Azure RBAC for infrastructure management
- Database-level authentication required
- Service accounts with minimal permissions
- Regular credential rotation

### Data Protection
- Encryption at rest enabled
- Backup encryption configured
- Audit logging enabled
- Compliance monitoring active

## Backup and Recovery

### Automated Backups
```bash
# Check backup status
az postgres flexible-server backup list \\
  --resource-group rg-databases-prod \\
  --name psql-employees-prod

# Restore from backup
az postgres flexible-server restore \\
  --resource-group rg-databases-prod \\
  --name psql-employees-restored \\
  --source-server psql-employees-prod \\
  --restore-time "2025-06-24T10:00:00Z"
```

### Manual Backup
```bash
# Create manual backup
pg_dump "postgresql://dbadmin@psql-lego-prod.postgres.database.azure.com:5432/lego?sslmode=require" \\
  --file=lego_backup_$(date +%Y%m%d).sql
```

## Cleanup and Decommissioning

### Scenario Testing Cleanup
```bash
# Remove test scenarios (be careful!)
terraform -chdir=terraform/environments/dev destroy
terraform -chdir=terraform/environments/staging destroy

# Remove monitoring
kubectl delete -f monitoring/database-monitors/
```

### Selective Removal
```bash
# Remove specific database (example)
terraform -chdir=terraform/environments/dev destroy \\
  -target=azurerm_postgresql_flexible_server.periodic_table
```

## Support and Contacts

### Database Team
- **Email:** database-team@company.com
- **Slack:** #database-team
- **On-call:** database-oncall@company.com

### Emergency Contacts
- **Critical Issues:** cto@company.com
- **Security Incidents:** security-team@company.com
- **Compliance Issues:** compliance@company.com

---

**Document Version:** 1.0  
**Last Updated:** June 24, 2025  
**Author:** Database Team  
**Review Date:** December 24, 2025
"""

# Save the deployment guide
with open("deployment_guide.md", "w") as f:
    f.write(deployment_guide)

print("✅ Created comprehensive deployment guide")
print("File: docs/deployment-guide.md")
print("Contains: Step-by-step deployment instructions for all scenarios")
print("Features: Environment configs, troubleshooting, security, monitoring")
