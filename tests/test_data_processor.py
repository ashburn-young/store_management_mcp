"""Tests for the collection agent data processor."""

import pytest
from datetime import datetime, date
from google_business_analytics.collection_agent.data_processor import DataProcessor
from google_business_analytics.shared.schemas import StoreInsight


class TestDataProcessor:
    """Test cases for the DataProcessor class."""
    
    @pytest.mark.asyncio
    async def test_process_store_data(self):
        """Test processing of complete store data."""
        processor = DataProcessor()
        
        store_data = {
            "store_id": "test_store_001",
            "rating": 4.2,
            "review_count": 50,
            "reviews": [
                {
                    "rating": 5,
                    "text": "Great service and excellent quality!",
                    "date": "2024-01-15T10:00:00Z",
                    "reviewer_name": "Happy Customer",
                    "verified_purchase": True
                },
                {
                    "rating": 2,
                    "text": "Poor customer service, very disappointed.",
                    "date": "2024-01-14T15:00:00Z",
                    "reviewer_name": "Unhappy Customer",
                    "verified_purchase": True
                }
            ]
        }
        
        insights = await processor.process_store_data(store_data)
        
        # Validate the structure
        assert isinstance(insights, StoreInsight)
        assert insights.store_id == "test_store_001"
        assert insights.rating == 4.2
        assert insights.review_count == 50
        assert insights.collection_date == date.today()
        assert isinstance(insights.themes_positive, list)
        assert isinstance(insights.themes_negative, list)
    
    def test_extract_themes_positive(self):
        """Test theme extraction for positive reviews."""
        processor = DataProcessor()
        
        reviews = [
            {
                "text": "Great customer service and helpful staff",
                "sentiment": "positive"
            },
            {
                "text": "Excellent service, very professional staff",
                "sentiment": "positive"
            },
            {
                "text": "Good quality products and fast service",
                "sentiment": "positive"
            }
        ]
        
        themes = processor._extract_themes(reviews, sentiment_filter="positive")
        
        # Should return a list of theme strings
        assert isinstance(themes, list)
        assert len(themes) <= 5  # Limited to top 5
    
    def test_extract_themes_negative(self):
        """Test theme extraction for negative reviews."""
        processor = DataProcessor()
        
        reviews = [
            {
                "text": "Staff was rude and service was slow",
                "sentiment": "negative"
            },
            {
                "text": "Poor service and unhelpful staff",
                "sentiment": "negative"
            }
        ]
        
        themes = processor._extract_themes(reviews, sentiment_filter="negative")
        
        # Should return a list of theme strings
        assert isinstance(themes, list)
        assert len(themes) <= 5  # Limited to top 5
    
    def test_calculate_sentiment_distribution(self):
        """Test sentiment distribution calculation."""
        processor = DataProcessor()
        
        reviews = [
            {"sentiment": "positive"},
            {"sentiment": "positive"},
            {"sentiment": "negative"},
            {"sentiment": "neutral"}
        ]
        
        sentiment_dist = processor._calculate_sentiment_distribution(reviews)
        
        # Check that we get a proper SentimentDistribution object
        assert hasattr(sentiment_dist, 'positive')
        assert hasattr(sentiment_dist, 'negative')
        assert hasattr(sentiment_dist, 'neutral')
        
        # Check that percentages are between 0 and 1
        assert 0 <= sentiment_dist.positive <= 1
        assert 0 <= sentiment_dist.negative <= 1
        assert 0 <= sentiment_dist.neutral <= 1
    
    def test_generate_excerpt(self):
        """Test excerpt generation from reviews."""
        processor = DataProcessor()
        
        reviews = [
            {
                "text": "Great service!",
                "rating": 5
            },
            {
                "text": "Terrible experience, very disappointed.",
                "rating": 1
            },
            {
                "text": "Average quality, nothing special.",
                "rating": 3
            }
        ]
        
        excerpt = processor._generate_excerpt(reviews)
        
        # Should return a string
        assert isinstance(excerpt, str)
        # Should not be empty if there are reviews
        assert len(excerpt) > 0
    
    def test_get_date_range(self):
        """Test date range calculation from reviews."""
        processor = DataProcessor()
        
        reviews = [
            {"date": "2024-01-15T10:00:00Z"},
            {"date": "2024-01-10T15:00:00Z"},
            {"date": "2024-01-20T08:00:00Z"}
        ]
        
        date_range = processor._get_date_range(reviews)
        
        # Should return a string with date range
        assert isinstance(date_range, str)
        assert len(date_range) > 0
        # Should contain "to" to indicate range
        assert "to" in date_range or "-" in date_range
    
    def test_empty_data_handling(self):
        """Test handling of empty or minimal data."""
        processor = DataProcessor()
        
        # Test with empty reviews
        empty_themes = processor._extract_themes([])
        assert isinstance(empty_themes, list)
        assert len(empty_themes) == 0
        
        # Test sentiment distribution with empty reviews
        empty_dist = processor._calculate_sentiment_distribution([])
        assert empty_dist.positive == 0.0
        assert empty_dist.negative == 0.0
        assert empty_dist.neutral == 0.0
        
        # Test excerpt with empty reviews
        empty_excerpt = processor._generate_excerpt([])
        assert isinstance(empty_excerpt, str)
        
        # Test date range with empty reviews
        empty_date_range = processor._get_date_range([])
        assert isinstance(empty_date_range, str)
