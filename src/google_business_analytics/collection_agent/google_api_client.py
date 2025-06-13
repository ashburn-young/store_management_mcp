"""Google API Client for retrieving business data."""

import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
import random

logger = logging.getLogger(__name__)


class GoogleAPIClient:
    """Client for Google Business API interactions."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "mock_api_key"
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
    async def get_store_data(self, store_id: str, days_back: int = 90) -> Dict[str, Any]:
        """
        Get store data from Google Business API.
        
        For now, this returns mock data. In production, this would:
        1. Call Google Places API to get basic store info
        2. Call Google My Business API to get reviews
        3. Handle rate limiting and retries
        """
        logger.info(f"Fetching data for store {store_id} ({days_back} days)")
        
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        # Generate mock data that resembles real Google Business data
        mock_data = self._generate_mock_store_data(store_id, days_back)
        
        return mock_data
    
    def _generate_mock_store_data(self, store_id: str, days_back: int) -> Dict[str, Any]:
        """Generate realistic mock data for testing."""
        
        # Generate mock reviews
        review_count = random.randint(20, 150)
        reviews = []
        
        positive_themes = [
            "helpful staff", "clean store", "fast service", "good selection", 
            "friendly employees", "convenient location", "well organized"
        ]
        
        negative_themes = [
            "long checkout lines", "limited parking", "crowded aisles", 
            "slow service", "out of stock items", "high prices", "poor customer service"
        ]
        
        for i in range(min(review_count, 50)):  # Limit to 50 for processing
            # Generate review with realistic sentiment distribution
            sentiment = random.choices(
                ["positive", "neutral", "negative"],
                weights=[70, 20, 10],  # Most reviews are positive
                k=1
            )[0]
            
            if sentiment == "positive":
                rating = random.randint(4, 5)
                themes = random.sample(positive_themes, random.randint(1, 3))
                text = f"Great experience! {', '.join(themes)}. Would recommend."
            elif sentiment == "negative":
                rating = random.randint(1, 2)
                themes = random.sample(negative_themes, random.randint(1, 2))
                text = f"Disappointing visit. Issues with {', '.join(themes)}."
            else:
                rating = 3
                themes = []
                text = "Average experience, nothing special but acceptable."
            
            review_date = date.today() - timedelta(days=random.randint(0, days_back))
            
            reviews.append({
                "rating": rating,
                "text": text,
                "date": review_date.isoformat(),
                "themes": themes,
                "sentiment": sentiment
            })
        
        # Calculate overall statistics
        ratings = [r["rating"] for r in reviews]
        avg_rating = sum(ratings) / len(ratings) if ratings else 4.0
        
        sentiment_counts = {
            "positive": len([r for r in reviews if r["sentiment"] == "positive"]),
            "neutral": len([r for r in reviews if r["sentiment"] == "neutral"]),
            "negative": len([r for r in reviews if r["sentiment"] == "negative"])
        }
        
        return {
            "store_id": store_id,
            "name": f"PB Store {store_id}",
            "rating": round(avg_rating, 1),
            "review_count": review_count,
            "reviews": reviews,
            "sentiment_stats": sentiment_counts,
            "location": {
                "address": f"123 Main St, City, State",
                "region": random.choice(["West Coast", "East Coast", "Midwest", "South"])
            },
            "collection_metadata": {
                "api_calls": 3,  # Places API + Reviews API calls
                "rate_limit_remaining": 1000,
                "collection_timestamp": datetime.now().isoformat()
            }
        }
    
    async def get_store_reviews(self, place_id: str, days_back: int = 90) -> List[Dict[str, Any]]:
        """Get reviews for a specific place."""
        # In production, this would call the Google My Business API
        store_data = await self.get_store_data(place_id, days_back)
        return store_data.get("reviews", [])
    
    async def get_store_info(self, place_id: str) -> Dict[str, Any]:
        """Get basic store information."""
        # In production, this would call the Google Places API
        store_data = await self.get_store_data(place_id)
        return {
            "place_id": place_id,
            "name": store_data.get("name"),
            "rating": store_data.get("rating"),
            "review_count": store_data.get("review_count"),
            "location": store_data.get("location")
        }
