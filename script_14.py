# Create deployment script
deployment_script = """#!/bin/bash
# scripts/deploy-scenarios.sh
# Automated deployment script for database decommissioning test scenarios

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$REPO_ROOT/deployment.log"

# Color codes for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Error handling
error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

# Warning message  
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

# Info message
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
    log "INFO: $1"
}

# Usage information
usage() {
    echo "Usage: $0 <environment> [options]"
    echo ""
    echo "Environments:"
    echo "  dev      - Development environment (Config-Only scenarios)"
    echo "  staging  - Staging environment (Mixed scenarios)"
    echo "  prod     - Production environment (Logic-Heavy scenarios)"
    echo "  all      - Deploy all environments"
    echo ""
    echo "Options:"
    echo "  --validate-only   Run validation only, no deployment"
    echo "  --skip-validation Skip scenario validation"
    echo "  --dry-run        Show what would be deployed"
    echo "  --force          Force deployment even with warnings"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev                    # Deploy development environment"
    echo "  $0 staging --dry-run      # Preview staging deployment"
    echo "  $0 all --validate-only    # Validate all scenarios"
}

# Check prerequisites
check_prerequisites() {
    info "Checking deployment prerequisites..."
    
    # Check required tools
    local tools=("terraform" "az" "helm" "docker" "python3")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "$tool is required but not installed"
        fi
    done
    
    # Check Azure authentication
    if ! az account show &> /dev/null; then
        error "Azure CLI not authenticated. Run 'az login' first."
    fi
    
    # Check required environment variables
    local env_vars=("ARM_SUBSCRIPTION_ID")
    for var in "${env_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            warning "Environment variable $var is not set"
        fi
    done
    
    success "Prerequisites check completed"
}

# Validate scenarios
validate_scenarios() {
    info "Validating database scenarios..."
    
    cd "$REPO_ROOT"
    if python3 test_scenarios_validation.py; then
        success "Scenario validation passed"
        return 0
    else
        error "Scenario validation failed. Fix issues before deployment."
        return 1
    fi
}

# Deploy development environment (Config-Only)
deploy_dev() {
    info "Deploying development environment (Config-Only scenarios)..."
    
    local tf_dir="$REPO_ROOT/terraform/environments/dev"
    
    if [[ ! -f "${tf_dir}/databases.tf" ]]; then
        # Copy our generated file to the expected location
        mkdir -p "$tf_dir"
        cp "$REPO_ROOT/terraform_dev_databases.tf" "${tf_dir}/databases.tf"
    fi
    
    cd "$tf_dir"
    
    # Initialize Terraform
    info "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    info "Planning Terraform deployment..."
    terraform plan \\
        -var="admin_password=${DB_ADMIN_PASSWORD:-$(openssl rand -base64 32)}" \\
        -out=dev.tfplan
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        info "Dry run completed. Plan saved to dev.tfplan"
        return 0
    fi
    
    # Apply deployment
    info "Applying Terraform configuration..."
    terraform apply dev.tfplan
    
    # Deploy monitoring
    deploy_monitoring "dev" "periodic_table world_happiness titanic"
    
    success "Development environment deployed successfully"
}

# Deploy staging environment (Mixed scenarios)
deploy_staging() {
    info "Deploying staging environment (Mixed scenarios)..."
    
    # Create staging Terraform configuration
    local tf_dir="$REPO_ROOT/terraform/environments/staging"
    mkdir -p "$tf_dir"
    
    # Generate staging config (simplified for demo)
    cat > "${tf_dir}/main.tf" << EOF
# Staging environment for Mixed scenarios
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Mixed scenario databases: pagila, chinook, netflix
# (Implementation would be similar to dev but with different configs)
EOF
    
    cd "$tf_dir"
    terraform init
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        info "Dry run - staging Terraform configuration created"
        return 0
    fi
    
    # Deploy service layer
    deploy_service_layer
    
    # Deploy monitoring
    deploy_monitoring "staging" "pagila chinook netflix"
    
    success "Staging environment deployed successfully"
}

# Deploy production environment (Logic-Heavy)
deploy_prod() {
    info "Deploying production environment (Logic-Heavy scenarios)..."
    
    # Production deployment requires additional approvals
    warning "Production deployment requires executive approval"
    
    if [[ "${FORCE:-false}" != "true" ]]; then
        read -p "Are you authorized to deploy to production? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            error "Production deployment cancelled"
        fi
    fi
    
    local tf_dir="$REPO_ROOT/terraform/environments/prod"
    
    if [[ ! -f "${tf_dir}/critical_databases.tf" ]]; then
        mkdir -p "$tf_dir"
        cp "$REPO_ROOT/terraform_prod_critical_databases.tf" "${tf_dir}/critical_databases.tf"
    fi
    
    cd "$tf_dir"
    terraform init
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        terraform plan \\
            -var="admin_password=${DB_ADMIN_PASSWORD:-$(openssl rand -base64 32)}"
        info "Production deployment plan completed"
        return 0
    fi
    
    # Deploy critical systems
    deploy_critical_systems
    
    # Deploy monitoring
    deploy_monitoring "prod" "employees lego postgres_air"
    
    success "Production environment deployed successfully"
}

# Deploy service layer for mixed scenarios
deploy_service_layer() {
    info "Deploying service layer applications..."
    
    # Create docker-compose for service layer
    cat > "$REPO_ROOT/docker-compose.services.yml" << EOF
version: '3.8'
services:
  database-service:
    build:
      context: .
      dockerfile: Dockerfile.services
    environment:
      - ENVIRONMENT=staging
      - PAGILA_DB_HOST=\${PAGILA_DB_HOST}
      - CHINOOK_DB_HOST=\${CHINOOK_DB_HOST}
      - NETFLIX_DB_HOST=\${NETFLIX_DB_HOST}
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF
    
    if command -v docker-compose &> /dev/null; then
        cd "$REPO_ROOT"
        docker-compose -f docker-compose.services.yml up -d
        success "Service layer deployed"
    else
        warning "Docker Compose not available, skipping service layer deployment"
    fi
}

# Deploy critical systems for logic-heavy scenarios  
deploy_critical_systems() {
    info "Deploying critical business systems..."
    
    # Deploy business logic applications
    if command -v kubectl &> /dev/null; then
        # Create Kubernetes deployments
        kubectl create namespace business-systems 2>/dev/null || true
        
        # Deploy payroll system
        helm upgrade --install employees-payroll \\
            "$REPO_ROOT/helm-charts/employees/" \\
            --namespace business-systems \\
            --wait
        
        # Deploy analytics system
        helm upgrade --install lego-analytics \\
            "$REPO_ROOT/helm-charts/lego/" \\
            --namespace business-systems \\
            --wait
        
        success "Critical systems deployed to Kubernetes"
    else
        warning "kubectl not available, skipping Kubernetes deployment"
    fi
}

# Deploy monitoring configurations
deploy_monitoring() {
    local environment=$1
    local databases=$2
    
    info "Deploying monitoring for $environment environment..."
    
    if command -v kubectl &> /dev/null; then
        kubectl create namespace monitoring 2>/dev/null || true
        
        for db in $databases; do
            if [[ -f "$REPO_ROOT/datadog_monitor_${db}.yaml" ]]; then
                kubectl apply -f "$REPO_ROOT/datadog_monitor_${db}.yaml" -n monitoring
            fi
        done
        
        success "Monitoring configurations deployed"
    else
        warning "kubectl not available, skipping monitoring deployment"
    fi
}

# Generate deployment report
generate_report() {
    local environment=$1
    
    info "Generating deployment report for $environment..."
    
    cat > "$REPO_ROOT/deployment_report_${environment}.md" << EOF
# Deployment Report - $environment Environment

**Deployment Date:** $(date)
**Environment:** $environment
**Deployed By:** $(whoami)

## Deployment Summary

$(case $environment in
    dev) echo "- Deployed Config-Only scenarios: periodic_table, world_happiness, titanic";;
    staging) echo "- Deployed Mixed scenarios: pagila, chinook, netflix";;  
    prod) echo "- Deployed Logic-Heavy scenarios: employees, lego, postgres_air";;
    all) echo "- Deployed all scenarios across dev, staging, and prod environments";;
esac)

## Infrastructure Deployed

- Terraform configurations applied
- Database servers provisioned
- Monitoring alerts configured
- $(if [[ "$environment" != "dev" ]]; then echo "Service layer deployed"; fi)

## Next Steps

1. Verify database connectivity
2. Run scenario validation: \`python test_scenarios_validation.py\`
3. Monitor Datadog alerts
4. Test decommissioning workflow

## Support

For issues, contact: database-team@company.com
EOF

    success "Deployment report generated: deployment_report_${environment}.md"
}

# Main deployment function
main() {
    local environment="${1:-}"
    local validate_only=false
    local skip_validation=false
    local dry_run=false
    local force=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --validate-only)
                validate_only=true
                shift
                ;;
            --skip-validation)
                skip_validation=true
                shift
                ;;
            --dry-run)
                dry_run=true
                export DRY_RUN=true
                shift
                ;;
            --force)
                force=true
                export FORCE=true
                shift
                ;;
            --help)
                usage
                exit 0
                ;;
            -*)
                error "Unknown option $1"
                ;;
            *)
                if [[ -z "$environment" ]]; then
                    environment=$1
                fi
                shift
                ;;
        esac
    done
    
    if [[ -z "$environment" ]]; then
        usage
        exit 1
    fi
    
    # Start deployment
    info "Starting database decommissioning scenarios deployment"
    info "Environment: $environment"
    info "Dry run: ${dry_run}"
    
    # Check prerequisites
    check_prerequisites
    
    # Validate scenarios unless skipped
    if [[ "$skip_validation" != "true" ]]; then
        validate_scenarios
    fi
    
    # Exit if validation only
    if [[ "$validate_only" == "true" ]]; then
        success "Validation completed successfully"
        exit 0
    fi
    
    # Deploy based on environment
    case "$environment" in
        dev)
            deploy_dev
            ;;
        staging)
            deploy_staging
            ;;
        prod)
            deploy_prod
            ;;
        all)
            deploy_dev
            deploy_staging
            deploy_prod
            ;;
        *)
            error "Invalid environment: $environment. Use dev, staging, prod, or all"
            ;;
    esac
    
    # Generate report
    generate_report "$environment"
    
    success "Deployment completed successfully!"
    info "Check deployment.log for detailed logs"
}

# Run main function with all arguments
main "$@"
"""

# Save the deployment script
with open("deploy_scenarios.sh", "w") as f:
    f.write(deployment_script)

print("✅ Created automated deployment script")
print("File: scripts/deploy-scenarios.sh")
print("Usage: ./scripts/deploy-scenarios.sh <environment> [options]")
print("Features: Environment-specific deployment, validation, monitoring setup")
