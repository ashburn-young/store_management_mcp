#!/usr/bin/env python3
"""Demo script to test the Google Business Analytics MCP servers."""

import asyncio
import json
from typing import Dict, Any

# Mock MCP client for testing
class MockMCPClient:
    """Mock MCP client for testing purposes."""
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock tool call that simulates MCP server responses."""
        print(f"🔧 Calling tool '{tool_name}' on {self.server_name}")
        print(f"📥 Arguments: {json.dumps(arguments, indent=2)}")
        
        # Simulate different tool responses
        if tool_name == "collect_store_data":
            return {
                "success": True,
                "data": {
                    "store_id": arguments.get("store_id", "test_store"),
                    "reviews": [
                        {
                            "review_id": "demo_001",
                            "rating": 5,
                            "text": "Great service and quality!",
                            "date": "2024-01-15T10:00:00Z"
                        }
                    ],
                    "qna": [
                        {
                            "question": "What are your hours?",
                            "answer": "9 AM to 9 PM daily",
                            "category": "hours"
                        }
                    ]
                }
            }
        elif tool_name == "generate_store_insights":
            return {
                "success": True,
                "insights": {
                    "store_id": arguments.get("store_id", "test_store"),
                    "avg_rating": 4.2,
                    "total_reviews": 25,
                    "sentiment_score": 0.65,
                    "themes": [
                        {"theme": "Service", "frequency": 8, "sentiment": "positive"},
                        {"theme": "Quality", "frequency": 6, "sentiment": "positive"}
                    ]
                }
            }
        elif tool_name == "aggregate_insights":
            return {
                "success": True,
                "executive_snapshot": {
                    "total_stores": 3,
                    "overall_rating": 4.1,
                    "key_insights": [
                        "Overall customer satisfaction is high",
                        "Service quality is a key differentiator"
                    ],
                    "alerts": [
                        {
                            "severity": "medium",
                            "message": "Store B needs attention - rating drop detected"
                        }
                    ]
                }
            }
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}


async def demo_collection_agent():
    """Demo the collection agent functionality."""
    print("\n" + "="*60)
    print("🏪 DEMO: Collection Agent")
    print("="*60)
    
    client = MockMCPClient("Collection Agent")
    
    # Test data collection
    result = await client.call_tool("collect_store_data", {
        "store_id": "demo_store_001",
        "date_range": "last_30_days"
    })
    
    print("📊 Collection Result:")
    print(json.dumps(result, indent=2))
    
    # Test insight generation
    insight_result = await client.call_tool("generate_store_insights", {
        "store_id": "demo_store_001",
        "store_data": result.get("data", {})
    })
    
    print("\n💡 Insights Result:")
    print(json.dumps(insight_result, indent=2))


async def demo_aggregation_agent():
    """Demo the aggregation agent functionality."""
    print("\n" + "="*60)
    print("📈 DEMO: Aggregation Agent")
    print("="*60)
    
    client = MockMCPClient("Aggregation Agent")
    
    # Mock multiple store insights
    store_insights = [
        {
            "store_id": "store_001",
            "avg_rating": 4.5,
            "sentiment_score": 0.7,
            "total_reviews": 30
        },
        {
            "store_id": "store_002", 
            "avg_rating": 3.2,
            "sentiment_score": 0.1,
            "total_reviews": 20
        },
        {
            "store_id": "store_003",
            "avg_rating": 4.8,
            "sentiment_score": 0.9,
            "total_reviews": 40
        }
    ]
    
    result = await client.call_tool("aggregate_insights", {
        "store_insights": store_insights,
        "time_period": "last_30_days"
    })
    
    print("📊 Executive Summary:")
    print(json.dumps(result, indent=2))


async def demo_dashboard_integration():
    """Demo dashboard data integration."""
    print("\n" + "="*60)
    print("📊 DEMO: Dashboard Integration")
    print("="*60)
    
    print("🌐 Dashboard Features:")
    print("- Real-time store performance metrics")
    print("- Executive alerts and insights")
    print("- Interactive charts and visualizations")
    print("- Store-level detail views")
    print("- Trending themes analysis")
    
    print("\n🔗 Dashboard URL: http://localhost:8501")
    print("📁 Mock data location: data/")
    print("⚙️ Configuration: config/config.yaml")


async def main():
    """Run the complete demo."""
    print("🌟 Google Business Analytics MCP Server Demo")
    print("="*60)
    print("This demo simulates the MCP server functionality")
    print("using mock data and responses.")
    
    try:
        await demo_collection_agent()
        await demo_aggregation_agent()
        await demo_dashboard_integration()
        
        print("\n" + "="*60)
        print("✅ Demo completed successfully!")
        print("="*60)
        print("\n💡 Next Steps:")
        print("1. Start the actual MCP servers: python scripts/start.py")
        print("2. Open the dashboard: http://localhost:8501")
        print("3. Run tests: python -m pytest tests/ -v")
        print("4. Configure real Google API credentials in .env")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
