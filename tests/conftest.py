"""Test configuration and utilities."""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List

# Test data constants
MOCK_STORE_DATA = [
    {
        "store_id": "test_store_001",
        "name": "Test Store Downtown",
        "address": "123 Test St, Test City, TC 12345",
        "phone": "+1-555-TEST-001",
        "manager": "Test Manager",
        "category": "Test Category",
        "opening_date": "2020-01-01",
        "square_footage": 2000,
        "employee_count": 10
    }
]

MOCK_REVIEW_DATA = [
    {
        "store_id": "test_store_001", 
        "review_id": "test_rev_001",
        "rating": 5,
        "text": "Excellent service and great products!",
        "date": "2024-01-15T10:00:00Z",
        "reviewer_name": "Test Reviewer",
        "verified_purchase": True
    },
    {
        "store_id": "test_store_001",
        "review_id": "test_rev_002", 
        "rating": 2,
        "text": "Poor customer service, very disappointed.",
        "date": "2024-01-14T15:00:00Z",
        "reviewer_name": "Another Reviewer",
        "verified_purchase": True
    }
]

MOCK_QNA_DATA = [
    {
        "store_id": "test_store_001",
        "question": "What are your hours?",
        "answer": "We are open 9 AM to 9 PM daily.",
        "date": "2024-01-15T08:00:00Z",
        "category": "hours"
    }
]


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory with test configuration files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir()
        
        # Create test config file
        config_content = {
            "google_api": {
                "api_key": "test_api_key",
                "service_account_file": "test_service_account.json",
                "requests_per_minute": 10,
                "batch_size": 5
            },
            "processing": {
                "sentiment_threshold_positive": 0.1,
                "sentiment_threshold_negative": -0.1,
                "min_theme_frequency": 2
            },
            "development": {
                "use_mock_data": True,
                "mock_data_path": str(Path(temp_dir) / "data"),
                "enable_debug_mode": True
            }
        }
        
        with open(config_dir / "config.yaml", 'w') as f:
            import yaml
            yaml.dump(config_content, f)
        
        yield temp_dir


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory with test data files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir) / "data"
        data_dir.mkdir()
        
        # Write test data files
        with open(data_dir / "mock_store_info.json", 'w') as f:
            json.dump(MOCK_STORE_DATA, f)
        
        with open(data_dir / "mock_reviews.json", 'w') as f:
            json.dump(MOCK_REVIEW_DATA, f)
        
        with open(data_dir / "mock_qna.json", 'w') as f:
            json.dump(MOCK_QNA_DATA, f)
        
        yield data_dir


@pytest.fixture
def sample_store_insights():
    """Sample store insights data for testing."""
    return {
        "store_id": "test_store_001",
        "store_name": "Test Store Downtown",
        "collection_date": "2024-01-15T12:00:00Z",
        "reviews_summary": {
            "total_reviews": 2,
            "avg_rating": 3.5,
            "rating_distribution": {"1": 0, "2": 1, "3": 0, "4": 0, "5": 1},
            "recent_reviews": MOCK_REVIEW_DATA
        },
        "sentiment_analysis": {
            "overall_sentiment": 0.25,
            "positive_reviews": 1,
            "negative_reviews": 1,
            "neutral_reviews": 0
        },
        "themes_and_topics": [
            {
                "theme": "Service",
                "frequency": 2,
                "sentiment": "mixed",
                "sample_mentions": ["service", "customer service"]
            }
        ],
        "qna_insights": {
            "total_questions": 1,
            "common_categories": ["hours"],
            "recent_qna": MOCK_QNA_DATA
        }
    }


@pytest.fixture
def sample_executive_snapshot():
    """Sample executive snapshot data for testing."""
    return {
        "snapshot_id": "exec_snap_001",
        "generated_at": "2024-01-15T12:00:00Z",
        "time_period": {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-15T23:59:59Z"
        },
        "overall_performance": {
            "total_stores": 1,
            "avg_rating_across_stores": 3.5,
            "total_reviews": 2,
            "overall_sentiment": 0.25
        },
        "store_performance": [
            {
                "store_id": "test_store_001",
                "store_name": "Test Store Downtown", 
                "avg_rating": 3.5,
                "total_reviews": 2,
                "sentiment_score": 0.25,
                "performance_category": "needs_attention"
            }
        ],
        "key_insights": [
            {
                "insight_type": "performance",
                "severity": "medium",
                "message": "Mixed customer sentiment detected",
                "affected_stores": ["test_store_001"]
            }
        ],
        "trending_themes": [
            {
                "theme": "Service",
                "frequency": 2,
                "trend": "stable",
                "sentiment": "mixed"
            }
        ],
        "alerts": [
            {
                "alert_id": "alert_001",
                "severity": "medium",
                "type": "sentiment",
                "message": "Store has equal positive and negative reviews",
                "store_id": "test_store_001",
                "created_at": "2024-01-15T12:00:00Z"
            }
        ]
    }
