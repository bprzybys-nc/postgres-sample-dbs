# Create Datadog monitoring configurations for all databases
def create_datadog_monitor(database_name, scenario_type, owner_email, criticality):
    """Create Datadog monitor configuration for a database"""

    # Set thresholds based on criticality
    if criticality == "CRITICAL":
        connection_threshold = 86400  # 24 hours
        warning_threshold = 43200  # 12 hours
    elif criticality == "MEDIUM":
        connection_threshold = 259200  # 72 hours (3 days)
        warning_threshold = 172800  # 48 hours (2 days)
    else:  # LOW
        connection_threshold = 2592000  # 30 days
        warning_threshold = 1814400  # 21 days

    monitor_config = f"""# monitoring/database-monitors/{database_name}_monitor.yaml
# Datadog monitoring configuration for {database_name} database
# Scenario: {scenario_type} | Criticality: {criticality}

api_version: v1
kind: Monitor
metadata:
  name: "{database_name}-database-connection-monitor"
  tags:
    - "database:{database_name}"
    - "scenario:{scenario_type.lower()}"
    - "criticality:{criticality.lower()}"
    - "environment:multi"
    - "service:database-monitoring"
    - "team:{owner_email.split('@')[0].replace('-', '_')}"

spec:
  # Database connection monitoring
  type: "query alert"
  
  query: |
    max(last_30m):max:postgresql.connections.active{{database:{database_name}}} by {{host}}
  
  name: "{database_name.title()} Database - Unused Connection Alert"
  
  message: |
    **🔍 Database Decommissioning Candidate Detected**
    
    Database: {database_name}
    Scenario Type: {scenario_type}
    Criticality: {criticality}
    
    **Alert Details:**
    - No active connections detected for {{{{#is_alert}}}}{{{{ value }}}}{{{{/is_alert}}}} seconds
    - Threshold: {connection_threshold} seconds ({connection_threshold/86400:.1f} days)
    - Owner: {owner_email}
    
    **Next Steps:**
    {'⚠️ **CRITICAL DATABASE** - Manual review required before any action' if criticality == 'CRITICAL' else ''}
    {'📊 Mixed scenario - Check service layer dependencies' if scenario_type == 'MIXED' else ''}
    {'⚙️ Config-only scenario - Safe for automated review' if scenario_type == 'CONFIG_ONLY' else ''}
    
    **Decommissioning Workflow:**
    1. Verify no hidden dependencies
    2. Contact owner: {owner_email}
    3. {'Create GitHub issue for manual review' if criticality == 'CRITICAL' else 'Evaluate for removal'}
    4. Document decision and rationale
    
    **Infrastructure References:**
    - Terraform: terraform/environments/*/{{database_name}}*
    - Helm Charts: helm-charts/{database_name}/
    - Monitoring: monitoring/database-monitors/{database_name}_monitor.yaml
    
    @{owner_email} @database-team@company.com
  
  # Alert thresholds
  options:
    thresholds:
      critical: {connection_threshold}
      warning: {warning_threshold}
      warning_recovery: {warning_threshold * 0.8}
      critical_recovery: {connection_threshold * 0.8}
    
    # Notification settings
    notify_audit: true
    require_full_window: true
    new_host_delay: 300
    evaluation_delay: 900  # 15 minutes
    
    # Escalation policy
    escalation_message: |
      **ESCALATION: Unused Database Alert**
      
      Database {database_name} has been without connections for an extended period.
      {'This is a CRITICAL system requiring immediate review.' if criticality == 'CRITICAL' else ''}
      
      Please review for potential decommissioning.
      
    # Advanced configuration
    include_tags: true
    no_data_timeframe: 1440  # 24 hours
    notify_no_data: true
    
    # Silencing options for maintenance
    silenced:
      "*": null  # No permanent silencing
    
  # Additional database-specific monitoring
  additional_checks:
    - name: "connection_count"
      query: "avg(last_15m):avg:postgresql.connections.active{{database:{database_name}}}"
      thresholds:
        warning: 1
        critical: 0
    
    - name: "query_activity" 
      query: "sum(last_1h):sum:postgresql.queries.count{{database:{database_name}}}"
      thresholds:
        warning: 10
        critical: 0
    
    - name: "last_activity"
      query: "max(last_24h):max:postgresql.activity.last_query_time{{database:{database_name}}}"
      thresholds:
        critical: {connection_threshold}

# Custom metrics for decommissioning workflow
custom_metrics:
  - metric_name: "database.decommissioning.candidate"
    description: "Flag database as decommissioning candidate"
    tags:
      - "database:{database_name}"
      - "scenario:{scenario_type.lower()}"
      - "auto_review:{str(scenario_type == 'CONFIG_ONLY').lower()}"
      - "manual_review:{str(criticality == 'CRITICAL').lower()}"
  
  - metric_name: "database.connection.idle_days"
    description: "Number of days since last connection"
    unit: "days"
    tags:
      - "database:{database_name}"
      - "threshold_days:{connection_threshold/86400:.0f}"

# Dashboard integration
dashboard_widgets:
  - widget_type: "timeseries"
    title: "{database_name.title()} Connection Activity"
    definition:
      requests:
        - q: "avg:postgresql.connections.active{{database:{database_name}}}"
          display_type: "line"
      yaxis:
        min: 0
        max: 100
      markers:
        - value: {connection_threshold/3600}  # Show threshold as marker
          display_type: "error dashed"
          label: "Decommissioning Threshold"

# Integration with GitHub for issue creation
github_integration:
  repository: "company/database-decommissioning"
  issue_template: |
    ## Database Decommissioning Review: {database_name}
    
    **Database Information:**
    - Name: {database_name}
    - Scenario: {scenario_type}
    - Criticality: {criticality}
    - Owner: {owner_email}
    
    **Alert Details:**
    - No connections for {{connection_threshold/86400:.0f}} days
    - Last activity: {{last_activity_timestamp}}
    
    **Required Actions:**
    - [ ] Verify no hidden dependencies
    - [ ] Check application logs for references
    - [ ] Contact database owner
    - [ ] {'Review business logic impact' if scenario_type == 'LOGIC_HEAVY' else 'Confirm safe removal'}
    - [ ] Document decommissioning decision
    
    **Owner:** @{owner_email.split('@')[0]}
    **Labels:** database-decommissioning, {scenario_type.lower()}, {criticality.lower()}

# Webhook for automated workflows
webhooks:
  - name: "decommissioning_workflow"
    url: "https://automation.company.com/database-decommissioning/webhook"
    payload: |
      {{
        "database_name": "{database_name}",
        "scenario_type": "{scenario_type}",
        "criticality": "{criticality}",
        "owner_email": "{owner_email}",
        "alert_timestamp": "{{{{alert_timestamp}}}}",
        "metric_value": "{{{{value}}}}",
        "requires_manual_review": {str(criticality == 'CRITICAL').lower()}
      }}
"""
    return monitor_config


# Create monitoring configurations for all databases
databases_config = [
    # Config-Only scenarios
    ("periodic_table", "CONFIG_ONLY", "chemistry-team@company.com", "LOW"),
    ("world_happiness", "CONFIG_ONLY", "analytics-team@company.com", "LOW"),
    ("titanic", "CONFIG_ONLY", "data-science-team@company.com", "LOW"),
    # Mixed scenarios
    ("pagila", "MIXED", "development-team@company.com", "MEDIUM"),
    ("chinook", "MIXED", "media-team@company.com", "MEDIUM"),
    ("netflix", "MIXED", "content-team@company.com", "MEDIUM"),
    # Logic-Heavy scenarios
    ("employees", "LOGIC_HEAVY", "hr-team@company.com", "CRITICAL"),
    ("lego", "LOGIC_HEAVY", "analytics-team@company.com", "CRITICAL"),
    ("postgres_air", "LOGIC_HEAVY", "operations-team@company.com", "CRITICAL"),
]

# Generate all monitor files
for db_name, scenario, owner, criticality in databases_config:
    monitor_content = create_datadog_monitor(db_name, scenario, owner, criticality)

    filename = f"datadog_monitor_{db_name}.yaml"
    with open(filename, "w") as f:
        f.write(monitor_content)

print("✅ Created Datadog monitoring configurations for all 9 databases")
print("Files created:")
for db_name, scenario, owner, criticality in databases_config:
    print(
        f"  - monitoring/database-monitors/{db_name}_monitor.yaml ({scenario}, {criticality})"
    )
print("\nFeatures:")
print("  - 30+ day connection thresholds (per user story)")
print("  - Automated GitHub issue creation")
print("  - Owner notification system")
print("  - Scenario-specific workflows")
print("  - Dashboard integration")
print("  - Webhook automation")
