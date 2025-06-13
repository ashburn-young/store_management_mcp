"""Collection Agent MCP Server

This file implements the MCP (Model Context Protocol) server for data collection.

Why MCP Server?
- MCP is a protocol for tool-based, composable, and language-agnostic AI/analytics workflows.
- It allows this agent to be orchestrated by other MCP clients, LLMs, or pipelines (e.g., for chaining, automation, or dashboard integration).
- The server exposes tools (functions) and resources (data endpoints) in a discoverable, schema-driven way.

What does this file do?
- Connects to Google Business Profile API (via GoogleAPIClient)
- Runs sentiment analysis and theme extraction (via DataProcessor)
- Exposes MCP tools for data collection and status
- Saves processed insights to disk (or optionally to Azure Cosmos DB)

How to adapt for your project:
- Update GoogleAPIClient to use your real Google API credentials and endpoints
- Set up Azure credentials (Cosmos DB, Key Vault, etc.) as needed
- Add/modify tools in @server.list_tools and @server.call_tool for your use case
- Use environment variables for all secrets (see .env)
"""

import asyncio
import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from ..shared.schemas import StoreInsight, SentimentDistribution, StoreInsightMetadata
from .data_processor import DataProcessor
from .google_api_client import GoogleAPIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("collection-agent")


# Main agent class for Google Business data collection
class CollectionAgent:
    """
    Handles all logic for fetching, processing, and saving store insights.
    Extend this class to add new data sources, enrichments, or output targets.
    """
    def __init__(self):
        # GoogleAPIClient: Handles all Google Business Profile API calls.
        # TODO: Update GoogleAPIClient to use your real API credentials and endpoints.
        self.google_client = GoogleAPIClient()
        # DataProcessor: Handles sentiment analysis, theme extraction, etc.
        self.data_processor = DataProcessor()
        # Output directory for processed insights (local JSON, can be replaced with Cosmos DB)
        self.output_dir = Path("data/processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def collect_store_data(self, store_ids: List[str], days_back: int = 90) -> List[StoreInsight]:
        """
        For each store_id, fetches data from Google API, processes it, and appends to results.
        Handles errors per-store so one failure doesn't stop the batch.
        Returns a list of StoreInsight objects (Pydantic models).
        """
        insights = []
        for store_id in store_ids:
            try:
                logger.info(f"Processing store: {store_id}")
                # Get store data from Google API (implement real call in GoogleAPIClient)
                store_data = await self.google_client.get_store_data(store_id, days_back)
                # Process the data into insights (sentiment, themes, etc.)
                insight = await self.data_processor.process_store_data(store_data)
                insights.append(insight)
                logger.info(f"Successfully processed {store_id}")
            except Exception as e:
                logger.error(f"Error processing store {store_id}: {e}")
                continue
        return insights

    async def save_insights(self, insights: List[StoreInsight]) -> str:
        """
        Saves insights to a JSON file (local disk).
        In production, you may want to save to Azure Cosmos DB or Blob Storage instead.
        To use Cosmos DB, add a Cosmos client and call it here.
        """
        timestamp = date.today().strftime("%Y-%m-%d")
        filename = f"store_insights_{timestamp}.json"
        filepath = self.output_dir / filename
        # Convert to JSON-serializable format
        data = [insight.model_dump() for insight in insights]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved {len(insights)} insights to {filepath}")
        return str(filepath)


# Initialize the collection agent
collection_agent = CollectionAgent()


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    Lists available tools for the collection agent.
    These are the main entry points for MCP clients (or LLMs) to call this agent.
    Add new tools here for new data collection or enrichment tasks.
    """
    # Each tool is described with a name, description, and input schema (JSON Schema)
    return [
        types.Tool(
            name="collect_store_insights",
            description="Collect Google Business data and generate store-level insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "store_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of store IDs to collect data for"
                    },
                    "days_back": {
                        "type": "integer",
                        "default": 90,
                        "description": "Number of days back to collect reviews"
                    }
                },
                "required": ["store_ids"]
            }
        ),
        types.Tool(
            name="get_store_status",
            description="Get the current status and recent insights for a store",
            inputSchema={
                "type": "object", 
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "Store ID to check status for"
                    }
                },
                "required": ["store_id"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handles tool calls from MCP clients (or LLMs).
    This is the main entry point for executing a tool (function) by name.
    Add new tool handlers here as you add new tools in list_tools.
    """
    if name == "collect_store_insights":
        # Collect insights for a list of store IDs
        store_ids = arguments.get("store_ids", [])
        days_back = arguments.get("days_back", 90)
        if not store_ids:
            return [types.TextContent(type="text", text="Error: No store IDs provided")]
        try:
            insights = await collection_agent.collect_store_data(store_ids, days_back)
            filepath = await collection_agent.save_insights(insights)
            summary = {
                "stores_processed": len(insights),
                "output_file": filepath,
                "insights": [
                    {
                        "store_id": insight.store_id,
                        "rating": insight.rating,
                        "review_count": insight.review_count,
                        "positive_themes": insight.themes_positive[:3],
                        "negative_themes": insight.themes_negative[:3]
                    }
                    for insight in insights
                ]
            }
            return [types.TextContent(
                type="text",
                text=f"Successfully collected insights for {len(insights)} stores.\n\n"
                     f"Output saved to: {filepath}\n\n"
                     f"Summary:\n{json.dumps(summary, indent=2)}"
            )]
        except Exception as e:
            logger.error(f"Error in collect_store_insights: {e}")
            return [types.TextContent(type="text", text=f"Error collecting store insights: {str(e)}")]
    elif name == "get_store_status":
        # Return status for a single store (mocked, update for your real data)
        store_id = arguments.get("store_id")
        if not store_id:
            return [types.TextContent(type="text", text="Error: No store ID provided")]
        try:
            # TODO: Replace with real status lookup (e.g., from Cosmos DB or latest file)
            status = {
                "store_id": store_id,
                "last_collection": "2025-06-03",
                "status": "active",
                "recent_rating": 4.2,
                "data_freshness": "24 hours"
            }
            return [types.TextContent(type="text", text=f"Store Status for {store_id}:\n{json.dumps(status, indent=2)}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error getting store status: {str(e)}")]
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """
    Lists available resources (data endpoints) for MCP clients.
    You can add more resources here (e.g., for raw data, logs, etc).
    """
    return [
        types.Resource(
            uri="file://data/processed/store_insights_latest.json",
            name="Latest Store Insights",
            description="Most recent store insights data",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """
    Reads resource content by URI.
    Used by MCP clients to fetch data files.
    Add more URI patterns as you add more resources.
    """
    if uri == "file://data/processed/store_insights_latest.json":
        # Find the most recent insights file
        pattern = "store_insights_*.json"
        files = list(Path("data/processed").glob(pattern))
        if not files:
            return json.dumps({"error": "No insight files found"})
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        return latest_file.read_text()
    raise ValueError(f"Unknown resource: {uri}")


async def main():
    """
    Main entry point for the collection agent MCP server.
    This starts the server and exposes all tools/resources over stdin/stdout (for orchestration).
    You can run this as a standalone process, or as part of a larger MCP workflow.
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="collection-agent",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
