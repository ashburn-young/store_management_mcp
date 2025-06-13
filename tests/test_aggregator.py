"""Tests for the aggregation agent aggregator."""

from datetime import date
import pytest
from google_business_analytics.aggregation_agent.aggregator import DataAggregator
from google_business_analytics.shared.schemas import (
    StoreInsight, StoreInsightMetadata, SentimentDistribution, ExecutiveSnapshot
)


class TestDataAggregator:
    """Test cases for the DataAggregator class."""
    
    @pytest.mark.asyncio
    async def test_create_executive_snapshot_empty(self):
        """Test creating executive snapshot with empty store insights."""
        aggregator = DataAggregator()
        insights = []
        
        result = await aggregator.create_executive_snapshot(insights)
        
        assert isinstance(result, ExecutiveSnapshot)
        assert result.snapshot_date is not None
        assert result.national_kpis.total_stores == 0
        assert result.national_kpis.avg_rating >= 0.0  # Should have a default value
    
    def test_calculate_national_kpis_empty(self):
        """Test national KPIs calculation with empty insights."""
        aggregator = DataAggregator()
        insights = []
        
        result = aggregator._calculate_national_kpis(insights)
        
        assert result.total_stores == 0
        assert result.avg_rating >= 0.0  # Should have a default value
        assert result.nps_equivalent >= -100 and result.nps_equivalent <= 100
    
    def test_generate_alerts_empty(self):
        """Test alert generation with empty insights."""
        aggregator = DataAggregator()
        insights = []
        
        alerts = aggregator._generate_alerts(insights)
        
        assert isinstance(alerts, list)
        # Empty insights should not generate alerts
        assert len(alerts) == 0
    
    def test_store_insight_creation(self):
        """Test creating a valid StoreInsight object."""
        # Create a valid StoreInsight for testing
        insight = StoreInsight(
            store_id="test_001",
            collection_date=date.today(),
            rating=4.2,
            review_count=50,
            themes_positive=["good service", "clean store"],
            themes_negative=["slow service"],
            review_excerpt="Great experience overall!",            sentiment_distribution=SentimentDistribution(
                positive=0.7,
                negative=0.1,
                neutral=0.2
            ),
            metadata=StoreInsightMetadata(
                reviews_analyzed=50,
                date_range="2023-01-01 to 2023-01-31"
            )
        )
        
        assert insight.store_id == "test_001"
        assert insight.rating == 4.2
        assert insight.review_count == 50
        assert len(insight.themes_positive) == 2
        assert len(insight.themes_negative) == 1
    
    def test_trending_issues_identification(self):
        """Test trending issues identification."""
        aggregator = DataAggregator()
        
        # Create mock insights with common negative themes
        insights = [
            StoreInsight(
                store_id="store_001",
                collection_date=date.today(),
                rating=3.0,
                review_count=20,
                themes_positive=["location"],
                themes_negative=["service", "cleanliness"],
                review_excerpt="Poor service",
                sentiment_distribution=SentimentDistribution(positive=0.2, negative=0.5, neutral=0.3),                metadata=StoreInsightMetadata(
                    reviews_analyzed=20,
                    date_range="2024-01-01 to 2024-01-07",
                    api_calls=5
                )
            ),
            StoreInsight(
                store_id="store_002",
                collection_date=date.today(),
                rating=2.8,
                review_count=30,
                themes_positive=["products"],
                themes_negative=["service", "staff"],
                review_excerpt="Unhelpful staff",
                sentiment_distribution=SentimentDistribution(positive=0.3, negative=0.4, neutral=0.3),
                metadata=StoreInsightMetadata(
                    reviews_analyzed=30,
                    date_range="2024-01-01 to 2024-01-07",
                    api_calls=8
                )
            )
        ]
        
        trending_issues = aggregator._identify_trending_issues(insights)
        
        assert isinstance(trending_issues, list)
        assert "service" in trending_issues  # Should appear as a trending issue
