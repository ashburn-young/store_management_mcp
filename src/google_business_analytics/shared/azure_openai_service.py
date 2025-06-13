"""Azure OpenAI service for enhanced text analysis and insight generation."""

import json
import logging
import os
from typing import Dict, List, Any, Optional
from openai import AzureOpenAI

from ..shared.config import config

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """Service for Azure OpenAI integration with enhanced analytics capabilities."""
    
    def __init__(self):
        """Initialize Azure OpenAI client."""
        self.client: Optional[AzureOpenAI] = None
        
        # Get deployment names with fallback capability
        self.advanced_deployment = config.get('azure_openai.deployment_name_advanced', os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME_ADVANCED', 'gpt-4o'))
        self.standard_deployment = config.get('azure_openai.deployment_name', os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o'))
        
        self.max_tokens = config.get('azure_openai.max_tokens', 1000)
        self.temperature = config.get('azure_openai.temperature', 0.1)
        self._initialize_client()
    def _initialize_client(self) -> None:
        """Initialize the Azure OpenAI client using API key authentication."""
        try:
            # Load environment variables directly
            from dotenv import load_dotenv
            load_dotenv()
            
            # Get values directly from environment, bypassing config system
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
            
            logger.info(f"[DEBUG] Azure OpenAI endpoint: {endpoint}")
            logger.info(f"[DEBUG] Azure OpenAI deployment: {self.standard_deployment}")
            logger.info(f"[DEBUG] Azure OpenAI API version: {api_version}")
            logger.info(f"[DEBUG] Azure OpenAI API key present: {'YES' if api_key and len(api_key) > 10 else 'NO'}")
            
            if not endpoint or not api_key:
                logger.warning("Azure OpenAI endpoint or API key not configured. Using fallback TextBlob.")
                return
            
            try:
                # Initialize with minimal parameters to avoid compatibility issues
                self.client = AzureOpenAI(
                    azure_endpoint=endpoint,
                    api_key=api_key,
                    api_version=api_version
                )
                
                # Test the client with a simple request
                logger.info("Testing Azure OpenAI client with simple request...")
                test_response = self.client.chat.completions.create(
                    model=self.standard_deployment,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5,
                    temperature=0.1
                )
                logger.info(f"✅ Azure OpenAI client test successful: {test_response.choices[0].message.content}")
                
            except Exception as inner_e:
                logger.error(f"[DEBUG] Exception during AzureOpenAI init or test: {inner_e}")
                logger.error(f"[DEBUG] Exception type: {type(inner_e)}")
                logger.error(f"[DEBUG] Exception args: {inner_e.args}")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            logger.error(f"[DEBUG] Outer exception type: {type(e)}")
            logger.error(f"[DEBUG] Outer exception args: {e.args}")
            self.client = None
    
    def analyze_sentiment_advanced(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform advanced sentiment analysis on reviews using Azure OpenAI."""
        if not self.client:
            logger.warning("Azure OpenAI not available, falling back to basic analysis")
            return self._fallback_sentiment_analysis(reviews)
        
        try:
            # Prepare review texts for analysis
            review_texts = [review.get('text', '')[:500] for review in reviews[:10]]  # Limit for token efficiency
            combined_text = "\n---\n".join(review_texts)
            
            prompt = f"""
Analyze the sentiment of these customer reviews for a business location. Provide a detailed analysis in JSON format.

Reviews:
{combined_text}

Please analyze and return a JSON response with:
1. overall_sentiment: number from -1 (very negative) to 1 (very positive)
2. sentiment_distribution: {{"positive": float, "neutral": float, "negative": float}} (percentages as decimals)
3. emotional_themes: list of specific emotions detected (e.g., "frustrated", "delighted", "concerned")
4. confidence: number from 0 to 1 indicating analysis confidence
5. key_sentiment_drivers: list of main factors influencing sentiment

Return only valid JSON, no additional text.
"""
            
            # Try advanced deployment first, fall back to standard if it fails
            try:
                response = self.client.chat.completions.create(
                    model=self.advanced_deployment,
                    messages=[
                        {"role": "system", "content": "You are an expert sentiment analyst for business reviews. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
            except Exception as model_error:
                logger.warning(f"Failed to use advanced model {self.advanced_deployment}, falling back to {self.standard_deployment}: {model_error}")
                response = self.client.chat.completions.create(
                    model=self.standard_deployment,
                    messages=[
                        {"role": "system", "content": "You are an expert sentiment analyst for business reviews. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Advanced sentiment analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Azure OpenAI sentiment analysis failed: {e}")
            return self._fallback_sentiment_analysis(reviews)
    
    def answer_store_question(self, store_insight: Dict[str, Any], question: str) -> str:
        """Answer a specific question about a store using AI analysis."""
        if not self.client:
            logger.warning("Azure OpenAI not available, using fallback response")
            return "Sorry, I can't answer your question at the moment. The AI service is unavailable."
        
        try:
            # Prepare store context
            store_context = {
                "store_id": store_insight.get("store_id", "Unknown"),
                "name": store_insight.get("name", "Unknown Store"),
                "rating": store_insight.get("rating", 0),
                "review_count": store_insight.get("review_count", 0),
                "positive_themes": store_insight.get("themes_positive", [])[:5],
                "negative_themes": store_insight.get("themes_negative", [])[:5],
                "location": store_insight.get("location", {}),
                "recent_trends": store_insight.get("trends", {})
            }
            
            prompt = f"""
You are an AI assistant helping analyze business performance data for Williams Sonoma stores. Answer the user's question based on the store data provided.

Store Data:
{json.dumps(store_context, indent=2)}

User Question: {question}

Provide a helpful, informative answer based on the available data. If the question cannot be answered with the provided data, explain what information is missing. Keep your response concise but detailed, and focus on actionable insights when possible.
"""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.advanced_deployment,
                    messages=[
                        {"role": "system", "content": "You are a business analyst helping interpret store performance data. Be helpful, accurate, and concise."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
            except Exception as model_error:
                logger.warning(f"Failed to use advanced model {self.advanced_deployment}, falling back to {self.standard_deployment}: {model_error}")
                response = self.client.chat.completions.create(
                    model=self.standard_deployment,
                    messages=[
                        {"role": "system", "content": "You are a business analyst helping interpret store performance data. Be helpful, accurate, and concise."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Successfully answered store question: {question[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Failed to answer store question: {e}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"
    
    def generate_store_summary(self, store_insight: Dict[str, Any]) -> str:
        """Generate a comprehensive summary of store performance."""
        if not self.client:
            logger.warning("Azure OpenAI not available, using fallback response")
            return "AI-powered analysis is currently unavailable."
        
        try:
            # Prepare store context
            store_context = {
                "store_id": store_insight.get("store_id", "Unknown"),
                "name": store_insight.get("name", "Unknown Store"),
                "rating": store_insight.get("rating", 0),
                "review_count": store_insight.get("review_count", 0),
                "positive_themes": store_insight.get("themes_positive", [])[:5],
                "negative_themes": store_insight.get("themes_negative", [])[:5],
                "location": store_insight.get("location", {}),
                "recent_trends": store_insight.get("trends", {})
            }
            
            prompt = f"""
Create a comprehensive business summary for this Williams Sonoma store based on the performance data.

Store Data:
{json.dumps(store_context, indent=2)}

Generate a professional executive summary that includes:
1. Overall performance assessment
2. Key strengths and opportunities
3. Customer satisfaction insights
4. Operational recommendations
5. Priority action items

Keep the summary concise but informative, focusing on actionable business insights.
"""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.advanced_deployment,
                    messages=[
                        {"role": "system", "content": "You are a senior business analyst creating executive summaries for retail store performance. Be professional, concise, and actionable."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.2
                )
            except Exception as model_error:
                logger.warning(f"Failed to use advanced model {self.advanced_deployment}, falling back to {self.standard_deployment}: {model_error}")
                response = self.client.chat.completions.create(
                    model=self.standard_deployment,
                    messages=[
                        {"role": "system", "content": "You are a senior business analyst creating executive summaries for retail store performance. Be professional, concise, and actionable."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.2
                )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Successfully generated store summary for {store_insight.get('name', 'Unknown')}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate store summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _fallback_sentiment_analysis(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback sentiment analysis using basic techniques."""
        if not reviews:
            return {
                "overall_sentiment": 0.0,
                "sentiment_distribution": {"positive": 0.33, "neutral": 0.34, "negative": 0.33},
                "emotional_themes": ["neutral"],
                "confidence": 0.1,
                "key_sentiment_drivers": ["insufficient data"]
            }
        
        # Basic sentiment analysis based on ratings
        ratings = [review.get('rating', 3) for review in reviews if 'rating' in review]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            overall_sentiment = (avg_rating - 3) / 2  # Convert 1-5 scale to -1 to 1
            
            positive_count = sum(1 for r in ratings if r >= 4)
            negative_count = sum(1 for r in ratings if r <= 2)
            neutral_count = len(ratings) - positive_count - negative_count
            
            total = len(ratings)
            sentiment_distribution = {
                "positive": positive_count / total,
                "neutral": neutral_count / total,
                "negative": negative_count / total
            }
        else:
            overall_sentiment = 0.0
            sentiment_distribution = {"positive": 0.33, "neutral": 0.34, "negative": 0.33}
        
        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_distribution": sentiment_distribution,
            "emotional_themes": ["mixed reactions"],
            "confidence": 0.3,
            "key_sentiment_drivers": ["basic rating analysis"]
        }
