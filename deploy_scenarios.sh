#!/bin/bash
# scripts/deploy-scenarios.sh
# Automated deployment script for database decommissioning test scenarios

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$REPO_ROOT/deployment.log"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo "  --skip-validation  Skip the validation step"
    echo "  --validate-only    Only run the validation step and exit"
    echo "  --dry-run          Perform a dry run without actual deployments"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev"
    echo "  $0 all --skip-validation"
    echo "  $0 prod --dry-run"
    echo "  $0 staging --validate-only"
    exit 1
}

# Function to check prerequisites (Terraform, Azure CLI, Helm)
check_prerequisites() {
    info "Checking prerequisites..."
    command -v terraform >/dev/null 2>&1 || error "Terraform is not installed. Please install it to proceed."
    command -v az >/dev/null 2>&1 || error "Azure CLI is not installed. Please install it to proceed."
    command -v helm >/dev/null 2>&1 || error "Helm is not installed. Please install it to proceed."
    success "All prerequisites are met."
}

# Function to validate scenarios using script_11.py
validate_scenarios() {
    info "Validating scenarios..."
    python3 "$SCRIPT_DIR/script_11.py"
    success "Scenario validation completed."
}

# Function to deploy development environment databases
deploy_dev() {
    info "Deploying development environment databases..."
    if [[ "$dry_run" == "true" ]]; then
        warning "Dry run: Skipping actual deployment for dev environment."
        return
    fi

    # Run script_1.py to generate terraform_dev_databases.tf
    info "Generating terraform_dev_databases.tf using script_1.py..."
    python3 "$SCRIPT_DIR/script_1.py"

    # Initialize and apply Terraform
    info "Initializing Terraform for dev environment..."
    terraform -chdir="$REPO_ROOT" init -backend-config="backend.azurerm.tfvars" -reconfigure
    info "Applying Terraform for dev environment..."
    terraform -chdir="$REPO_ROOT" apply -auto-approve -var-file="dev.tfvars"
    success "Development environment databases deployed."
}

# Function to deploy staging environment databases
deploy_staging() {
    info "Deploying staging environment databases..."
    if [[ "$dry_run" == "true" ]]; then
        warning "Dry run: Skipping actual deployment for staging environment."
        return
    fi

    # Run script_2.py to generate terraform_staging_mixed_databases.tf
    info "Generating terraform_staging_mixed_databases.tf using script_2.py..."
    python3 "$SCRIPT_DIR/script_2.py"

    # Initialize and apply Terraform
    info "Initializing Terraform for staging environment..."
    terraform -chdir="$REPO_ROOT" init -backend-config="backend.azurerm.tfvars" -reconfigure
    info "Applying Terraform for staging environment..."
    terraform -chdir="$REPO_ROOT" apply -auto-approve -var-file="staging.tfvars"
    success "Staging environment databases deployed."
}

# Function to deploy production environment databases
deploy_prod() {
    info "Deploying production environment databases..."
    if [[ "$dry_run" == "true" ]]; then
        warning "Dry run: Skipping actual deployment for prod environment."
        return
    }

    # Run script_3.py to generate terraform_prod_critical_databases.tf
    info "Generating terraform_prod_critical_databases.tf using script_3.py..."
    python3 "$SCRIPT_DIR/script_3.py"

    # Initialize and apply Terraform
    info "Initializing Terraform for prod environment..."
    terraform -chdir="$REPO_ROOT" init -backend-config="backend.azurerm.tfvars" -reconfigure
    info "Applying Terraform for prod environment..."
    terraform -chdir="$REPO_ROOT" apply -auto-approve -var-file="prod.tfvars"
    success "Production environment databases deployed."
}

# Main function to parse arguments and execute deployment
main() {
    local environment=""
    local skip_validation="false"
    local validate_only="false"
    local dry_run="false"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --skip-validation)
                skip_validation="true"
                shift
                ;;
            --validate-only)
                validate_only="true"
                shift
                ;;
            --dry-run)
                dry_run="true"
                shift
                ;;
            -h|--help)
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
