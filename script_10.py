# Create comprehensive database ownership documentation
database_ownership_doc = """# Database Ownership and Decommissioning Documentation

## Overview

This document provides comprehensive ownership information for all databases in the postgres-sample-dbs testing environment, designed to simulate realistic database decommissioning workflows.

## Database Inventory

| Database | Scenario Type | Criticality | Owner Team | Contact Email | Last Used | Decommissioning Risk |
|----------|---------------|-------------|------------|---------------|-----------|---------------------|
| periodic_table | CONFIG_ONLY | LOW | Chemistry Team | chemistry-team@company.com | 2024-02-20 | HIGH |
| world_happiness | CONFIG_ONLY | LOW | Analytics Team | analytics-team@company.com | 2024-01-30 | HIGH |
| titanic | CONFIG_ONLY | LOW | Data Science Team | data-science-team@company.com | 2024-02-10 | HIGH |
| pagila | MIXED | MEDIUM | Development Team | development-team@company.com | 2024-04-15 | MEDIUM |
| chinook | MIXED | MEDIUM | Media Team | media-team@company.com | 2024-03-25 | MEDIUM |
| netflix | MIXED | MEDIUM | Content Team | content-team@company.com | 2024-05-10 | MEDIUM |
| employees | LOGIC_HEAVY | CRITICAL | HR Team | hr-team@company.com | 2025-06-24 | LOW |
| lego | LOGIC_HEAVY | CRITICAL | Analytics Team | analytics-team@company.com | 2025-06-24 | LOW |
| postgres_air | LOGIC_HEAVY | CRITICAL | Operations Team | operations-team@company.com | 2025-06-24 | LOW |

## Scenario Type Definitions

### CONFIG_ONLY Databases
**Characteristics:**
- References ONLY in infrastructure configurations (Terraform, Helm, Docker)
- NO application code dependencies
- Safe for automated removal after approval
- Minimal business impact

**Examples:** periodic_table, world_happiness, titanic

**Decommissioning Process:**
1. Automated monitoring detects 30+ days of inactivity
2. Datadog alert sent to owner team
3. 7-day grace period for owner response
4. If no response, create GitHub issue for review
5. Remove infrastructure configurations after approval

### MIXED Scenarios
**Characteristics:**
- Infrastructure configurations + basic service layer connections
- NO complex business logic
- Requires service dependency review
- Moderate business impact

**Examples:** pagila, chinook, netflix

**Decommissioning Process:**
1. Automated monitoring detects 21+ days of inactivity
2. Manual review of service layer dependencies required
3. Owner approval needed before removal
4. Update service configurations
5. Remove infrastructure configurations

### LOGIC_HEAVY Scenarios
**Characteristics:**
- Infrastructure + complex business operations + analytics
- Critical business dependencies
- Requires manual review and executive approval
- High business impact

**Examples:** employees, lego, postgres_air

**Decommissioning Process:**
1. Automated monitoring detects 24+ hours of inactivity (alert only)
2. MANDATORY manual review by database team
3. Executive approval required (CFO/CTO level)
4. Business impact assessment
5. Migration plan required before removal

## Owner Team Details

### Chemistry Team
- **Primary Contact:** Dr. Sarah Chen (sarah.chen@company.com)
- **Secondary Contact:** Dr. Michael Rodriguez (michael.rodriguez@company.com)
- **Slack Channel:** #chemistry-team
- **Databases:** periodic_table
- **Business Impact:** Research and educational applications
- **Approval Authority:** Team Lead (Sarah Chen)

### Analytics Team
- **Primary Contact:** Jennifer Wang (jennifer.wang@company.com)
- **Secondary Contact:** David Park (david.park@company.com)
- **Slack Channel:** #analytics-team
- **Databases:** world_happiness, lego
- **Business Impact:** Business intelligence and strategic reporting
- **Approval Authority:** Analytics Director (Jennifer Wang)

### Data Science Team
- **Primary Contact:** Dr. Alex Thompson (alex.thompson@company.com)
- **Secondary Contact:** Maria Garcia (maria.garcia@company.com)
- **Slack Channel:** #data-science
- **Databases:** titanic
- **Business Impact:** ML model training and research
- **Approval Authority:** Data Science Manager (Alex Thompson)

### Development Team
- **Primary Contact:** Kevin Liu (kevin.liu@company.com)
- **Secondary Contact:** Rachel Kim (rachel.kim@company.com)
- **Slack Channel:** #development
- **Databases:** pagila
- **Business Impact:** Application development and testing
- **Approval Authority:** Development Manager (Kevin Liu)

### Media Team
- **Primary Contact:** James Wilson (james.wilson@company.com)
- **Secondary Contact:** Lisa Brown (lisa.brown@company.com)
- **Slack Channel:** #media-team
- **Databases:** chinook
- **Business Impact:** Digital media catalog management
- **Approval Authority:** Media Director (James Wilson)

### Content Team
- **Primary Contact:** Emma Davis (emma.davis@company.com)
- **Secondary Contact:** Robert Johnson (robert.johnson@company.com)
- **Slack Channel:** #content-team
- **Databases:** netflix
- **Business Impact:** Content recommendation systems
- **Approval Authority:** Content Manager (Emma Davis)

### HR Team
- **Primary Contact:** Patricia Miller (patricia.miller@company.com)
- **Secondary Contact:** Mark Anderson (mark.anderson@company.com)
- **Slack Channel:** #hr-team
- **Databases:** employees
- **Business Impact:** CRITICAL - $50M+ annual payroll operations
- **Approval Authority:** Chief Human Resources Officer (Patricia Miller)
- **Executive Escalation:** CFO approval required for any changes

### Operations Team
- **Primary Contact:** Thomas White (thomas.white@company.com)
- **Secondary Contact:** Nancy Taylor (nancy.taylor@company.com)
- **Slack Channel:** #operations
- **Databases:** postgres_air
- **Business Impact:** CRITICAL - Flight safety and regulatory compliance
- **Approval Authority:** Chief Operations Officer (Thomas White)
- **Executive Escalation:** CTO approval required for any changes

## Decommissioning Risk Assessment

### HIGH RISK (Config-Only)
- **Risk Level:** HIGH for decommissioning
- **Reason:** Databases appear unused and safe for removal
- **Action:** Automated workflow with owner notification
- **Timeline:** 30-day monitoring threshold
- **Approval:** Owner team approval sufficient

### MEDIUM RISK (Mixed)
- **Risk Level:** MEDIUM for decommissioning
- **Reason:** Service layer dependencies require review
- **Action:** Manual service dependency analysis
- **Timeline:** 21-day monitoring threshold
- **Approval:** Owner approval + service team review

### LOW RISK (Logic-Heavy)
- **Risk Level:** LOW for decommissioning (but HIGH business impact)
- **Reason:** Critical business operations - likely false positive
- **Action:** Executive review and business impact assessment
- **Timeline:** 24-hour alert threshold (investigation only)
- **Approval:** Executive level (CFO/CTO) + business justification

## Escalation Procedures

### Level 1: Owner Team Notification
- **Trigger:** Monitoring threshold exceeded
- **Recipients:** Primary and secondary contacts
- **Timeline:** Immediate notification
- **Required Action:** Response within 7 days

### Level 2: Management Escalation
- **Trigger:** No response to Level 1 after 7 days
- **Recipients:** Team managers and database team
- **Timeline:** 14 days after initial alert
- **Required Action:** Management review and decision

### Level 3: Executive Escalation
- **Trigger:** CRITICAL databases or unresolved Level 2
- **Recipients:** CFO, CTO, affected executives
- **Timeline:** 21 days after initial alert
- **Required Action:** Executive decision and business justification

## Compliance and Audit Requirements

### SOX Compliance (Employees Database)
- **Requirement:** Full audit trail for any changes
- **Documentation:** Business justification and executive approval
- **Timeline:** 90-day advance notice for any changes
- **External Review:** External auditor notification required

### Regulatory Compliance (Postgres Air Database)
- **Requirement:** FAA and EASA regulatory review
- **Documentation:** Safety impact assessment
- **Timeline:** 180-day advance notice for any changes
- **External Review:** Regulatory authority notification

### Data Privacy (All Databases)
- **Requirement:** GDPR and CCPA compliance review
- **Documentation:** Data privacy impact assessment
- **Timeline:** 30-day advance notice for data changes
- **External Review:** Legal team approval

## Contact Information

### Database Team
- **Primary:** Database Administrator (dba@company.com)
- **Secondary:** Infrastructure Team (infrastructure@company.com)
- **Emergency:** On-call rotation (database-oncall@company.com)
- **Slack:** #database-team

### Executive Contacts
- **CFO:** Chief Financial Officer (cfo@company.com)
- **CTO:** Chief Technology Officer (cto@company.com)
- **CHRO:** Chief Human Resources Officer (chro@company.com)
- **COO:** Chief Operations Officer (coo@company.com)

### External Contacts
- **External Auditor:** Auditing Firm (audit@external-firm.com)
- **Legal Team:** Legal Department (legal@company.com)
- **Compliance Officer:** Compliance Team (compliance@company.com)

## Standard Operating Procedures

### Database Decommissioning Workflow
1. **Detection:** Automated monitoring identifies inactive database
2. **Classification:** Determine scenario type and business impact
3. **Notification:** Alert appropriate owner team and stakeholders
4. **Assessment:** Conduct dependency analysis and impact review
5. **Approval:** Obtain required approvals based on criticality
6. **Documentation:** Complete all required documentation
7. **Execution:** Remove infrastructure configurations
8. **Verification:** Confirm successful removal and update inventory

### Emergency Procedures
- **Immediate Response:** Contact database on-call team
- **Business Hours:** 8 AM - 5 PM PT, Monday-Friday
- **After Hours:** Emergency escalation via PagerDuty
- **Critical Issues:** Executive notification within 1 hour

---

**Document Version:** 1.0  
**Last Updated:** June 24, 2025  
**Owner:** Database Team  
**Approved By:** CTO Office  
**Next Review:** December 24, 2025
"""

# Save the ownership documentation
with open("database_ownership.md", "w") as f:
    f.write(database_ownership_doc)

print("✅ Created comprehensive database ownership documentation")
print("File: docs/database-ownership.md")
print("Contains: Owner contacts, escalation procedures, compliance requirements")
