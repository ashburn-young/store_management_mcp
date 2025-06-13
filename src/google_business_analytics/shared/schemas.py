"""Pydantic data models for Google Business Analytics."""

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class SentimentDistribution(BaseModel):
    """Distribution of sentiment across reviews."""
    positive: float = Field(ge=0, le=1.0, description="Percentage of positive reviews (0.0-1.0)")
    neutral: float = Field(ge=0, le=1.0, description="Percentage of neutral reviews (0.0-1.0)") 
    negative: float = Field(ge=0, le=1.0, description="Percentage of negative reviews (0.0-1.0)")
    
    @model_validator(mode='after')
    def validate_total(self):
        """Ensure percentages don't exceed 100% total."""
        total = self.positive + self.neutral + self.negative
        if total > 1.0:
            raise ValueError('Total sentiment percentages cannot exceed 100%')
        return self


class StoreInsightMetadata(BaseModel):
    """Metadata about store insight collection."""
    reviews_analyzed: int = Field(ge=0, description="Number of reviews analyzed")
    date_range: str = Field(description="Date range of reviews analyzed")
    api_calls: Optional[int] = Field(default=None, ge=0, description="Number of API calls made")


class StoreInsight(BaseModel):
    """Store-level insights from Google Business data."""
    store_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$", description="Unique store identifier")
    collection_date: date = Field(description="Date when data was collected")
    rating: float = Field(ge=1.0, le=5.0, description="Overall store rating")
    review_count: int = Field(ge=0, description="Total number of reviews")
    themes_positive: List[str] = Field(description="Positive themes from reviews")
    themes_negative: List[str] = Field(description="Negative themes from reviews")
    review_excerpt: Optional[str] = Field(description="Representative review excerpt")
    sentiment_distribution: SentimentDistribution
    metadata: StoreInsightMetadata


class NationalKPIs(BaseModel):
    """National-level key performance indicators."""
    avg_rating: float = Field(ge=0.0, le=5.0, description="National average rating")
    total_stores: int = Field(ge=0, description="Total stores analyzed")
    nps_equivalent: float = Field(ge=-100, le=100, description="Net Promoter Score equivalent")
    total_reviews: Optional[int] = Field(default=None, ge=0, description="Total reviews across all stores")


class RegionalSummary(BaseModel):
    """Regional aggregation of store data."""
    region: str = Field(description="Region name")
    avg_rating: float = Field(ge=1.0, le=5.0, description="Regional average rating")
    store_count: int = Field(ge=0, description="Number of stores in region")
    top_positive_theme: Optional[str] = Field(description="Most common positive theme")
    top_concern: Optional[str] = Field(description="Most common negative theme")


class Alert(BaseModel):
    """Alert for significant changes or issues."""
    store_id: str = Field(description="Store identifier")
    alert_type: str = Field(description="Type of alert", pattern=r"^(rating_drop|negative_trend|volume_spike)$")
    severity: str = Field(description="Alert severity", pattern=r"^(low|medium|high|critical)$")
    current_rating: Optional[float] = Field(ge=1.0, le=5.0, description="Current rating")
    previous_rating: Optional[float] = Field(ge=1.0, le=5.0, description="Previous rating")
    change: Optional[float] = Field(description="Rating change amount")
    description: Optional[str] = Field(description="Human-readable description")


class PerformanceMetrics(BaseModel):
    """Performance metrics for processing."""
    processing_time_seconds: Optional[float] = Field(ge=0, description="Processing time")
    stores_processed: Optional[int] = Field(ge=0, description="Stores successfully processed")
    errors_encountered: Optional[int] = Field(ge=0, description="Number of errors")


class ExecutiveSnapshot(BaseModel):
    """Executive-level aggregated insights."""
    snapshot_date: date = Field(description="Date of snapshot")
    national_kpis: NationalKPIs
    regional_summary: List[RegionalSummary]
    alerts: List[Alert]
    trending_issues: List[str] = Field(description="Trending negative themes")
    data_freshness: datetime = Field(description="Last data update timestamp")
    performance_metrics: Optional[PerformanceMetrics] = Field(description="Processing metrics")
