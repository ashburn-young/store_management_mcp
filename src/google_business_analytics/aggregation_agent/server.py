"""Aggregation Agent MCP Server

This file implements the MCP (Model Context Protocol) server for data aggregation and executive analytics.

Why MCP Server?
- MCP enables composable, orchestratable analytics pipelines (tool/resource-based, LLM-friendly).
- This agent can be called by other MCP clients, LLMs, or dashboards to generate executive summaries, KPIs, and alerts.
- All tools and resources are discoverable and schema-driven for easy integration.

What does this file do?
- Loads processed store insights (from collection agent or Cosmos DB)
- Aggregates, cleans, and summarizes data for executive/board-level reporting
- Exposes MCP tools for snapshot generation, trend analysis, and resource access
- Saves executive snapshots to disk (or optionally to Azure)

How to adapt for your project:
- Update DataAggregator to match your business logic and KPIs
- Add/modify tools in @server.list_tools and @server.call_tool for new analytics
- Use environment variables for all secrets (see .env)
- For Azure integration, add Cosmos DB/Blob/Key Vault as needed
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

from ..shared.schemas import ExecutiveSnapshot, StoreInsight
from .aggregator import DataAggregator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("aggregation-agent")


# Main agent class for executive insights aggregation
class AggregationAgent:
    """
    Handles all logic for aggregating, summarizing, and saving executive-level analytics.
    Extend this class to add new KPIs, alerting, or output targets.
    """
    def __init__(self):
        # DataAggregator: Handles all business logic for aggregation, KPIs, and alerts.
        # TODO: Update DataAggregator to match your business rules and metrics.
        self.aggregator = DataAggregator()
        # Input directory for processed store insights (from collection agent or Cosmos DB)
        self.input_dir = Path("data/processed")
        # Output directory for executive snapshots
        self.output_dir = Path("data/snapshots")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_executive_snapshot(self, date_filter: Optional[str] = None) -> ExecutiveSnapshot:
        """
        Loads insights, aggregates them, and returns a snapshot object.
        You can add more aggregation logic in DataAggregator.
        """
        insights = await self._load_store_insights(date_filter)
        if not insights:
            raise ValueError("No store insights found to aggregate")
        logger.info(f"Generating executive snapshot from {len(insights)} store insights")
        snapshot = await self.aggregator.create_executive_snapshot(insights)
        return snapshot

    async def save_snapshot(self, snapshot: ExecutiveSnapshot) -> str:
        """
        Saves executive snapshot to a JSON file (local disk).
        In production, you may want to save to Azure Cosmos DB or Blob Storage instead.
        To use Cosmos DB, add a Cosmos client and call it here.
        """
        filename = f"exec_snapshot_{snapshot.snapshot_date.strftime('%Y-%m-%d')}.json"
        filepath = self.output_dir / filename
        # Also save as latest
        latest_filepath = self.output_dir / "exec_snapshot_latest.json"
        # Convert to JSON-serializable format
        data = snapshot.model_dump()
        for file_path in [filepath, latest_filepath]:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved executive snapshot to {filepath}")
        return str(filepath)

    async def _load_store_insights(self, date_filter: Optional[str] = None) -> List[StoreInsight]:
        """
        Loads store insights from JSON files (or Cosmos DB).
        You can update this to load from Azure Cosmos DB or another data source.
        Returns a list of StoreInsight objects (Pydantic models).
        """
        insights = []
        if date_filter:
            pattern = f"store_insights_{date_filter}.json"
        else:
            pattern = "store_insights_*.json"
        files = list(self.input_dir.glob(pattern))
        if not files:
            logger.warning(f"No insight files found matching pattern: {pattern}")
            return []
        # If no date filter, use the most recent file
        if not date_filter:
            files = [max(files, key=lambda f: f.stat().st_mtime)]
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                for item in data:
                    insight = StoreInsight.model_validate(item)
                    insights.append(insight)
                logger.info(f"Loaded {len(data)} insights from {file_path}")
            except Exception as e:
                logger.error(f"Error loading insights from {file_path}: {e}")
                continue
        return insights


# Initialize the aggregation agent
aggregation_agent = AggregationAgent()


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    Lists available tools for the aggregation agent.
    Add new tools here for new analytics or reporting tasks.
    """
    return [
        types.Tool(
            name="generate_executive_snapshot",
            description="Generate executive-level snapshot from store insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_filter": {
                        "type": "string",
                        "description": "Optional date filter (YYYY-MM-DD) for insights to include"
                    }
                }
            }
        ),
        types.Tool(
            name="get_latest_snapshot",
            description="Get the most recent executive snapshot",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="analyze_trends",
            description="Analyze trends across multiple snapshots",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_back": {
                        "type": "integer",
                        "default": 7,
                        "description": "Number of days to look back for trend analysis"
                    }
                }
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
    
    if name == "generate_executive_snapshot":
        date_filter = arguments.get("date_filter")
        
        try:
            snapshot = await aggregation_agent.generate_executive_snapshot(date_filter)
            filepath = await aggregation_agent.save_snapshot(snapshot)
            
            # Create summary for display
            summary = {
                "snapshot_date": snapshot.snapshot_date.isoformat(),
                "national_kpis": {
                    "avg_rating": snapshot.national_kpis.avg_rating,
                    "total_stores": snapshot.national_kpis.total_stores,
                    "nps_equivalent": snapshot.national_kpis.nps_equivalent
                },
                "regions_analyzed": len(snapshot.regional_summary),
                "alerts_generated": len(snapshot.alerts),
                "trending_issues": snapshot.trending_issues[:3],  # Top 3
                "output_file": filepath
            }
            
            return [types.TextContent(
                type="text",
                text=f"Executive snapshot generated successfully!\n\n"
                     f"Summary:\n{json.dumps(summary, indent=2)}\n\n"
                     f"Full snapshot saved to: {filepath}"
            )]
            
        except Exception as e:
            logger.error(f"Error generating executive snapshot: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error generating executive snapshot: {str(e)}"
            )]
    
    elif name == "get_latest_snapshot":
        try:
            latest_file = Path("data/snapshots/exec_snapshot_latest.json")
            
            if not latest_file.exists():
                return [types.TextContent(
                    type="text",
                    text="No executive snapshots found. Generate one first using 'generate_executive_snapshot'."
                )]
            
            with open(latest_file, 'r') as f:
                snapshot_data = json.load(f)
            
            # Extract key metrics for display
            kpis = snapshot_data.get("national_kpis", {})
            alerts = snapshot_data.get("alerts", [])
            
            summary = {
                "snapshot_date": snapshot_data.get("snapshot_date"),
                "avg_rating": kpis.get("avg_rating"),
                "total_stores": kpis.get("total_stores"),
                "nps_score": kpis.get("nps_equivalent"),
                "active_alerts": len(alerts),
                "critical_alerts": len([a for a in alerts if a.get("severity") == "critical"])
            }
            
            return [types.TextContent(
                type="text",
                text=f"Latest Executive Snapshot:\n{json.dumps(summary, indent=2)}"
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error retrieving latest snapshot: {str(e)}"
            )]
    
    elif name == "analyze_trends":
        days_back = arguments.get("days_back", 7)
        
        try:
            # Mock trend analysis - in real implementation would analyze multiple snapshots
            trends = {
                "period": f"Last {days_back} days",
                "rating_trend": "+0.1 (improving)",
                "alert_trend": "-2 alerts (improving)",
                "emerging_issues": ["parking concerns", "checkout speed"],
                "resolved_issues": ["staff training"]
            }
            
            return [types.TextContent(
                type="text",
                text=f"Trend Analysis:\n{json.dumps(trends, indent=2)}"
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error analyzing trends: {str(e)}"
            )]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """
    Lists available resources (data endpoints) for MCP clients.
    Add more resources here as needed.
    """
    return [
        types.Resource(
            uri="file://data/snapshots/exec_snapshot_latest.json",
            name="Latest Executive Snapshot",
            description="Most recent executive snapshot data",
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
    if uri == "file://data/snapshots/exec_snapshot_latest.json":
        filepath = Path("data/snapshots/exec_snapshot_latest.json")
        
        if not filepath.exists():
            return json.dumps({"error": "No executive snapshots available"})
        
        return filepath.read_text()
    
    raise ValueError(f"Unknown resource: {uri}")


async def main():
    """
    Main entry point for the aggregation agent MCP server.
    This starts the server and exposes all tools/resources over stdin/stdout (for orchestration).
    You can run this as a standalone process, or as part of a larger MCP workflow.
    """
    # Run the server using stdin/stdout
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aggregation-agent",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
