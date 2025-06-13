"""Data processor for converting raw Google Business data into structured insights."""

import asyncio
import logging
from collections import Counter
from datetime import date
from typing import Any, Dict, List
import re

from textblob import TextBlob

from ..shared.schemas import StoreInsight, SentimentDistribution, StoreInsightMetadata
from ..shared.azure_openai_service import AzureOpenAIService
from ..shared.config import config

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes raw Google Business data into structured insights."""
    
    def __init__(self):
        self.positive_keywords = {
            "staff", "service", "helpful", "friendly", "clean", "fast", "good", 
            "great", "excellent", "recommend", "love", "amazing", "best"
        }
        
        self.negative_keywords = {
            "slow", "rude", "dirty", "expensive", "crowded", "wait", "long", 
            "poor", "bad", "terrible", "worst", "disappointing", "awful"
        }
          # Initialize Azure OpenAI service for enhanced analytics
        self.azure_openai = AzureOpenAIService()
        self.use_azure_openai = config.get('azure_openai.enabled', True)
    
    async def process_store_data(self, store_data: Dict[str, Any]) -> StoreInsight:
        """Process raw store data into a structured insight."""
        store_id = store_data["store_id"]
        reviews = store_data.get("reviews", [])
        
        logger.info(f"Processing {len(reviews)} reviews for store {store_id}")
        
        # Extract themes and sentiments
        positive_themes = await self._extract_themes(reviews, sentiment_filter="positive")
        negative_themes = await self._extract_themes(reviews, sentiment_filter="negative")
        
        # Calculate sentiment distribution
        sentiment_dist = await self._calculate_sentiment_distribution(reviews)
        
        # Generate representative excerpt
        excerpt = self._generate_excerpt(reviews)
        
        # Create metadata
        metadata = StoreInsightMetadata(
            reviews_analyzed=len(reviews),
            date_range=self._get_date_range(reviews),
            api_calls=store_data.get("collection_metadata", {}).get("api_calls", 0)
        )
        
        return StoreInsight(
            store_id=store_id,
            collection_date=date.today(),
            rating=store_data["rating"],
            review_count=store_data["review_count"],
            themes_positive=positive_themes,
            themes_negative=negative_themes,
            review_excerpt=excerpt,
            sentiment_distribution=sentiment_dist,
            metadata=metadata
        )
    async def _extract_themes(self, reviews: List[Dict[str, Any]], sentiment_filter: str = None) -> List[str]:
        """Extract common themes from reviews using Azure OpenAI or fallback."""
        
        # Filter reviews by sentiment if specified
        if sentiment_filter:
            filtered_reviews = [r for r in reviews if r.get("sentiment") == sentiment_filter]
        else:
            filtered_reviews = reviews
        
        if not filtered_reviews:
            return []
        
        # Try Azure OpenAI first for intelligent theme extraction
        if self.use_azure_openai and config.get('azure_openai.use_for_themes', True):
            try:
                advanced_themes = await self.azure_openai.extract_themes_intelligent(filtered_reviews)
                
                # Extract themes based on sentiment filter
                if sentiment_filter == "positive":
                    themes_list = advanced_themes.get('positive_themes', [])
                elif sentiment_filter == "negative":
                    themes_list = advanced_themes.get('negative_themes', [])
                else:
                    # Combine both positive and negative themes
                    pos_themes = advanced_themes.get('positive_themes', [])
                    neg_themes = advanced_themes.get('negative_themes', [])
                    themes_list = pos_themes + neg_themes
                
                return themes_list[:5]  # Return top 5 themes
                
            except Exception as e:
                logger.warning(f"Azure OpenAI theme extraction failed, using fallback: {e}")
          # Fallback to keyword-based extraction
        # Combine all review text
        all_text = " ".join([r.get("text", "") for r in filtered_reviews])
        
        # Extract themes using a combination of keyword matching and n-grams
        themes = Counter()
        
        # Use pre-existing themes if available
        for review in filtered_reviews:
            review_themes = review.get("themes", [])
            for theme in review_themes:
                themes[theme] += 1
        
        # If no pre-existing themes, extract from text
        if not themes:
            themes = self._extract_themes_from_text(all_text, sentiment_filter)
        
        # Return top themes
        return [theme for theme, count in themes.most_common(5)]
    
    def _extract_themes_from_text(self, text: str, sentiment_filter: str = None) -> Counter:
        """Extract themes from raw text using NLP."""
        themes = Counter()
        
        # Clean and normalize text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Define theme patterns based on sentiment
        if sentiment_filter == "positive":
            patterns = [
                (r'\b(staff|employee|worker)s?\b.*\b(helpful|friendly|nice|great)\b', "helpful staff"),
                (r'\b(clean|tidy|neat)\b.*\b(store|location|place)\b', "clean store"),
                (r'\b(fast|quick|speedy)\b.*\b(service|checkout)\b', "fast service"),
                (r'\b(good|great|excellent)\b.*\b(selection|variety)\b', "good selection"),
                (r'\b(convenient|easy)\b.*\b(location|parking)\b', "convenient location"),
            ]
        elif sentiment_filter == "negative":
            patterns = [
                (r'\b(long|slow)\b.*\b(line|wait|checkout)\b', "long checkout lines"),
                (r'\b(parking)\b.*\b(limited|hard|difficult|full)\b', "limited parking"),
                (r'\b(crowded|busy|packed)\b.*\b(aisle|store)\b', "crowded aisles"),
                (r'\b(slow|poor)\b.*\b(service|staff)\b', "slow service"),
                (r'\b(out of stock|empty|sold out)\b', "out of stock items"),                (r'\b(expensive|pricey|high)\b.*\b(price|cost)\b', "high prices"),
            ]
        else:
            patterns = []
        
        # Apply patterns
        for pattern, theme in patterns:
            if re.search(pattern, text):
                themes[theme] += text.count(theme.split()[0])  # Count primary keyword
        
        return themes
    
    async def _calculate_sentiment_distribution(self, reviews: List[Dict[str, Any]]) -> SentimentDistribution:
        """Calculate sentiment distribution from reviews using Azure OpenAI or fallback."""
        
        if not reviews:
            return SentimentDistribution(positive=0, neutral=0, negative=0)
        
        # Try Azure OpenAI first for enhanced analysis
        if self.use_azure_openai and config.get('azure_openai.use_for_sentiment', True):
            try:
                advanced_sentiment = await self.azure_openai.analyze_sentiment_advanced(reviews)
                sentiment_dist = advanced_sentiment.get('sentiment_distribution', {})
                
                # Convert to our format (percentages as integers)
                return SentimentDistribution(
                    positive=round(sentiment_dist.get('positive', 0) * 100),
                    neutral=round(sentiment_dist.get('neutral', 0) * 100),
                    negative=round(sentiment_dist.get('negative', 0) * 100)
                )
            except Exception as e:
                logger.warning(f"Azure OpenAI sentiment analysis failed, using fallback: {e}")
        
        # Fallback to TextBlob analysis
        sentiment_counts = Counter()
        
        for review in reviews:
            # Use existing sentiment if available
            sentiment = review.get("sentiment")
            
            if not sentiment:
                # Analyze sentiment using TextBlob
                blob = TextBlob(review.get("text", ""))
                polarity = blob.sentiment.polarity
                
                if polarity > 0.1:
                    sentiment = "positive"
                elif polarity < -0.1:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
            
            sentiment_counts[sentiment] += 1
        
        total = len(reviews)
        return SentimentDistribution(
            positive=round((sentiment_counts["positive"] / total) * 100),
            neutral=round((sentiment_counts["neutral"] / total) * 100),
            negative=round((sentiment_counts["negative"] / total) * 100)
        )
    
    def _generate_excerpt(self, reviews: List[Dict[str, Any]]) -> str:
        """Generate a representative excerpt from reviews."""
        
        if not reviews:
            return "No reviews available."
        
        # Find a good representative review (moderate length, recent)
        candidates = [
            r for r in reviews 
            if r.get("text") and 50 <= len(r["text"]) <= 200
        ]
        
        if not candidates:
            candidates = [r for r in reviews if r.get("text")]
        
        if not candidates:
            return "No review text available."
        
        # Sort by date (newest first) and take the first one
        candidates.sort(key=lambda r: r.get("date", ""), reverse=True)
        return candidates[0]["text"]
    
    def _get_date_range(self, reviews: List[Dict[str, Any]]) -> str:
        """Get the date range of analyzed reviews."""
        
        if not reviews:
            return "No reviews"
        
        dates = [r.get("date") for r in reviews if r.get("date")]
        
        if not dates:
            return "No dates available"
        
        dates.sort()
        
        if len(dates) == 1:
            return dates[0]
        else:
            return f"{dates[0]} to {dates[-1]}"
