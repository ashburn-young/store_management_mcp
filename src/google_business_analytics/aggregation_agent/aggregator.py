"""Data aggregator for creating executive-level insights from store data."""

import asyncio
import logging
from collections import Counter
from datetime import date, datetime
from typing import List, Dict, Any
import statistics
import random

from ..shared.schemas import (
    ExecutiveSnapshot, StoreInsight, NationalKPIs, RegionalSummary, 
    Alert, PerformanceMetrics
)
from ..shared.azure_openai_service import AzureOpenAIService
from ..shared.config import config

logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregates store-level insights into executive summaries."""
    
    def __init__(self):
        self.alert_thresholds = {
            "rating_drop_critical": 0.5,
            "rating_drop_high": 0.3,
            "rating_drop_medium": 0.2,
            "low_rating_threshold": 3.0
        }
        
        # Initialize Azure OpenAI service for enhanced analytics
        self.azure_openai = AzureOpenAIService()
        self.use_azure_openai = config.get('azure_openai.enabled', True)
    
    async def create_executive_snapshot(self, store_insights: List[StoreInsight]) -> ExecutiveSnapshot:
        """Create executive snapshot from store insights."""
        
        start_time = datetime.now()
        
        try:
            # Calculate national KPIs
            national_kpis = self._calculate_national_kpis(store_insights)
            
            # Create regional summaries
            regional_summary = self._create_regional_summaries(store_insights)
            
            # Generate alerts - use Azure OpenAI if available
            if self.use_azure_openai and config.get('azure_openai.use_for_alerts', True):
                try:
                    # Get historical insights for comparison (mock for now)
                    historical_data = {"previous_period": self._create_historical_mock(store_insights)}
                    current_data = {"current_period": [s.dict() for s in store_insights[:20]]}
                    
                    # Generate enhanced alerts with Azure OpenAI
                    advanced_alerts = await self.azure_openai.generate_smart_alerts(current_data, historical_data)
                    
                    # Convert to Alert schema
                    alerts = []
                    for adv_alert in advanced_alerts:
                        alerts.append(Alert(
                            alert_id=adv_alert.get("alert_id", f"alert_{len(alerts)}"),
                            severity=adv_alert.get("severity", "medium"),
                            title=adv_alert.get("title", "Alert"),
                            description=adv_alert.get("description", ""),
                            stores_affected=adv_alert.get("affected_stores", []),
                            recommended_action=adv_alert.get("recommended_actions", [])[0] if adv_alert.get("recommended_actions") else ""
                        ))
                    
                    logger.info(f"Generated {len(alerts)} enhanced alerts using Azure OpenAI")
                except Exception as e:
                    logger.warning(f"Azure OpenAI alert generation failed, using fallback: {e}")
                    alerts = self._generate_alerts(store_insights)
            else:
                # Use traditional alert generation
                alerts = self._generate_alerts(store_insights)
            
            # Identify trending issues - use Azure OpenAI if available
            if self.use_azure_openai and config.get('azure_openai.use_for_summaries', True):
                try:
                    # Generate enhanced executive summary with Azure OpenAI
                    advanced_summary = await self.azure_openai.generate_executive_summary([s.dict() for s in store_insights[:30]])
                    
                    # Extract trending issues from the enhanced summary
                    trending_issues = advanced_summary.get("key_insights", [])
                    
                    # Add additional insights if available
                    if advanced_summary.get("opportunities"):
                        trending_issues.extend(advanced_summary.get("opportunities", [])[:3])
                    
                    logger.info(f"Generated enhanced trending issues using Azure OpenAI")
                except Exception as e:
                    logger.warning(f"Azure OpenAI trending issues generation failed, using fallback: {e}")
                    trending_issues = self._identify_trending_issues(store_insights)
            else:
                # Use traditional trending issues identification
                trending_issues = self._identify_trending_issues(store_insights)
            
            # Calculate performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            performance_metrics = PerformanceMetrics(
                processing_time_seconds=processing_time,
                stores_processed=len(store_insights),
                errors_encountered=0  # Would track actual errors in production
            )
            
            snapshot = ExecutiveSnapshot(
                snapshot_date=date.today(),
                national_kpis=national_kpis,
                regional_summary=regional_summary,
                alerts=alerts,
                trending_issues=trending_issues,
                data_freshness=datetime.now(),
                performance_metrics=performance_metrics
            )
            
            logger.info(f"Generated executive snapshot with {len(alerts)} alerts and {len(regional_summary)} regions")            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error creating executive snapshot: {e}")
            raise
    
    def _calculate_national_kpis(self, insights: List[StoreInsight]) -> NationalKPIs:
        """Calculate national-level KPIs."""
        
        if not insights:
            return NationalKPIs(avg_rating=0, total_stores=0, nps_equivalent=0, total_reviews=0)
        
        # Calculate average rating
        ratings = [insight.rating for insight in insights]
        avg_rating = statistics.mean(ratings)
        
        # Calculate total reviews
        total_reviews = sum(insight.review_count for insight in insights)
        
        # Calculate NPS equivalent (simplified calculation)
        # Convert 5-star ratings to NPS-like score
        nps_scores = []
        for insight in insights:
            if insight.rating >= 4.5:
                nps_scores.append(1)  # Promoter
            elif insight.rating >= 3.5:
                nps_scores.append(0)  # Passive
            else:
                nps_scores.append(-1)  # Detractor
        
        nps_equivalent = (sum(nps_scores) / len(nps_scores)) * 100 if nps_scores else 0
        
        return NationalKPIs(
            avg_rating=round(avg_rating, 2),
            total_stores=len(insights),
            nps_equivalent=round(nps_equivalent, 1),
            total_reviews=total_reviews
        )
    
    def _create_regional_summaries(self, insights: List[StoreInsight]) -> List[RegionalSummary]:
        """Create regional summaries from store insights."""
        
        # Group stores by region (mock regions for now)
        regional_data = {}
        
        for insight in insights:
            # Mock region assignment based on store_id pattern
            if insight.store_id.endswith(('1', '2', '3')):
                region = "West Coast"
            elif insight.store_id.endswith(('4', '5', '6')):
                region = "East Coast"
            elif insight.store_id.endswith(('7', '8')):
                region = "Midwest"
            else:
                region = "South"
            
            if region not in regional_data:
                regional_data[region] = []
            regional_data[region].append(insight)
        
        # Create summaries for each region
        summaries = []
        for region, region_insights in regional_data.items():
            avg_rating = statistics.mean([i.rating for i in region_insights])
            
            # Find most common themes
            all_positive_themes = []
            all_negative_themes = []
            
            for insight in region_insights:
                all_positive_themes.extend(insight.themes_positive)
                all_negative_themes.extend(insight.themes_negative)
            
            top_positive = Counter(all_positive_themes).most_common(1)
            top_negative = Counter(all_negative_themes).most_common(1)
            
            summary = RegionalSummary(
                region=region,
                avg_rating=round(avg_rating, 2),
                store_count=len(region_insights),
                top_positive_theme=top_positive[0][0] if top_positive else None,
                top_concern=top_negative[0][0] if top_negative else None
            )
            summaries.append(summary)
        
        return sorted(summaries, key=lambda x: x.avg_rating, reverse=True)
    
    def _generate_alerts(self, insights: List[StoreInsight]) -> List[Alert]:
        """Generate alerts for significant issues."""
        
        alerts = []
        
        # Mock previous ratings for comparison (in production, would load historical data)
        for insight in insights:
            previous_rating = insight.rating + 0.2  # Mock previous rating
            rating_change = insight.rating - previous_rating
            
            # Check for rating drops
            if rating_change <= -self.alert_thresholds["rating_drop_critical"]:
                severity = "critical"
            elif rating_change <= -self.alert_thresholds["rating_drop_high"]:
                severity = "high"
            elif rating_change <= -self.alert_thresholds["rating_drop_medium"]:
                severity = "medium"
            else:
                continue  # No alert needed
            
            alert = Alert(
                store_id=insight.store_id,
                alert_type="rating_drop",
                severity=severity,
                current_rating=insight.rating,
                previous_rating=previous_rating,
                change=round(rating_change, 2),
                description=f"Store rating dropped by {abs(rating_change):.1f} stars"
            )
            alerts.append(alert)
        
        # Check for low ratings
        for insight in insights:
            if insight.rating < self.alert_thresholds["low_rating_threshold"]:
                alert = Alert(
                    store_id=insight.store_id,
                    alert_type="negative_trend",
                    severity="high" if insight.rating < 2.5 else "medium",
                    current_rating=insight.rating,
                    description=f"Store has low rating of {insight.rating} stars"
                )
                alerts.append(alert)
        
        return sorted(alerts, key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.severity], reverse=True)
    
    def _identify_trending_issues(self, insights: List[StoreInsight]) -> List[str]:
        """Identify trending negative themes across all stores."""
        
        # Collect all negative themes
        all_negative_themes = []
        for insight in insights:
            all_negative_themes.extend(insight.themes_negative)
        
        # Count occurrences and find most common
        theme_counts = Counter(all_negative_themes)
        
        # Return top trending issues
        trending = [theme for theme, count in theme_counts.most_common(5)]
        
        return trending
    
    def _create_historical_mock(self, current_insights: List[StoreInsight]) -> List[Dict[str, Any]]:
        """Create mock historical data for comparison.
        
        In a real implementation, this would retrieve actual historical data.
        """
        
        historical = []
        for insight in current_insights[:20]:  # Limit for performance
            # Create slightly modified historical version
            hist_insight = insight.dict()
            
            # Modify some values to create differences
            hist_insight["rating"] = max(1.0, min(5.0, insight.rating + random.uniform(-0.3, 0.3)))
            hist_insight["review_count"] = max(0, insight.review_count - random.randint(5, 20))
            
            # Modify sentiment distribution slightly
            if "sentiment_distribution" in hist_insight:
                sent_dist = hist_insight["sentiment_distribution"]
                sent_dist["positive"] = max(0, min(100, sent_dist["positive"] + random.randint(-10, 10)))
                sent_dist["negative"] = max(0, min(100, sent_dist["negative"] + random.randint(-10, 10)))
                sent_dist["neutral"] = 100 - sent_dist["positive"] - sent_dist["negative"]
            
            historical.append(hist_insight)
        
        return historical
