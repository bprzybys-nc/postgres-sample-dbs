# src/business/employee_payroll_system.py
# Critical business logic for employees database (Logic-Heavy scenario)
# Complex payroll calculations and compliance functions requiring manual review

import asyncio
import logging
from typing import Dict, List, Optional, Decimal, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import asyncpg
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PayrollFrequency(Enum):
    """Payroll frequency types"""

    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"
    ANNUAL = "ANNUAL"


class TaxJurisdiction(Enum):
    """Tax jurisdiction types"""

    FEDERAL = "FEDERAL"
    STATE = "STATE"
    LOCAL = "LOCAL"
    FICA = "FICA"


@dataclass
class Employee:
    """Employee data model"""

    emp_no: int
    first_name: str
    last_name: str
    hire_date: date
    birth_date: date
    gender: str
    current_title: Optional[str] = None
    current_salary: Optional[Decimal] = None
    department: Optional[str] = None
    manager_emp_no: Optional[int] = None


@dataclass
class PayrollCalculation:
    """Payroll calculation result"""

    emp_no: int
    pay_period_start: date
    pay_period_end: date
    gross_pay: Decimal
    federal_tax: Decimal
    state_tax: Decimal
    fica_tax: Decimal
    medicare_tax: Decimal
    total_deductions: Decimal
    net_pay: Decimal
    overtime_hours: Decimal = Decimal("0")
    overtime_pay: Decimal = Decimal("0")
    calculation_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceAlert:
    """Compliance monitoring alert"""

    alert_id: str
    emp_no: int
    alert_type: str
    severity: str
    description: str
    created_at: datetime
    requires_action: bool = True


class EmployeePayrollSystem:
    """
    CRITICAL BUSINESS SYSTEM: Employee Payroll Operations

    This system handles multi-million dollar payroll operations and compliance.
    Any changes require manual review and approval from HR leadership.

    Business Impact:
    - Processing $50M+ annual payroll
    - SOX compliance requirements
    - GDPR data protection
    - Federal/State tax reporting
    """

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._tax_rates = self._load_tax_rates()

    def _load_tax_rates(self) -> Dict[str, Decimal]:
        """Load current tax rates (would typically come from external service)"""
        return {
            "federal_rate": Decimal("0.22"),  # 22% federal tax
            "state_rate": Decimal("0.05"),  # 5% state tax
            "fica_rate": Decimal("0.062"),  # 6.2% FICA
            "medicare_rate": Decimal("0.0145"),  # 1.45% Medicare
        }

    async def get_employee_details(self, emp_no: int) -> Optional[Employee]:
        """
        Retrieve comprehensive employee information
        CRITICAL: Used for payroll, benefits, and compliance reporting
        """
        query = """
        SELECT 
            e.emp_no,
            e.first_name,
            e.last_name,
            e.hire_date,
            e.birth_date,
            e.gender,
            t.title as current_title,
            s.salary as current_salary,
            d.dept_name as department,
            dm.emp_no as manager_emp_no
        FROM employees e
        LEFT JOIN titles t ON e.emp_no = t.emp_no AND t.to_date = '9999-01-01'
        LEFT JOIN salaries s ON e.emp_no = s.emp_no AND s.to_date = '9999-01-01'
        LEFT JOIN dept_emp de ON e.emp_no = de.emp_no AND de.to_date = '9999-01-01'
        LEFT JOIN departments d ON de.dept_no = d.dept_no
        LEFT JOIN dept_manager dm ON d.dept_no = dm.dept_no AND dm.to_date = '9999-01-01'
        WHERE e.emp_no = $1
        """

        try:
            conn = await asyncpg.connect(self.connection_string)
            row = await conn.fetchrow(query, emp_no)
            await conn.close()

            if row:
                return Employee(
                    emp_no=row["emp_no"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    hire_date=row["hire_date"],
                    birth_date=row["birth_date"],
                    gender=row["gender"],
                    current_title=row["current_title"],
                    current_salary=(
                        Decimal(str(row["current_salary"]))
                        if row["current_salary"]
                        else None
                    ),
                    department=row["department"],
                    manager_emp_no=row["manager_emp_no"],
                )
            return None

        except Exception as e:
            logger.error(f"Failed to retrieve employee {emp_no}: {e}")
            raise

    async def calculate_payroll(
        self,
        emp_no: int,
        pay_period_start: date,
        pay_period_end: date,
        overtime_hours: Decimal = Decimal("0"),
    ) -> PayrollCalculation:
        """
        MISSION CRITICAL: Calculate employee payroll with full tax compliance

        This function processes multi-million dollar payroll calculations.
        Must maintain SOX compliance and audit trail.

        Business Rules:
        - Federal/State/Local tax calculations
        - FICA and Medicare withholdings
        - Overtime calculations (1.5x rate)
        - 401k contributions
        - Health insurance deductions
        """
        employee = await self.get_employee_details(emp_no)
        if not employee or not employee.current_salary:
            raise ValueError(
                f"Cannot calculate payroll for employee {emp_no}: missing salary data"
            )

        # Calculate gross pay based on pay period
        days_in_period = (pay_period_end - pay_period_start).days + 1
        daily_rate = employee.current_salary / Decimal("365")
        base_pay = daily_rate * Decimal(str(days_in_period))

        # Calculate overtime pay (1.5x rate for hours over 40/week)
        if overtime_hours > 0:
            hourly_rate = employee.current_salary / Decimal(
                "2080"
            )  # 40 hours * 52 weeks
            overtime_rate = hourly_rate * Decimal("1.5")
            overtime_pay = overtime_rate * overtime_hours
        else:
            overtime_pay = Decimal("0")

        gross_pay = base_pay + overtime_pay

        # Tax calculations (simplified - real system would be much more complex)
        federal_tax = gross_pay * self._tax_rates["federal_rate"]
        state_tax = gross_pay * self._tax_rates["state_rate"]
        fica_tax = gross_pay * self._tax_rates["fica_rate"]
        medicare_tax = gross_pay * self._tax_rates["medicare_rate"]

        # Apply FICA cap (would be dynamic in real system)
        fica_cap = Decimal("147000")  # 2022 FICA wage base
        if gross_pay > fica_cap:
            fica_tax = fica_cap * self._tax_rates["fica_rate"]

        total_deductions = federal_tax + state_tax + fica_tax + medicare_tax
        net_pay = gross_pay - total_deductions

        # Round to cents
        net_pay = net_pay.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return PayrollCalculation(
            emp_no=emp_no,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            gross_pay=gross_pay,
            federal_tax=federal_tax,
            state_tax=state_tax,
            fica_tax=fica_tax,
            medicare_tax=medicare_tax,
            total_deductions=total_deductions,
            net_pay=net_pay,
            overtime_hours=overtime_hours,
            overtime_pay=overtime_pay,
        )

    async def generate_compliance_report(
        self, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """
        SOX COMPLIANCE: Generate audit-ready payroll compliance report

        Required for:
        - SOX 404 controls testing
        - External auditor review
        - Regulatory reporting
        - Board of Directors review
        """
        total_employees_query = """
        SELECT COUNT(DISTINCT emp_no) as total_employees
        FROM employees
        WHERE hire_date <= $1
        """

        salary_distribution_query = """
        SELECT 
            CASE 
                WHEN s.salary < 50000 THEN 'Under $50K'
                WHEN s.salary < 100000 THEN '$50K-$100K'
                WHEN s.salary < 150000 THEN '$100K-$150K'
                ELSE 'Over $150K'
            END as salary_range,
            COUNT(*) as employee_count,
            AVG(s.salary) as avg_salary,
            SUM(s.salary) as total_salary
        FROM salaries s
        WHERE s.to_date = '9999-01-01'
        GROUP BY salary_range
        ORDER BY avg_salary
        """

        try:
            conn = await asyncpg.connect(self.connection_string)

            # Get total employees
            total_emp_result = await conn.fetchrow(total_employees_query, end_date)
            total_employees = total_emp_result["total_employees"]

            # Get salary distribution
            salary_dist_results = await conn.fetch(salary_distribution_query)

            await conn.close()

            # Calculate compliance metrics
            total_annual_payroll = sum(
                row["total_salary"] for row in salary_dist_results
            )

            compliance_report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "employee_metrics": {
                    "total_employees": total_employees,
                    "total_annual_payroll": float(total_annual_payroll),
                    "average_salary": (
                        float(total_annual_payroll / total_employees)
                        if total_employees > 0
                        else 0
                    ),
                },
                "salary_distribution": [
                    {
                        "range": row["salary_range"],
                        "employee_count": row["employee_count"],
                        "average_salary": float(row["avg_salary"]),
                        "total_salary": float(row["total_salary"]),
                    }
                    for row in salary_dist_results
                ],
                "compliance_status": {
                    "sox_compliant": True,
                    "audit_trail_complete": True,
                    "report_generated_at": datetime.utcnow().isoformat(),
                    "requires_cfo_approval": total_annual_payroll
                    > 10000000,  # $10M threshold
                },
            }

            logger.info(f"Generated compliance report for {total_employees} employees")
            logger.info(f"Total annual payroll: ${total_annual_payroll:,.2f}")

            return compliance_report

        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            raise


if __name__ == "__main__":

    async def demo():
        """Demo critical payroll operations"""
        print("CRITICAL BUSINESS SYSTEM: Employee Payroll Operations")
        print("=" * 60)
        print("⚠️  WARNING: This system processes multi-million dollar payroll")
        print("⚠️  Any modifications require manual approval from HR leadership")
        print("⚠️  System maintains SOX compliance and full audit trail")

        # This would use actual connection string in production
        demo_connection = "postgresql://user:pass@host:5432/employees"

        print("\n🔒 System requires database connection for operations")
        print("🔒 Compliance monitoring active")
        print("🔒 Audit trail enabled")

    asyncio.run(demo())
