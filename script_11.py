# Create comprehensive validation script for scenario implementation
validation_script = '''#!/usr/bin/env python3
"""
Test Scenarios Validation Script
================================

Validates that database decommissioning test scenarios are properly implemented
according to the separation rules defined in the requirements.

Scenario Rules:
- CONFIG_ONLY: References ONLY in Terraform, Helm, Docker, environment files
- MIXED: Terraform + basic service connections (NO business logic)
- LOGIC_HEAVY: Terraform + complex business operations + analytics

Author: Database Team
Version: 1.0
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class ScenarioType(Enum):
    CONFIG_ONLY = "CONFIG_ONLY"
    MIXED = "MIXED"
    LOGIC_HEAVY = "LOGIC_HEAVY"

class ViolationType(Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"

@dataclass
class ValidationResult:
    """Validation result for a specific check"""
    database: str
    scenario: ScenarioType
    check_name: str
    status: str  # PASS, FAIL, WARNING
    violation_type: ViolationType
    message: str
    details: List[str]
    file_references: List[str]

@dataclass
class ScenarioDefinition:
    """Database scenario definition"""
    name: str
    scenario_type: ScenarioType
    criticality: str
    owner_email: str
    description: str

class DatabaseScenarioValidator:
    """Main validator for database scenarios"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.results: List[ValidationResult] = []
        
        # Database scenario definitions
        self.scenarios = {
            # Config-Only scenarios
            "periodic_table": ScenarioDefinition(
                "periodic_table", ScenarioType.CONFIG_ONLY, "LOW",
                "chemistry-team@company.com", "Chemical elements reference"
            ),
            "world_happiness": ScenarioDefinition(
                "world_happiness", ScenarioType.CONFIG_ONLY, "LOW",
                "analytics-team@company.com", "World happiness index data"
            ),
            "titanic": ScenarioDefinition(
                "titanic", ScenarioType.CONFIG_ONLY, "LOW",
                "data-science-team@company.com", "Historical passenger data"
            ),
            
            # Mixed scenarios
            "pagila": ScenarioDefinition(
                "pagila", ScenarioType.MIXED, "MEDIUM",
                "development-team@company.com", "DVD rental store database"
            ),
            "chinook": ScenarioDefinition(
                "chinook", ScenarioType.MIXED, "MEDIUM",
                "media-team@company.com", "Digital media store"
            ),
            "netflix": ScenarioDefinition(
                "netflix", ScenarioType.MIXED, "MEDIUM", 
                "content-team@company.com", "Content catalog database"
            ),
            
            # Logic-Heavy scenarios
            "employees": ScenarioDefinition(
                "employees", ScenarioType.LOGIC_HEAVY, "CRITICAL",
                "hr-team@company.com", "Enterprise payroll system"
            ),
            "lego": ScenarioDefinition(
                "lego", ScenarioType.LOGIC_HEAVY, "CRITICAL",
                "analytics-team@company.com", "Product analytics system"
            ),
            "postgres_air": ScenarioDefinition(
                "postgres_air", ScenarioType.LOGIC_HEAVY, "CRITICAL",
                "operations-team@company.com", "Flight operations database"
            )
        }
    
    def validate_all_scenarios(self) -> List[ValidationResult]:
        """Run all validation checks"""
        print("🔍 Starting database scenario validation...")
        print("=" * 60)
        
        for database, scenario_def in self.scenarios.items():
            print(f"\\n📊 Validating {database} ({scenario_def.scenario_type.value})")
            
            # Core validation checks
            self._validate_terraform_configuration(database, scenario_def)
            self._validate_application_code_rules(database, scenario_def)
            self._validate_monitoring_configuration(database, scenario_def)
            self._validate_helm_configuration(database, scenario_def)
            self._validate_documentation(database, scenario_def)
            
            # Scenario-specific validation
            if scenario_def.scenario_type == ScenarioType.CONFIG_ONLY:
                self._validate_config_only_rules(database, scenario_def)
            elif scenario_def.scenario_type == ScenarioType.MIXED:
                self._validate_mixed_scenario_rules(database, scenario_def)
            elif scenario_def.scenario_type == ScenarioType.LOGIC_HEAVY:
                self._validate_logic_heavy_rules(database, scenario_def)
        
        self._generate_validation_report()
        return self.results
    
    def _validate_terraform_configuration(self, database: str, scenario_def: ScenarioDefinition):
        """Validate Terraform configurations exist and are properly configured"""
        terraform_files = [
            f"terraform/environments/dev/databases.tf",
            f"terraform/environments/prod/critical_databases.tf",
            f"terraform/modules/database/main.tf"
        ]
        
        found_references = []
        for tf_file in terraform_files:
            file_path = self.repo_root / tf_file
            if file_path.exists():
                content = file_path.read_text()
                if database in content:
                    found_references.append(tf_file)
        
        if found_references:
            self._add_result(database, scenario_def.scenario_type, "terraform_config", "PASS",
                           ViolationType.INFO, f"Terraform configurations found",
                           [f"Found in {len(found_references)} files"], found_references)
        else:
            self._add_result(database, scenario_def.scenario_type, "terraform_config", "FAIL",
                           ViolationType.CRITICAL, f"No Terraform configurations found",
                           ["Database must have infrastructure definitions"], [])
    
    def _validate_application_code_rules(self, database: str, scenario_def: ScenarioDefinition):
        """Validate application code follows scenario rules"""
        app_code_patterns = [
            (r"src/config/.*\\.py", "configuration"),
            (r"src/services/.*\\.py", "service_layer"),
            (r"src/business/.*\\.py", "business_logic"),
            (r"src/analytics/.*\\.py", "analytics")
        ]
        
        code_references = {}
        for pattern, code_type in app_code_patterns:
            files = list(self.repo_root.glob(pattern))
            for file_path in files:
                if file_path.exists():
                    content = file_path.read_text()
                    if database in content:
                        if code_type not in code_references:
                            code_references[code_type] = []
                        code_references[code_type].append(str(file_path))
        
        # Validate based on scenario type
        if scenario_def.scenario_type == ScenarioType.CONFIG_ONLY:
            if code_references:
                self._add_result(database, scenario_def.scenario_type, "code_separation", "FAIL",
                               ViolationType.CRITICAL, 
                               "Config-only database has application code references",
                               [f"Found in: {list(code_references.keys())}"],
                               sum(code_references.values(), []))
            else:
                self._add_result(database, scenario_def.scenario_type, "code_separation", "PASS",
                               ViolationType.INFO, "No application code references (correct)",
                               ["Config-only scenario properly implemented"], [])
        
        elif scenario_def.scenario_type == ScenarioType.MIXED:
            allowed_types = {"configuration", "service_layer"}
            forbidden_types = {"business_logic", "analytics"}
            
            violations = []
            for code_type in code_references:
                if code_type in forbidden_types:
                    violations.append(f"Found {code_type} references")
            
            if violations:
                self._add_result(database, scenario_def.scenario_type, "code_separation", "FAIL",
                               ViolationType.CRITICAL,
                               "Mixed scenario has forbidden business logic",
                               violations, sum(code_references.values(), []))
            else:
                self._add_result(database, scenario_def.scenario_type, "code_separation", "PASS",
                               ViolationType.INFO, "Mixed scenario properly implemented",
                               [f"Found allowed types: {list(code_references.keys())}"], [])
        
        elif scenario_def.scenario_type == ScenarioType.LOGIC_HEAVY:
            required_types = {"business_logic", "analytics"}
            missing_types = []
            for req_type in required_types:
                if req_type not in code_references:
                    missing_types.append(req_type)
            
            if missing_types:
                self._add_result(database, scenario_def.scenario_type, "code_separation", "FAIL",
                               ViolationType.WARNING,
                               "Logic-heavy scenario missing required code types",
                               [f"Missing: {missing_types}"], [])
            else:
                self._add_result(database, scenario_def.scenario_type, "code_separation", "PASS",
                               ViolationType.INFO, "Logic-heavy scenario properly implemented",
                               [f"Found all required types: {list(code_references.keys())}"], [])
    
    def _validate_config_only_rules(self, database: str, scenario_def: ScenarioDefinition):
        """Validate config-only specific rules"""
        # Check that database is not referenced in service layer
        service_files = list(self.repo_root.glob("src/services/**/*.py"))
        business_files = list(self.repo_root.glob("src/business/**/*.py"))
        analytics_files = list(self.repo_root.glob("src/analytics/**/*.py"))
        
        violations = []
        for file_group, group_name in [(service_files, "service"), 
                                      (business_files, "business"), 
                                      (analytics_files, "analytics")]:
            for file_path in file_group:
                if file_path.exists():
                    content = file_path.read_text()
                    if database in content:
                        violations.append(f"Found reference in {group_name}: {file_path}")
        
        if violations:
            self._add_result(database, scenario_def.scenario_type, "config_only_purity", "FAIL",
                           ViolationType.CRITICAL,
                           "Config-only database has code references",
                           violations, [])
        else:
            self._add_result(database, scenario_def.scenario_type, "config_only_purity", "PASS",
                           ViolationType.INFO, "Config-only purity maintained", [], [])
    
    def _validate_mixed_scenario_rules(self, database: str, scenario_def: ScenarioDefinition):
        """Validate mixed scenario specific rules"""
        # Should have service layer but no business logic
        config_files = list(self.repo_root.glob("src/config/**/*.py"))
        service_files = list(self.repo_root.glob("src/services/**/*.py"))
        
        has_config = any(database in f.read_text() for f in config_files if f.exists())
        has_service = any(database in f.read_text() for f in service_files if f.exists())
        
        if has_config and has_service:
            self._add_result(database, scenario_def.scenario_type, "mixed_scenario_structure", "PASS",
                           ViolationType.INFO, "Mixed scenario properly structured",
                           ["Has both config and service layer"], [])
        else:
            missing = []
            if not has_config:
                missing.append("configuration")
            if not has_service:
                missing.append("service layer")
            
            self._add_result(database, scenario_def.scenario_type, "mixed_scenario_structure", "WARNING",
                           ViolationType.WARNING, "Mixed scenario incomplete",
                           [f"Missing: {missing}"], [])
    
    def _validate_logic_heavy_rules(self, database: str, scenario_def: ScenarioDefinition):
        """Validate logic-heavy scenario specific rules"""
        # Should have business logic and/or analytics
        business_files = list(self.repo_root.glob("src/business/**/*.py"))
        analytics_files = list(self.repo_root.glob("src/analytics/**/*.py"))
        
        has_business = any(database in f.read_text() for f in business_files if f.exists())
        has_analytics = any(database in f.read_text() for f in analytics_files if f.exists())
        
        if has_business or has_analytics:
            components = []
            if has_business:
                components.append("business logic")
            if has_analytics:
                components.append("analytics")
            
            self._add_result(database, scenario_def.scenario_type, "logic_heavy_complexity", "PASS",
                           ViolationType.INFO, "Logic-heavy scenario properly implemented",
                           [f"Has: {components}"], [])
        else:
            self._add_result(database, scenario_def.scenario_type, "logic_heavy_complexity", "FAIL",
                           ViolationType.CRITICAL, "Logic-heavy scenario lacks complex logic",
                           ["Missing business logic and analytics"], [])
    
    def _validate_monitoring_configuration(self, database: str, scenario_def: ScenarioDefinition):
        """Validate monitoring configurations"""
        monitor_file = self.repo_root / f"monitoring/database-monitors/{database}_monitor.yaml"
        
        if monitor_file.exists():
            try:
                content = monitor_file.read_text()
                # Check for required monitoring elements
                required_elements = ["threshold", "alert", "owner", scenario_def.scenario_type.value]
                missing_elements = [elem for elem in required_elements if elem.lower() not in content.lower()]
                
                if missing_elements:
                    self._add_result(database, scenario_def.scenario_type, "monitoring_config", "WARNING",
                                   ViolationType.WARNING, "Monitoring config incomplete",
                                   [f"Missing: {missing_elements}"], [str(monitor_file)])
                else:
                    self._add_result(database, scenario_def.scenario_type, "monitoring_config", "PASS",
                                   ViolationType.INFO, "Monitoring properly configured", [], [str(monitor_file)])
            except Exception as e:
                self._add_result(database, scenario_def.scenario_type, "monitoring_config", "FAIL",
                               ViolationType.WARNING, f"Monitoring config error: {e}", [], [str(monitor_file)])
        else:
            self._add_result(database, scenario_def.scenario_type, "monitoring_config", "FAIL",
                           ViolationType.CRITICAL, "No monitoring configuration found", [], [])
    
    def _validate_helm_configuration(self, database: str, scenario_def: ScenarioDefinition):
        """Validate Helm chart configurations"""
        helm_file = self.repo_root / f"helm-charts/{database}/values.yaml"
        
        if helm_file.exists():
            self._add_result(database, scenario_def.scenario_type, "helm_config", "PASS",
                           ViolationType.INFO, "Helm configuration found", [], [str(helm_file)])
        else:
            self._add_result(database, scenario_def.scenario_type, "helm_config", "WARNING",
                           ViolationType.WARNING, "No Helm configuration found", [], [])
    
    def _validate_documentation(self, database: str, scenario_def: ScenarioDefinition):
        """Validate documentation exists and is complete"""
        doc_file = self.repo_root / "docs/database-ownership.md"
        
        if doc_file.exists():
            content = doc_file.read_text()
            if database in content and scenario_def.owner_email in content:
                self._add_result(database, scenario_def.scenario_type, "documentation", "PASS",
                               ViolationType.INFO, "Documentation complete", [], [str(doc_file)])
            else:
                self._add_result(database, scenario_def.scenario_type, "documentation", "WARNING",
                               ViolationType.WARNING, "Documentation incomplete", 
                               [f"Missing database or owner info"], [str(doc_file)])
        else:
            self._add_result(database, scenario_def.scenario_type, "documentation", "FAIL",
                           ViolationType.CRITICAL, "No documentation found", [], [])
    
    def _add_result(self, database: str, scenario: ScenarioType, check_name: str, 
                    status: str, violation_type: ViolationType, message: str, 
                    details: List[str], file_refs: List[str]):
        """Add validation result"""
        result = ValidationResult(
            database=database,
            scenario=scenario,
            check_name=check_name,
            status=status,
            violation_type=violation_type,
            message=message,
            details=details,
            file_references=file_refs
        )
        self.results.append(result)
        
        # Print immediate feedback
        status_emoji = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️"}
        print(f"  {status_emoji.get(status, '❓')} {check_name}: {message}")
    
    def _generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\\n" + "=" * 60)
        print("📋 VALIDATION SUMMARY")
        print("=" * 60)
        
        # Count results by status
        status_counts = {"PASS": 0, "FAIL": 0, "WARNING": 0}
        for result in self.results:
            status_counts[result.status] += 1
        
        print(f"✅ PASSED: {status_counts['PASS']}")
        print(f"❌ FAILED: {status_counts['FAIL']}")
        print(f"⚠️  WARNINGS: {status_counts['WARNING']}")
        print(f"📊 TOTAL CHECKS: {len(self.results)}")
        
        # Critical failures
        critical_failures = [r for r in self.results 
                           if r.status == "FAIL" and r.violation_type == ViolationType.CRITICAL]
        
        if critical_failures:
            print(f"\\n🚨 CRITICAL FAILURES ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"  ❌ {failure.database} ({failure.scenario.value}): {failure.message}")
        
        # Scenario compliance summary
        print(f"\\n📊 SCENARIO COMPLIANCE:")
        for scenario_type in ScenarioType:
            scenario_results = [r for r in self.results if r.scenario == scenario_type]
            passes = len([r for r in scenario_results if r.status == "PASS"])
            total = len(scenario_results)
            compliance_rate = (passes / total * 100) if total > 0 else 0
            print(f"  {scenario_type.value}: {compliance_rate:.1f}% ({passes}/{total})")
        
        # Overall assessment
        overall_compliance = (status_counts["PASS"] / len(self.results) * 100) if self.results else 0
        print(f"\\n🎯 OVERALL COMPLIANCE: {overall_compliance:.1f}%")
        
        if critical_failures:
            print("\\n❌ VALIDATION FAILED - Critical issues must be resolved")
            return False
        elif status_counts["FAIL"] > 0:
            print("\\n⚠️  VALIDATION PASSED WITH ISSUES - Review failures")
            return True
        else:
            print("\\n✅ VALIDATION PASSED - All scenarios properly implemented")
            return True

def main():
    """Main validation entry point"""
    print("🔍 Database Decommissioning Test Scenarios Validation")
    print("=" * 60)
    print("Validating scenario separation and implementation...")
    
    validator = DatabaseScenarioValidator()
    results = validator.validate_all_scenarios()
    
    # Save results to JSON for CI/CD integration
    results_data = []
    for result in results:
        results_data.append({
            "database": result.database,
            "scenario": result.scenario.value,
            "check": result.check_name,
            "status": result.status,
            "violation_type": result.violation_type.value,
            "message": result.message,
            "details": result.details,
            "files": result.file_references
        })
    
    with open("validation_results.json", "w") as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\\n💾 Results saved to validation_results.json")
    
    # Exit code for CI/CD
    critical_failures = [r for r in results if r.status == "FAIL" and 
                        r.violation_type == ViolationType.CRITICAL]
    exit_code = 1 if critical_failures else 0
    
    print(f"\\n🚀 Validation complete - Exit code: {exit_code}")
    return exit_code

if __name__ == "__main__":
    exit(main())
'''

# Save the validation script
with open("test_scenarios_validation.py", "w") as f:
    f.write(validation_script)

# Make it executable
os.chmod("test_scenarios_validation.py", 0o755)

print("✅ Created comprehensive validation script")
print("File: test_scenarios_validation.py")
print("Features:")
print("  - Validates scenario separation rules")
print("  - Checks Terraform, application code, monitoring configs")
print("  - Ensures CONFIG_ONLY has no app code")
print("  - Validates MIXED has service layer only")
print("  - Confirms LOGIC_HEAVY has complex business logic")
print("  - Generates detailed compliance report")
print("  - CI/CD integration with exit codes")
print("  - JSON output for automation")
