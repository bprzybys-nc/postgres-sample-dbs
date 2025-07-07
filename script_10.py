# Create comprehensive database ownership documentation
database_ownership_doc = """# Database Ownership and Decommissioning Documentation

## Overview

This document provides comprehensive ownership information for all databases in the postgres-sample-dbs testing environment, designed to simulate realistic database decommissioning workflows.

## Database Inventory

| Database | Scenario Type | Criticality | Owner Team | Contact Email | Last Used | Decommissioning Risk |
|----------|---------------|-------------|------------|---------------|-----------|---------------------|
| world_happiness | CONFIG_ONLY | LOW | Analytics Team | analytics-team@company.com | 2024-01-30 | HIGH |
| titanic | CONFIG_ONLY | LOW | Data Science Team | data-science-team@company.com | 2024-02-10 | HIGH |
| pagila | MIXED | MEDIUM | Development Team | development-team@company.com | 2024-04-15 | MEDIUM |
| chinook | MIXED | MEDIUM | Media Team | media-team@company.com | 2024-03-25 | MEDIUM |
| netflix | MIXED | MEDIUM | Content Team | content-team@company.com | 2024-05-10 | MEDIUM |
| employees | LOGIC_HEAVY | CRITICAL | HR Team | hr-team@company.com | 2025-06-24 | LOW |
| lego | LOGIC_HEAVY | CRITICAL | Analytics Team | analytics-team@company.com | 2025-06-24 | LOW |
| postgres_air | LOGIC_HEAVY | CRITICAL | Operations Team | operations-team@company.com | 2025-06-24 | LOW |

## Key Stakeholders and Contacts

### Internal Teams
- **DevOps Team:** devops@company.com
- **Database Administration Team:** dba@company.com
- **Security Team:** security@company.com
- **Compliance Team:** compliance@company.com
- **Legal Team:** legal@company.com

### Database Owners (by scenario type)

#### Config-Only Databases
- **world_happiness:** Analytics Team (analytics-team@company.com)
- **titanic:** Data Science Team (data-science-team@company.com)

#### Mixed Databases
- **pagila:** Development Team (development-team@company.com)
- **chinook:** Media Team (media-team@company.com)
- **netflix:** Content Team (content-team@company.com)

#### Logic-Heavy Databases
- **employees:** HR Team (hr-team@company.com)
- **lego:** Analytics Team (analytics-team@company.com)
- **postgres_air:** Operations Team (operations-team@company.com)

## Escalation Matrix

### Internal Escalation
- **Level 1 (On-Call Engineer):** PagerDuty alert
- **Level 2 (Team Lead):** Slack notification, direct call
- **Level 3 (Department Head):** Email, executive summary

### Executive Contacts
- **CTO:** Chief Technology Officer (cto@company.com)
- **CISO:** Chief Information Security Officer (ciso@company.com)
- **CIO:** Chief Information Officer (cio@company.com)
- **CRO:** Chief Risk Officer (cro@company.com)
- **CPO:** Chief Privacy Officer (cpo@company.com)
- **CLO:** Chief Legal Officer (clo@company.com)
- **CFO:** Chief Financial Officer (cfo@company.com)
- **CEO:** Chief Executive Officer (ceo@company.com)
- **Chief Data Officer:** Chief Data Officer (cdo@company.com)
- **Chief Compliance Officer:** Chief Compliance Officer (cco@company.com)
- **Chief Product Officer:** Chief Product Officer (cpo@company.com)
- **Chief Marketing Officer:** Chief Marketing Officer (cmo@company.com)
- **Chief Human Resources Officer:** Chief Human Resources Officer (chro@company.com)
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
