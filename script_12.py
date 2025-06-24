# Create the validation script again without the chmod operation
validation_script = '''#!/usr/bin/env python3
"""
Test Scenarios Validation Script
================================

Validates that database decommissioning test scenarios are properly implemented
according to the separation rules defined in the requirements.

Usage: python test_scenarios_validation.py

Author: Database Team
Version: 1.0
"""

import os
import re
import json
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

class DatabaseScenarioValidator:
    """Main validator for database scenarios"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.results: List[ValidationResult] = []
        
        # Database scenario definitions
        self.scenarios = {
            # Config-Only scenarios
            "periodic_table": ("CONFIG_ONLY", "LOW", "chemistry-team@company.com"),
            "world_happiness": ("CONFIG_ONLY", "LOW", "analytics-team@company.com"),
            "titanic": ("CONFIG_ONLY", "LOW", "data-science-team@company.com"),
            
            # Mixed scenarios
            "pagila": ("MIXED", "MEDIUM", "development-team@company.com"),
            "chinook": ("MIXED", "MEDIUM", "media-team@company.com"),
            "netflix": ("MIXED", "MEDIUM", "content-team@company.com"),
            
            # Logic-Heavy scenarios
            "employees": ("LOGIC_HEAVY", "CRITICAL", "hr-team@company.com"),
            "lego": ("LOGIC_HEAVY", "CRITICAL", "analytics-team@company.com"),
            "postgres_air": ("LOGIC_HEAVY", "CRITICAL", "operations-team@company.com")
        }
    
    def validate_all_scenarios(self) -> bool:
        """Run all validation checks and return success status"""
        print("🔍 Starting database scenario validation...")
        print("=" * 60)
        
        for database, (scenario_str, criticality, owner) in self.scenarios.items():
            scenario_type = ScenarioType(scenario_str)
            print(f"\\n📊 Validating {database} ({scenario_type.value})")
            
            # Core validation checks
            self._validate_scenario_separation(database, scenario_type)
            self._validate_infrastructure_files(database, scenario_type)
            self._validate_monitoring_setup(database, scenario_type)
        
        return self._generate_report()
    
    def _validate_scenario_separation(self, database: str, scenario_type: ScenarioType):
        """Validate that scenarios follow separation rules"""
        
        # Check for application code references
        app_code_files = [
            ("src/config/", "configuration"),
            ("src/services/", "service_layer"),
            ("src/business/", "business_logic"),
            ("src/analytics/", "analytics")
        ]
        
        found_references = {}
        
        for dir_path, code_type in app_code_files:
            full_path = self.repo_root / dir_path
            if full_path.exists():
                for py_file in full_path.rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding='utf-8')
                        if database in content:
                            if code_type not in found_references:
                                found_references[code_type] = []
                            found_references[code_type].append(str(py_file))
                    except Exception:
                        pass  # Skip files that can't be read
        
        # Validate based on scenario type
        if scenario_type == ScenarioType.CONFIG_ONLY:
            if found_references:
                self._add_result(database, scenario_type, "config_only_purity", "FAIL",
                               ViolationType.CRITICAL,
                               "Config-only database has application code references",
                               [f"Found in: {list(found_references.keys())}"],
                               sum(found_references.values(), []))
            else:
                self._add_result(database, scenario_type, "config_only_purity", "PASS",
                               ViolationType.INFO, "No application code references (correct)", [], [])
        
        elif scenario_type == ScenarioType.MIXED:
            allowed_types = {"configuration", "service_layer"}
            forbidden_types = {"business_logic", "analytics"}
            
            violations = [t for t in found_references.keys() if t in forbidden_types]
            
            if violations:
                self._add_result(database, scenario_type, "mixed_scenario_rules", "FAIL",
                               ViolationType.CRITICAL,
                               "Mixed scenario has forbidden business logic",
                               [f"Found forbidden: {violations}"],
                               sum([found_references[v] for v in violations], []))
            else:
                has_allowed = any(t in found_references for t in allowed_types)
                if has_allowed:
                    self._add_result(database, scenario_type, "mixed_scenario_rules", "PASS",
                                   ViolationType.INFO, "Mixed scenario properly implemented",
                                   [f"Found allowed: {list(found_references.keys())}"], [])
                else:
                    self._add_result(database, scenario_type, "mixed_scenario_rules", "WARNING",
                                   ViolationType.WARNING, "Mixed scenario has no service layer",
                                   ["Should have configuration and service references"], [])
        
        elif scenario_type == ScenarioType.LOGIC_HEAVY:
            required_types = {"business_logic", "analytics"}
            missing_types = [t for t in required_types if t not in found_references]
            
            if missing_types:
                self._add_result(database, scenario_type, "logic_heavy_complexity", "WARNING",
                               ViolationType.WARNING,
                               "Logic-heavy scenario missing complex logic",
                               [f"Missing: {missing_types}"], [])
            else:
                self._add_result(database, scenario_type, "logic_heavy_complexity", "PASS",
                               ViolationType.INFO, "Logic-heavy scenario properly implemented",
                               [f"Found: {list(found_references.keys())}"], [])
    
    def _validate_infrastructure_files(self, database: str, scenario_type: ScenarioType):
        """Validate infrastructure file existence"""
        
        # Check Terraform files
        terraform_patterns = [
            "terraform_*_databases.tf",
            "terraform_*_critical_databases.tf", 
            "terraform_module_*.tf"
        ]
        
        terraform_found = False
        for pattern in terraform_patterns:
            matches = list(self.repo_root.glob(pattern))
            for tf_file in matches:
                try:
                    content = tf_file.read_text(encoding='utf-8')
                    if database in content:
                        terraform_found = True
                        break
                except Exception:
                    pass
            if terraform_found:
                break
        
        if terraform_found:
            self._add_result(database, scenario_type, "terraform_config", "PASS",
                           ViolationType.INFO, "Terraform configuration found", [], [])
        else:
            self._add_result(database, scenario_type, "terraform_config", "FAIL",
                           ViolationType.CRITICAL, "No Terraform configuration found", [], [])
        
        # Check Helm files  
        helm_pattern = f"helm_values_{database}.yaml"
        helm_files = list(self.repo_root.glob(helm_pattern))
        
        if helm_files:
            self._add_result(database, scenario_type, "helm_config", "PASS",
                           ViolationType.INFO, "Helm configuration found", [], [])
        else:
            self._add_result(database, scenario_type, "helm_config", "WARNING",
                           ViolationType.WARNING, "No Helm configuration found", [], [])
    
    def _validate_monitoring_setup(self, database: str, scenario_type: ScenarioType):
        """Validate monitoring configuration"""
        
        monitor_pattern = f"datadog_monitor_{database}.yaml"
        monitor_files = list(self.repo_root.glob(monitor_pattern))
        
        if monitor_files:
            # Check monitor content
            try:
                monitor_file = monitor_files[0]
                content = monitor_file.read_text(encoding='utf-8')
                
                required_elements = [
                    scenario_type.value,
                    "threshold",
                    "alert",
                    "database_name"
                ]
                
                missing = [elem for elem in required_elements 
                          if elem.lower() not in content.lower()]
                
                if missing:
                    self._add_result(database, scenario_type, "monitoring_config", "WARNING",
                                   ViolationType.WARNING, "Monitoring config incomplete",
                                   [f"Missing: {missing}"], [str(monitor_file)])
                else:
                    self._add_result(database, scenario_type, "monitoring_config", "PASS",
                                   ViolationType.INFO, "Monitoring properly configured",
                                   [], [str(monitor_file)])
            except Exception as e:
                self._add_result(database, scenario_type, "monitoring_config", "WARNING",
                               ViolationType.WARNING, f"Error reading monitor config: {e}",
                               [], [])
        else:
            self._add_result(database, scenario_type, "monitoring_config", "FAIL",
                           ViolationType.CRITICAL, "No monitoring configuration found", [], [])
    
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
    
    def _generate_report(self) -> bool:
        """Generate validation report and return success status"""
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
        
        # Overall assessment
        overall_compliance = (status_counts["PASS"] / len(self.results) * 100) if self.results else 0
        print(f"\\n🎯 OVERALL COMPLIANCE: {overall_compliance:.1f}%")
        
        # Save results
        results_data = []
        for result in self.results:
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
        
        try:
            with open("validation_results.json", "w") as f:
                json.dump(results_data, f, indent=2)
            print(f"\\n💾 Results saved to validation_results.json")
        except Exception as e:
            print(f"\\n⚠️  Could not save results: {e}")
        
        if critical_failures:
            print("\\n❌ VALIDATION FAILED - Critical issues must be resolved")
            return False
        else:
            print("\\n✅ VALIDATION PASSED - Scenarios properly implemented")
            return True

def main():
    """Main validation entry point"""
    print("🔍 Database Decommissioning Test Scenarios Validation")
    print("=" * 60)
    print("Validating scenario separation and implementation...")
    
    validator = DatabaseScenarioValidator()
    success = validator.validate_all_scenarios()
    
    exit_code = 0 if success else 1
    print(f"\\n🚀 Validation complete - Exit code: {exit_code}")
    return exit_code

if __name__ == "__main__":
    exit(main())
'''

# Save the validation script
with open("test_scenarios_validation.py", "w") as f:
    f.write(validation_script)

print("✅ Created validation script")
print("File: test_scenarios_validation.py")
print("Usage: python test_scenarios_validation.py")
print(
    "Features: Validates all scenario separation rules and generates compliance report"
)
