# src/analytics/lego_business_intelligence.py
# Revenue-critical analytics for lego database (Logic-Heavy scenario)
# Complex market analytics and revenue forecasting with executive decision support

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import asyncpg
from enum import Enum
import statistics
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketSegment(Enum):
    """Market segments for LEGO products"""

    CREATOR_EXPERT = "CREATOR_EXPERT"
    LICENSED_PRODUCTS = "LICENSED_PRODUCTS"
    CLASSIC_BUILDING = "CLASSIC_BUILDING"
    EDUCATIONAL = "EDUCATIONAL"
    SEASONAL = "SEASONAL"


class RevenueCategory(Enum):
    """Revenue impact categories"""

    PREMIUM = "PREMIUM"  # >$200 sets
    MAINSTREAM = "MAINSTREAM"  # $50-$200 sets
    ENTRY_LEVEL = "ENTRY_LEVEL"  # <$50 sets


@dataclass
class ProductPerformanceMetrics:
    """Product performance analytics"""

    set_num: str
    set_name: str
    theme: str
    year_released: int
    piece_count: int
    estimated_retail_price: Decimal
    market_segment: MarketSegment
    revenue_category: RevenueCategory
    popularity_score: float
    profit_margin_estimate: Decimal
    market_penetration: float
    competitive_advantage: float


@dataclass
class MarketForecast:
    """Market forecasting model results"""

    forecast_period: str
    theme: str
    projected_revenue: Decimal
    confidence_interval: Tuple[Decimal, Decimal]
    market_growth_rate: float
    risk_factors: List[str]
    strategic_recommendations: List[str]
    executive_summary: str


@dataclass
class ExecutiveMetrics:
    """Executive dashboard metrics"""

    total_portfolio_value: Decimal
    quarterly_growth_rate: float
    market_share_estimate: float
    innovation_index: float
    customer_satisfaction_score: float
    competitive_position: str
    strategic_priorities: List[str]


class LegoBusinessIntelligenceSystem:
    """
    MISSION CRITICAL: LEGO Business Intelligence & Revenue Analytics

    This system supports multi-million dollar executive decisions and strategic planning.
    Used for quarterly board presentations and investor relations.

    Business Impact:
    - $7B+ annual revenue analysis
    - Strategic product portfolio decisions
    - Market expansion planning
    - Competitive positioning
    - Executive decision support
    """

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._market_data = self._initialize_market_intelligence()

    def _initialize_market_intelligence(self) -> Dict[str, Any]:
        """Initialize market intelligence data (would come from external sources)"""
        return {
            "average_price_per_piece": Decimal("0.12"),  # Industry average
            "premium_threshold": Decimal("200.00"),
            "market_growth_rates": {
                "creator_expert": 0.15,  # 15% annual growth
                "licensed_products": 0.08,  # 8% annual growth
                "classic_building": 0.03,  # 3% annual growth
                "educational": 0.12,  # 12% annual growth
                "seasonal": 0.05,  # 5% annual growth
            },
            "competitive_factors": {
                "piece_complexity": 0.25,
                "brand_strength": 0.30,
                "innovation_score": 0.20,
                "market_timing": 0.25,
            },
        }

    async def analyze_product_portfolio(self) -> List[ProductPerformanceMetrics]:
        """
        EXECUTIVE FUNCTION: Comprehensive product portfolio analysis

        Used for:
        - Quarterly board presentations
        - Product discontinuation decisions
        - Investment allocation
        - Strategic planning
        """
        query = """
        SELECT DISTINCT
            s.set_num,
            s.name as set_name,
            t.name as theme,
            s.year,
            s.num_parts,
            pc.name as primary_color,
            COUNT(DISTINCT ip.part_num) as unique_parts,
            AVG(p.part_material) as avg_complexity
        FROM sets s
        JOIN themes t ON s.theme_id = t.id
        LEFT JOIN inventories i ON s.set_num = i.set_num
        LEFT JOIN inventory_parts ip ON i.id = ip.inventory_id
        LEFT JOIN parts p ON ip.part_num = p.part_num
        LEFT JOIN colors pc ON ip.color_id = pc.id
        WHERE s.year >= 2015  -- Focus on recent products
        GROUP BY s.set_num, s.name, t.name, s.year, s.num_parts, pc.name
        ORDER BY s.year DESC, s.num_parts DESC
        LIMIT 500
        """

        try:
            conn = await asyncpg.connect(self.connection_string)
            rows = await conn.fetch(query)
            await conn.close()

            portfolio_metrics = []

            for row in rows:
                # Calculate sophisticated business metrics
                estimated_price = self._calculate_estimated_retail_price(
                    row["num_parts"], row["theme"]
                )
                market_segment = self._determine_market_segment(
                    row["theme"], estimated_price
                )
                revenue_category = self._categorize_revenue_impact(estimated_price)

                # Advanced analytics calculations
                popularity_score = self._calculate_popularity_score(
                    row["year"], row["num_parts"], row["unique_parts"]
                )
                profit_margin = self._estimate_profit_margin(
                    estimated_price, row["num_parts"]
                )
                market_penetration = self._calculate_market_penetration(
                    row["theme"], row["year"]
                )
                competitive_advantage = self._assess_competitive_advantage(
                    row["num_parts"], row["unique_parts"], row["theme"]
                )

                metrics = ProductPerformanceMetrics(
                    set_num=row["set_num"],
                    set_name=row["set_name"],
                    theme=row["theme"],
                    year_released=row["year"],
                    piece_count=row["num_parts"] or 0,
                    estimated_retail_price=estimated_price,
                    market_segment=market_segment,
                    revenue_category=revenue_category,
                    popularity_score=popularity_score,
                    profit_margin_estimate=profit_margin,
                    market_penetration=market_penetration,
                    competitive_advantage=competitive_advantage,
                )

                portfolio_metrics.append(metrics)

            logger.info(f"Analyzed {len(portfolio_metrics)} products in portfolio")
            return portfolio_metrics

        except Exception as e:
            logger.error(f"Portfolio analysis failed: {e}")
            raise

    def _calculate_estimated_retail_price(
        self, piece_count: int, theme: str
    ) -> Decimal:
        """Calculate estimated retail price using proprietary algorithm"""
        if not piece_count:
            return Decimal("29.99")  # Default entry price

        base_price = (
            Decimal(str(piece_count)) * self._market_data["average_price_per_piece"]
        )

        # Theme-based premium multipliers
        theme_multipliers = {
            "Creator Expert": Decimal("1.8"),
            "Star Wars": Decimal("1.5"),
            "Technic": Decimal("1.4"),
            "Architecture": Decimal("1.6"),
            "Ideas": Decimal("1.7"),
            "City": Decimal("1.1"),
            "Friends": Decimal("1.0"),
            "Classic": Decimal("0.9"),
        }

        multiplier = theme_multipliers.get(theme, Decimal("1.2"))
        estimated_price = base_price * multiplier

        # Round to realistic price points
        if estimated_price < 30:
            return Decimal("29.99")
        elif estimated_price < 100:
            return (estimated_price // 10) * 10 + Decimal("9.99")
        else:
            return (estimated_price // 50) * 50 + Decimal("49.99")

    def _determine_market_segment(self, theme: str, price: Decimal) -> MarketSegment:
        """Determine market segment based on theme and price"""
        if theme in ["Creator Expert", "Architecture", "Ideas"]:
            return MarketSegment.CREATOR_EXPERT
        elif theme in ["Star Wars", "Harry Potter", "Marvel", "DC Comics"]:
            return MarketSegment.LICENSED_PRODUCTS
        elif theme in ["Education", "Mindstorms"]:
            return MarketSegment.EDUCATIONAL
        elif "Holiday" in theme or "Christmas" in theme:
            return MarketSegment.SEASONAL
        else:
            return MarketSegment.CLASSIC_BUILDING

    def _categorize_revenue_impact(self, price: Decimal) -> RevenueCategory:
        """Categorize product by revenue impact"""
        if price >= self._market_data["premium_threshold"]:
            return RevenueCategory.PREMIUM
        elif price >= Decimal("50.00"):
            return RevenueCategory.MAINSTREAM
        else:
            return RevenueCategory.ENTRY_LEVEL

    def _calculate_popularity_score(
        self, year: int, piece_count: int, unique_parts: int
    ) -> float:
        """Calculate proprietary popularity score (0-100)"""
        # Recency factor (newer products score higher)
        current_year = datetime.now().year
        recency_score = max(0, 100 - (current_year - year) * 10)

        # Complexity factor (optimal complexity scores highest)
        optimal_pieces = 800  # Sweet spot for complexity
        complexity_score = 100 - abs(piece_count - optimal_pieces) / optimal_pieces * 50

        # Part diversity factor
        if piece_count > 0:
            diversity_ratio = unique_parts / piece_count
            diversity_score = min(100, diversity_ratio * 200)
        else:
            diversity_score = 0

        # Weighted average
        popularity = (
            recency_score * 0.3 + complexity_score * 0.4 + diversity_score * 0.3
        )
        return max(0, min(100, popularity))

    def _estimate_profit_margin(
        self, retail_price: Decimal, piece_count: int
    ) -> Decimal:
        """Estimate profit margin using cost modeling"""
        # Simplified cost model (real version would be highly confidential)
        material_cost = Decimal(str(piece_count)) * Decimal("0.04")  # $0.04 per piece
        manufacturing_cost = material_cost * Decimal("1.5")
        total_cost = manufacturing_cost + retail_price * Decimal(
            "0.15"
        )  # 15% for overhead

        profit_margin = (retail_price - total_cost) / retail_price
        return max(
            Decimal("0.05"), min(Decimal("0.70"), profit_margin)
        )  # Cap between 5-70%

    def _calculate_market_penetration(self, theme: str, year: int) -> float:
        """Calculate market penetration score (0-1)"""
        # Proprietary market penetration algorithm
        base_penetration = 0.15  # 15% base market penetration

        # Theme popularity factors
        theme_factors = {
            "Star Wars": 0.85,
            "City": 0.65,
            "Creator Expert": 0.35,
            "Technic": 0.45,
            "Friends": 0.55,
        }

        theme_factor = theme_factors.get(theme, 0.25)
        year_factor = max(0.1, 1.0 - (2025 - year) * 0.1)  # Decay over time

        return min(1.0, base_penetration + theme_factor * year_factor)

    def _assess_competitive_advantage(
        self, piece_count: int, unique_parts: int, theme: str
    ) -> float:
        """Assess competitive advantage score (0-100)"""
        # Innovation factor
        if piece_count > 0:
            innovation_factor = min(1.0, unique_parts / piece_count)
        else:
            innovation_factor = 0

        # Brand strength factor
        strong_brands = ["Star Wars", "Creator Expert", "Technic", "Architecture"]
        brand_factor = 0.8 if theme in strong_brands else 0.4

        # Complexity factor
        complexity_factor = min(1.0, piece_count / 2000)  # Normalize to 2000 pieces

        # Weighted competitive advantage
        competitive_score = (
            innovation_factor * 40 + brand_factor * 35 + complexity_factor * 25
        )
        return max(0, min(100, competitive_score))

    async def generate_market_forecast(
        self, theme: str, forecast_months: int = 12
    ) -> MarketForecast:
        """
        STRATEGIC PLANNING: Generate market forecast for executive planning

        Used for:
        - Annual strategic planning
        - Investor presentations
        - Board of Directors reports
        - Product roadmap decisions
        """
        try:
            # Get historical data for theme
            portfolio_data = await self.analyze_product_portfolio()
            theme_products = [p for p in portfolio_data if p.theme == theme]

            if not theme_products:
                raise ValueError(f"No data available for theme: {theme}")

            # Calculate current metrics
            total_revenue = sum(p.estimated_retail_price for p in theme_products)
            avg_margin = statistics.mean(
                [float(p.profit_margin_estimate) for p in theme_products]
            )
            avg_popularity = statistics.mean(
                [p.popularity_score for p in theme_products]
            )

            # Market segment analysis
            market_segment = theme_products[0].market_segment
            growth_rate = self._market_data["market_growth_rates"].get(
                market_segment.value.lower(), 0.05
            )

            # Forecast calculations
            monthly_growth = (1 + growth_rate) ** (1 / 12) - 1
            projected_revenue = total_revenue * (
                (1 + monthly_growth) ** forecast_months
            )

            # Confidence intervals (simplified statistical model)
            variance = 0.15  # 15% variance
            lower_bound = projected_revenue * (1 - variance)
            upper_bound = projected_revenue * (1 + variance)

            # Risk assessment
            risk_factors = self._assess_market_risks(theme, avg_popularity, growth_rate)

            # Strategic recommendations
            recommendations = self._generate_strategic_recommendations(
                theme, projected_revenue, growth_rate, avg_margin
            )

            # Executive summary
            executive_summary = self._create_executive_summary(
                theme, projected_revenue, growth_rate, risk_factors
            )

            forecast = MarketForecast(
                forecast_period=f"{forecast_months} months",
                theme=theme,
                projected_revenue=projected_revenue,
                confidence_interval=(lower_bound, upper_bound),
                market_growth_rate=growth_rate,
                risk_factors=risk_factors,
                strategic_recommendations=recommendations,
                executive_summary=executive_summary,
            )

            logger.info(
                f"Generated market forecast for {theme}: ${projected_revenue:,.2f}"
            )
            return forecast

        except Exception as e:
            logger.error(f"Market forecast generation failed for {theme}: {e}")
            raise

    def _assess_market_risks(
        self, theme: str, avg_popularity: float, growth_rate: float
    ) -> List[str]:
        """Assess market risks for strategic planning"""
        risks = []

        if avg_popularity < 40:
            risks.append("LOW_CONSUMER_INTEREST: Below-average popularity scores")

        if growth_rate < 0.03:
            risks.append("MARKET_SATURATION: Limited growth potential")

        if theme in ["Star Wars", "Harry Potter"]:
            risks.append("LICENSE_DEPENDENCY: Revenue dependent on external IP")

        if "Classic" in theme:
            risks.append("COMMODITY_PRESSURE: High competition in basic building sets")

        return risks or ["LOW_RISK: No significant risks identified"]

    def _generate_strategic_recommendations(
        self, theme: str, revenue: Decimal, growth_rate: float, margin: float
    ) -> List[str]:
        """Generate strategic recommendations for executives"""
        recommendations = []

        if revenue > 50000000:  # $50M threshold
            recommendations.append(
                "MAINTAIN_INVESTMENT: High-revenue theme requiring continued support"
            )

        if growth_rate > 0.10:
            recommendations.append(
                "ACCELERATE_EXPANSION: High-growth market opportunity"
            )

        if margin > 0.50:
            recommendations.append(
                "PREMIUM_POSITIONING: Maintain premium pricing strategy"
            )
        elif margin < 0.30:
            recommendations.append(
                "COST_OPTIMIZATION: Review manufacturing and pricing strategies"
            )

        if theme in ["Creator Expert", "Architecture"]:
            recommendations.append(
                "ADULT_MARKET_FOCUS: Continue targeting adult collectors"
            )

        return recommendations or [
            "CONTINUE_MONITORING: Maintain current strategic approach"
        ]

    def _create_executive_summary(
        self, theme: str, revenue: Decimal, growth_rate: float, risks: List[str]
    ) -> str:
        """Create executive summary for board presentations"""
        risk_level = (
            "HIGH" if len(risks) > 2 else "MODERATE" if len(risks) > 1 else "LOW"
        )

        return f"""
        EXECUTIVE SUMMARY - {theme} Market Analysis

        Projected Revenue: ${revenue:,.0f}
        Growth Rate: {growth_rate:.1%}
        Risk Level: {risk_level}

        The {theme} theme shows {'strong' if growth_rate > 0.08 else 'moderate' if growth_rate > 0.03 else 'limited'} 
        growth potential with {'significant' if revenue > 100000000 else 'moderate'} revenue impact.

        Key Focus: {'Maintain market leadership' if revenue > 50000000 else 'Optimize performance'}
        """


if __name__ == "__main__":

    async def demo():
        """Demo revenue-critical analytics"""
        print("MISSION CRITICAL: LEGO Business Intelligence & Revenue Analytics")
        print("=" * 65)
        print("💰 WARNING: This system supports multi-million dollar decisions")
        print("💰 Used for quarterly board presentations and investor relations")
        print("💰 Strategic product portfolio analysis and market forecasting")

        # This would use actual connection string in production
        demo_connection = "postgresql://user:pass@host:5432/lego"

        print("\n📊 Executive dashboard active")
        print("📊 Market intelligence enabled")
        print("📊 Revenue forecasting ready")

    asyncio.run(demo())
