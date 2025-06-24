# Create Helm chart configurations for each database
def create_helm_values(database_name, scenario_type, criticality, description):
    """Create Helm values.yaml for a database"""

    helm_values = f"""# helm-charts/{database_name}/values.yaml
# Kubernetes deployment configuration for {database_name} database
# Scenario: {scenario_type} | Criticality: {criticality}

# Global configuration
global:
  database:
    name: "{database_name}"
    scenario: "{scenario_type.lower()}"
    criticality: "{criticality.lower()}"
  
  # Image registry settings
  imageRegistry: "registry.company.com"
  storageClass: "premium-ssd"
  
# PostgreSQL configuration
postgresql:
  enabled: true
  
  # Database connection settings
  auth:
    postgresPassword: ""  # Will be set via secret
    username: "dbuser"
    password: ""  # Will be set via secret
    database: "{database_name}"
  
  # Primary server configuration
  primary:
    name: "primary"
    
    # Resource allocation based on criticality
    resources:
      requests:
        {"cpu: '2000m'" if criticality == "CRITICAL" else "cpu: '500m'" if criticality == "MEDIUM" else "cpu: '250m'"}
        {"memory: '4Gi'" if criticality == "CRITICAL" else "memory: '2Gi'" if criticality == "MEDIUM" else "memory: '1Gi'"}
      limits:
        {"cpu: '4000m'" if criticality == "CRITICAL" else "cpu: '1000m'" if criticality == "MEDIUM" else "cpu: '500m'"}
        {"memory: '8Gi'" if criticality == "CRITICAL" else "memory: '4Gi'" if criticality == "MEDIUM" else "memory: '2Gi'"}
    
    # Storage configuration  
    persistence:
      enabled: true
      size: {"100Gi" if criticality == "CRITICAL" else "50Gi" if criticality == "MEDIUM" else "20Gi"}
      storageClass: {"premium-ssd" if criticality == "CRITICAL" else "standard-ssd"}
      accessModes:
        - ReadWriteOnce
    
    # PostgreSQL configuration parameters
    postgresqlConfiguration:
      max_connections: {"200" if criticality == "CRITICAL" else "100" if criticality == "MEDIUM" else "50"}
      shared_buffers: {"1GB" if criticality == "CRITICAL" else "512MB" if criticality == "MEDIUM" else "256MB"}
      effective_cache_size: {"3GB" if criticality == "CRITICAL" else "1536MB" if criticality == "MEDIUM" else "768MB"}
      work_mem: {"32MB" if criticality == "CRITICAL" else "16MB" if criticality == "MEDIUM" else "8MB"}
      
      # Logging configuration for monitoring
      log_statement: "all"  # Log all statements for decommissioning analysis
      log_connections: "on"
      log_disconnections: "on"
      log_duration: "on"
      log_min_duration_statement: "1000"  # Log queries longer than 1 second
      
    # Pod security context
    podSecurityContext:
      fsGroup: 1001
      runAsUser: 1001
      runAsNonRoot: true
      
    # Container security context  
    containerSecurityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
      
  # High availability configuration (for critical databases)
  {"readReplicas:" if criticality == "CRITICAL" else "# readReplicas: # Disabled for non-critical"}
    {"replicaCount: 2" if criticality == "CRITICAL" else "# replicaCount: 0"}
    
    {"resources:" if criticality == "CRITICAL" else ""}
      {"requests:" if criticality == "CRITICAL" else ""}
        {"cpu: '1000m'" if criticality == "CRITICAL" else ""}
        {"memory: '2Gi'" if criticality == "CRITICAL" else ""}
      {"limits:" if criticality == "CRITICAL" else ""}
        {"cpu: '2000m'" if criticality == "CRITICAL" else ""}
        {"memory: '4Gi'" if criticality == "CRITICAL" else ""}

# Service configuration
service:
  type: ClusterIP
  port: 5432
  
  # Service annotations for monitoring
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9187"
    datadog.com/check: "postgres"
    
    # Decommissioning metadata
    decommissioning.company.com/scenario: "{scenario_type.lower()}"
    decommissioning.company.com/criticality: "{criticality.lower()}"
    decommissioning.company.com/monitor: "enabled"

# Network policies
networkPolicy:
  enabled: true
  
  # Ingress rules based on scenario type
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: "application"
      - namespaceSelector:
          matchLabels:
            name: "monitoring"
      ports:
      - protocol: TCP
        port: 5432
    
    # Additional access for logic-heavy scenarios
    {"- from:" if scenario_type == "LOGIC_HEAVY" else "# Additional ingress disabled for non-logic-heavy"}
      {"- namespaceSelector:" if scenario_type == "LOGIC_HEAVY" else ""}
          {"matchLabels:" if scenario_type == "LOGIC_HEAVY" else ""}
            {"name: 'analytics'" if scenario_type == "LOGIC_HEAVY" else ""}
      {"- namespaceSelector:" if scenario_type == "LOGIC_HEAVY" else ""}
          {"matchLabels:" if scenario_type == "LOGIC_HEAVY" else ""}
            {"name: 'business-intelligence'" if scenario_type == "LOGIC_HEAVY" else ""}

# Monitoring and observability
monitoring:
  enabled: true
  
  # PostgreSQL exporter for Prometheus
  postgresqlExporter:
    enabled: true
    image:
      registry: quay.io
      repository: prometheuscommunity/postgres-exporter
      tag: "v0.12.0"
    
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "200m"
        memory: "256Mi"
        
    # Custom metrics for decommissioning
    customMetrics:
      - metric_name: "pg_database_connection_idle_time"
        help: "Time since last database connection"
        query: |
          SELECT 
            datname as database,
            EXTRACT(EPOCH FROM (now() - pg_stat_get_db_stat_reset_time(oid))) as idle_seconds
          FROM pg_database 
          WHERE datname = '{database_name}'
      
      - metric_name: "pg_database_last_query_time"  
        help: "Timestamp of last query executed"
        query: |
          SELECT 
            datname as database,
            EXTRACT(EPOCH FROM max(query_start)) as last_query_epoch
          FROM pg_stat_activity 
          WHERE datname = '{database_name}'
          GROUP BY datname

  # Service monitor for Prometheus
  serviceMonitor:
    enabled: true
    namespace: "monitoring"
    labels:
      app: "{database_name}-postgres"
      scenario: "{scenario_type.lower()}"
    interval: "30s"
    path: "/metrics"

# Backup configuration
backup:
  enabled: {"true" if criticality in ["CRITICAL", "MEDIUM"] else "false"}
  
  {"schedule: '0 2 * * *'  # Daily at 2 AM" if criticality in ["CRITICAL", "MEDIUM"] else "# Backup disabled for low criticality"}
  {"retention: '30d'" if criticality == "CRITICAL" else "retention: '7d'" if criticality == "MEDIUM" else ""}
  
  {"storage:" if criticality in ["CRITICAL", "MEDIUM"] else ""}
    {"type: 'azure-blob'" if criticality in ["CRITICAL", "MEDIUM"] else ""}
    {"container: 'database-backups'" if criticality in ["CRITICAL", "MEDIUM"] else ""}

# Pod disruption budget (for critical databases)
{"podDisruptionBudget:" if criticality == "CRITICAL" else "# podDisruptionBudget: # Disabled for non-critical"}
  {"enabled: true" if criticality == "CRITICAL" else ""}
  {"minAvailable: 1" if criticality == "CRITICAL" else ""}

# Resource quotas and limits
resourceQuota:
  enabled: true
  hard:
    {"limits.cpu: '8000m'" if criticality == "CRITICAL" else "limits.cpu: '2000m'" if criticality == "MEDIUM" else "limits.cpu: '1000m'"}
    {"limits.memory: '16Gi'" if criticality == "CRITICAL" else "limits.memory: '8Gi'" if criticality == "MEDIUM" else "limits.memory: '4Gi'"}
    {"persistentvolumeclaims: '3'" if criticality == "CRITICAL" else "persistentvolumeclaims: '2'" if criticality == "MEDIUM" else "persistentvolumeclaims: '1'"}

# Labels and annotations
labels:
  app: "{database_name}"
  database: "{database_name}"
  scenario: "{scenario_type.lower()}"
  criticality: "{criticality.lower()}"
  chart: "postgresql"
  heritage: "Helm"
  
annotations:
  # Decommissioning workflow metadata
  decommissioning.company.com/database: "{database_name}"
  decommissioning.company.com/scenario: "{scenario_type}"
  decommissioning.company.com/criticality: "{criticality}"
  decommissioning.company.com/description: "{description}"
  decommissioning.company.com/created: "{{{{ .Release.Time }}}}"
  
  # Monitoring annotations
  prometheus.io/scrape: "true"
  datadog.com/check: "postgres"
  
  # Configuration management
  helm.sh/hook-weight: "0"
  
# Environment-specific overrides
environments:
  development:
    postgresql:
      primary:
        resources:
          requests:
            cpu: "250m"
            memory: "1Gi"
          limits:
            cpu: "500m" 
            memory: "2Gi"
        persistence:
          size: "10Gi"
          
  staging:
    postgresql:
      primary:
        resources:
          requests:
            {"cpu: '1000m'" if criticality == "CRITICAL" else "cpu: '500m'"}
            {"memory: '2Gi'" if criticality == "CRITICAL" else "memory: '1Gi'"}
          limits:
            {"cpu: '2000m'" if criticality == "CRITICAL" else "cpu: '1000m'"}
            {"memory: '4Gi'" if criticality == "CRITICAL" else "memory: '2Gi'"}
        persistence:
          size: {"50Gi" if criticality == "CRITICAL" else "25Gi"}
          
  production:
    # Use default values defined above
    postgresql:
      primary:
        nodeSelector:
          {"database-tier: 'critical'" if criticality == "CRITICAL" else "database-tier: 'standard'"}
        tolerations:
        - key: "database"
          operator: "Equal"
          value: "{criticality.lower()}"
          effect: "NoSchedule"

# Health checks and probes
healthChecks:
  livenessProbe:
    enabled: true
    exec:
      command:
        - /bin/bash
        - -ec
        - 'PGPASSWORD=$POSTGRES_PASSWORD psql -w -U "dbuser" -d "{database_name}" -h 127.0.0.1 -c "SELECT 1"'
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 6
    successThreshold: 1
    
  readinessProbe:
    enabled: true
    exec:
      command:
        - /bin/bash
        - -ec
        - 'PGPASSWORD=$POSTGRES_PASSWORD psql -w -U "dbuser" -d "{database_name}" -h 127.0.0.1 -c "SELECT 1"'
    initialDelaySeconds: 5
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 6
    successThreshold: 1
"""
    return helm_values


# Database configurations with descriptions
databases_helm_config = [
    # Config-Only scenarios
    (
        "periodic_table",
        "CONFIG_ONLY",
        "LOW",
        "Chemical elements reference database for chemistry applications",
    ),
    (
        "world_happiness",
        "CONFIG_ONLY",
        "LOW",
        "World happiness index data for analytics and reporting",
    ),
    (
        "titanic",
        "CONFIG_ONLY",
        "LOW",
        "Historical passenger data for data science training and demos",
    ),
    # Mixed scenarios
    (
        "pagila",
        "MIXED",
        "MEDIUM",
        "DVD rental store database with moderate service layer usage",
    ),
    (
        "chinook",
        "MIXED",
        "MEDIUM",
        "Digital media store with basic service integrations",
    ),
    (
        "netflix",
        "MIXED",
        "MEDIUM",
        "Content catalog with lightweight service connections",
    ),
    # Logic-Heavy scenarios
    (
        "employees",
        "LOGIC_HEAVY",
        "CRITICAL",
        "Enterprise payroll system with critical business operations",
    ),
    (
        "lego",
        "LOGIC_HEAVY",
        "CRITICAL",
        "Product analytics and revenue forecasting system",
    ),
    (
        "postgres_air",
        "LOGIC_HEAVY",
        "CRITICAL",
        "Flight operations and safety-critical airline database",
    ),
]

# Generate all Helm values files
for db_name, scenario, criticality, description in databases_helm_config:
    helm_content = create_helm_values(db_name, scenario, criticality, description)

    filename = f"helm_values_{db_name}.yaml"
    with open(filename, "w") as f:
        f.write(helm_content)

print("✅ Created Helm chart configurations for all 9 databases")
print("Files created:")
for db_name, scenario, criticality, description in databases_helm_config:
    print(f"  - helm-charts/{db_name}/values.yaml ({scenario}, {criticality})")
print("\nFeatures:")
print("  - Environment-specific resource allocation")
print("  - Criticality-based configurations")
print("  - Monitoring and observability integration")
print("  - Network policies and security")
print("  - Backup strategies by criticality")
print("  - Health checks and probes")
print("  - Decommissioning metadata annotations")
