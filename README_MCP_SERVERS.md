# Google Business Analytics MCP Servers

This document provides comprehensive information on working with the Google Business Analytics Model Context Protocol (MCP) servers for collecting, processing, and analyzing Google Business Profile data for Williams Sonoma retail locations.

## Table of Contents

1. [Overview](#overview)
2. [Google Business Profile API Setup](#google-business-profile-api-setup)
3. [MCP Server Architecture](#mcp-server-architecture)
4. [Code Documentation](#code-documentation)
5. [Azure Deployment](#azure-deployment)
6. [Development and Testing](#development-and-testing)
7. [Configuration](#configuration)
8. [Usage Examples](#usage-examples)

## Overview

This project implements two specialized MCP servers that work together to provide real-time business intelligence from Google Business Profile data:

- **Collection Agent**: Gathers raw data from Google Business APIs, processes reviews, and extracts store-level insights
- **Aggregation Agent**: Combines store insights into executive summaries, generates alerts, and produces actionable analytics

The system uses Azure OpenAI for enhanced sentiment analysis, theme extraction, and intelligent alert generation, with fallback mechanisms for offline operation.

## Google Business Profile API Setup

### Prerequisites

Before using these MCP servers, you need to set up access to the Google Business Profile API for your business. This requires:

1. **Google Cloud Project**: Create a new project in the [Google Cloud Console](https://console.cloud.google.com/)
2. **Business Profile API Access**: Enable the Google My Business API
3. **Authentication**: Set up service account credentials

### Step-by-Step Setup

#### 1. Create Google Cloud Project

```bash
# Using Google Cloud CLI
gcloud projects create your-business-analytics-project
gcloud config set project your-business-analytics-project
```

#### 2. Enable Required APIs

Enable the Google My Business API and related services:

```bash
gcloud services enable mybusiness.googleapis.com
gcloud services enable places.googleapis.com
gcloud services enable geocoding-backend.googleapis.com
```

#### 3. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create business-analytics-sa \
    --description="Service account for business analytics MCP servers" \
    --display-name="Business Analytics Service Account"

# Generate key file
gcloud iam service-accounts keys create credentials.json \
    --iam-account=business-analytics-sa@your-project-id.iam.gserviceaccount.com
```

#### 4. Set Up Business Profile Access

1. Visit the [Google My Business website](https://business.google.com/)
2. Verify ownership of your business locations
3. Grant API access to your service account:
   - Go to Settings → Users and permissions
   - Add the service account email with "Manager" permissions

#### 5. Environment Configuration

Create a `.env` file with your credentials:

```env
# Google API Configuration
GOOGLE_API_KEY=your-google-api-key
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/credentials.json
GOOGLE_PROJECT_ID=your-project-id

# Azure OpenAI Configuration (optional but recommended)
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### API Quotas and Limits

- **Google My Business API**: 1,000 requests per day (free tier)
- **Rate Limiting**: 100 requests per minute (configurable)
- **Review Data**: Up to 100 reviews per location per request
- **Historical Data**: Up to 18 months of review history

## MCP Server Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────────┐    ┌─────────────────────┐
│   Collection Agent  │    │  Aggregation Agent  │
│                     │    │                     │
│ ┌─────────────────┐ │    │ ┌─────────────────┐ │
│ │ Google API      │ │    │ │ Data Aggregator │ │
│ │ Client          │ │    │ │                 │ │
│ └─────────────────┘ │    │ └─────────────────┘ │
│ ┌─────────────────┐ │    │ ┌─────────────────┐ │
│ │ Data Processor  │ │    │ │ Alert Generator │ │
│ │                 │ │    │ │                 │ │
│ └─────────────────┘ │    │ └─────────────────┘ │
└─────────────────────┘    └─────────────────────┘
           │                           │
           └───────┬───────────────────┘
                   │
      ┌─────────────────────┐
      │   Shared Services   │
      │                     │
      │ ┌─────────────────┐ │
      │ │ Azure OpenAI    │ │
      │ │ Service         │ │
      │ └─────────────────┘ │
      │ ┌─────────────────┐ │
      │ │ Configuration   │ │
      │ │ Manager         │ │
      │ └─────────────────┘ │
      │ ┌─────────────────┐ │
      │ │ Pydantic        │ │
      │ │ Schemas         │ │
      │ └─────────────────┘ │
      └─────────────────────┘
```

### Data Flow

1. **Collection Phase**: Collection Agent retrieves data from Google Business API
2. **Processing Phase**: Raw data is processed into structured insights
3. **Storage Phase**: Store insights are saved to JSON files
4. **Aggregation Phase**: Aggregation Agent combines insights into executive summaries
5. **Alert Generation**: System identifies critical issues and opportunities
6. **Dashboard Integration**: Processed data feeds into Streamlit dashboard

## Why Model Context Protocol (MCP)?

MCP is a protocol for tool-based, composable, and language-agnostic AI/analytics workflows. It allows these agents to be orchestrated by other MCP clients, LLMs, or pipelines (e.g., for chaining, automation, or dashboard integration). Each server exposes tools (functions) and resources (data endpoints) in a discoverable, schema-driven way, making integration and automation easy.

## MCP Server Code Structure & Extensibility

- **Collection Agent Server** (`src/google_business_analytics/collection_agent/server.py`)
  - Connects to Google Business Profile API (via `GoogleAPIClient`)
  - Runs sentiment analysis and theme extraction (via `DataProcessor`)
  - Exposes MCP tools for data collection and status
  - Saves processed insights to disk (or optionally to Azure Cosmos DB)
  - **To adapt:**
    - Update `GoogleAPIClient` to use your real Google API credentials and endpoints
    - Set up Azure credentials (Cosmos DB, Key Vault, etc.) as needed
    - Add/modify tools in `@server.list_tools` and `@server.call_tool` for your use case
    - Use environment variables for all secrets (see `.env`)

- **Aggregation Agent Server** (`src/google_business_analytics/aggregation_agent/server.py`)
  - Loads processed store insights (from collection agent or Cosmos DB)
  - Aggregates, cleans, and summarizes data for executive/board-level reporting
  - Exposes MCP tools for snapshot generation, trend analysis, and resource access
  - Saves executive snapshots to disk (or optionally to Azure)
  - **To adapt:**
    - Update `DataAggregator` to match your business logic and KPIs
    - Add/modify tools in `@server.list_tools` and `@server.call_tool` for new analytics
    - Use environment variables for all secrets (see `.env`)
    - For Azure integration, add Cosmos DB/Blob/Key Vault as needed

> **See the in-code comments in both server files for detailed guidance on each block and how to extend or adapt for your business and cloud environment.**

## Code Documentation

### Collection Agent (`collection_agent/`)

The Collection Agent is responsible for gathering and processing raw Google Business data.

#### `server.py` - MCP Server Implementation

**Purpose**: Implements the MCP protocol server for data collection operations.

**Key Components**:
- `CollectionAgent` class: Main orchestrator for data collection
- MCP tool handlers for external integration
- Error handling and logging

**MCP Tools Exposed**:
1. `collect_store_insights`: Collects data for multiple stores
2. `get_store_status`: Retrieves current status for a specific store

**Usage Flow**:
```python
# Initialize collection agent
collection_agent = CollectionAgent()

# Collect data for stores
insights = await collection_agent.collect_store_data(['store_001', 'store_002'], days_back=90)

# Save processed insights
filepath = await collection_agent.save_insights(insights)
```

#### `google_api_client.py` - Google API Integration

**Purpose**: Handles all interactions with Google Business Profile APIs.

**Key Features**:
- Service account authentication
- Rate limiting and quota management
- Mock data support for development
- Error handling and retry logic

**API Methods**:
- `get_store_data()`: Retrieves store information and reviews
- `get_store_reviews()`: Fetches recent reviews for a location
- `get_store_info()`: Gets basic store metadata

#### `data_processor.py` - Data Processing Engine

**Purpose**: Converts raw Google API data into structured business insights.

**Processing Pipeline**:
1. **Review Analysis**: Processes individual customer reviews
2. **Sentiment Analysis**: Uses Azure OpenAI or TextBlob for sentiment scoring
3. **Theme Extraction**: Identifies positive and negative themes
4. **Insight Generation**: Creates structured `StoreInsight` objects

**Key Methods**:
- `process_store_data()`: Main processing entry point
- `_extract_themes()`: Extracts common themes from reviews
- `_calculate_sentiment_distribution()`: Computes sentiment percentages
- `_generate_excerpt()`: Creates representative review excerpts

**Azure OpenAI Integration**:
```python
if self.use_azure_openai:
    # Use advanced AI for theme extraction
    advanced_themes = await self.azure_openai.extract_themes_intelligent(reviews)
else:
    # Fall back to keyword-based analysis
    themes = self._extract_themes_fallback(reviews)
```

### Aggregation Agent (`aggregation_agent/`)

The Aggregation Agent transforms store-level insights into executive-ready analytics.

#### `server.py` - MCP Server Implementation

**Purpose**: Implements the MCP protocol server for data aggregation operations.

**Key Components**:
- `AggregationAgent` class: Main orchestrator for aggregation
- Executive snapshot generation
- Historical data management

**MCP Tools Exposed**:
1. `generate_executive_snapshot`: Creates comprehensive executive summary
2. `get_national_kpis`: Retrieves high-level performance metrics
3. `get_alerts`: Returns active alerts and recommendations

#### `aggregator.py` - Data Aggregation Engine

**Purpose**: Combines store insights into actionable executive intelligence.

**Aggregation Functions**:

1. **National KPIs Calculation**:
   ```python
   def _calculate_national_kpis(self, insights: List[StoreInsight]) -> NationalKPIs:
       """Calculate national-level performance indicators."""
       avg_rating = statistics.mean([insight.rating for insight in insights])
       total_reviews = sum(insight.review_count for insight in insights)
       nps_equivalent = self._calculate_nps_equivalent(insights)
   ```

2. **Regional Summaries**:
   - Groups stores by geographic region
   - Calculates regional performance metrics
   - Identifies regional trends and outliers

3. **Alert Generation**:
   - **Severity Levels**: Critical, High, Medium, Low
   - **Alert Types**: Rating drops, review volume changes, sentiment shifts
   - **Smart Alerts**: Uses Azure OpenAI for intelligent alert generation

4. **Trending Issues**:
   - Identifies emerging themes across stores
   - Tracks sentiment trends over time
   - Provides actionable recommendations

### Shared Services (`shared/`)

Common services and utilities used by both agents.

#### `schemas.py` - Data Models

**Purpose**: Defines Pydantic models for type safety and validation.

**Key Models**:
1. `StoreInsight`: Individual store analytics
2. `ExecutiveSnapshot`: Company-wide summary
3. `Alert`: Issue notifications and recommendations
4. `NationalKPIs`: High-level performance metrics

**Validation Features**:
- Type checking for all data fields
- Range validation (e.g., ratings 1.0-5.0)
- Custom validators for business logic

#### `azure_openai_service.py` - AI Integration

**Purpose**: Provides enhanced analytics using Azure OpenAI.

**AI-Powered Features**:
1. **Advanced Sentiment Analysis**: Multi-dimensional sentiment scoring
2. **Intelligent Theme Extraction**: Context-aware theme identification
3. **Smart Alert Generation**: AI-generated insights and recommendations
4. **Executive Summaries**: Natural language business intelligence

**Fallback Mechanisms**:
- Graceful degradation when Azure OpenAI is unavailable
- TextBlob-based sentiment analysis as backup
- Keyword-based theme extraction as fallback

#### `config.py` - Configuration Management

**Purpose**: Centralized configuration with environment variable support.

**Configuration Categories**:
- Azure OpenAI settings
- Google API credentials
- Processing parameters
- Alert thresholds

## Azure Deployment

For production deployment to Azure, this section provides a complete infrastructure-as-code solution using Azure Bicep templates.

### Architecture Overview

The Azure deployment includes:
- **Azure Container Apps**: For hosting the MCP servers
- **Azure OpenAI Service**: For enhanced analytics
- **Azure Storage Account**: For data persistence
- **Azure Key Vault**: For secure credential management
- **Application Insights**: For monitoring and logging

### Deployment Files

A complete Azure deployment example is provided in a separate file: [`azure_deployment_example.bicep`](azure_deployment_example.bicep)

### Quick Deployment Guide

1. **Prerequisites**:
   ```bash
   az login
   az account set --subscription "your-subscription-id"
   ```

2. **Deploy Infrastructure**:
   ```bash
   az deployment group create \
     --resource-group "rg-business-analytics" \
     --template-file azure_deployment_example.bicep \
     --parameters @parameters.json
   ```

3. **Configure Environment Variables**:
   ```bash
   az containerapp update \
     --name "ca-collection-agent" \
     --resource-group "rg-business-analytics" \
     --set-env-vars \
       AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com/" \
       GOOGLE_API_KEY="your-api-key"
   ```

### Monitoring and Scaling

- **Application Insights**: Monitors performance and errors
- **Auto-scaling**: Scales based on CPU and memory usage
- **Health Checks**: Ensures service availability
- **Log Analytics**: Centralized logging for troubleshooting

## Development and Testing

### Local Development Setup

1. **Clone and Install**:
   ```bash
   git clone <repository-url>
   cd google-business-analytics
   pip install -e .[dev]
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run Tests**:
   ```bash
   python -m pytest tests/ -v
   python -m pytest tests/ --cov=src --cov-report=html
   ```

### Running MCP Servers

#### Start Collection Agent:
```bash
python -m google_business_analytics.collection_agent.server
```

#### Start Aggregation Agent:
```bash
python -m google_business_analytics.aggregation_agent.server
```

#### Using VS Code Tasks:
- `Ctrl+Shift+P` → "Tasks: Run Task"
- Select "Start Collection Agent Server" or "Start Aggregation Agent Server"

### Testing with Mock Data

The system includes comprehensive mock data for development:

```python
# Use mock data for testing
google_client = GoogleAPIClient(use_mock_data=True)
store_data = await google_client.get_store_data("mock_store_001")
```

### Code Quality Tools

- **Black**: Code formatting
- **Ruff**: Fast Python linting
- **MyPy**: Type checking
- **Pytest**: Testing framework

Run all quality checks:
```bash
python -m black src/ tests/ dashboard/
python -m ruff check src/ tests/ dashboard/
python -m mypy src/
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Cloud API key |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Yes | Path to service account JSON |
| `AZURE_OPENAI_ENDPOINT` | No | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | No | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | No | Model deployment name |

### Configuration File (`config/config.yaml`)

The system supports extensive configuration via YAML:

```yaml
azure_openai:
  enabled: true
  max_tokens: 1500
  temperature: 0.1
  use_for_sentiment: true
  use_for_themes: true

google_api:
  requests_per_minute: 100
  batch_size: 50
  default_lookback_days: 30

processing:
  alert_rating_drop_threshold: 0.5
  min_theme_frequency: 3
  max_themes_per_store: 10
```

## Usage Examples

### Example 1: Collect Store Insights

```python
from google_business_analytics.collection_agent.server import CollectionAgent

# Initialize agent
agent = CollectionAgent()

# Collect data for specific stores
store_ids = ["store_001", "store_002", "store_003"]
insights = await agent.collect_store_data(store_ids, days_back=30)

# Save results
filepath = await agent.save_insights(insights)
print(f"Insights saved to: {filepath}")
```

### Example 2: Generate Executive Summary

```python
from google_business_analytics.aggregation_agent.server import AggregationAgent

# Initialize agent
agent = AggregationAgent()

# Generate executive snapshot
snapshot = await agent.generate_executive_snapshot()

# Access key metrics
print(f"National Average Rating: {snapshot.national_kpis.avg_rating}")
print(f"Active Alerts: {len(snapshot.alerts)}")
print(f"Trending Issues: {snapshot.trending_issues}")
```

### Example 3: Dashboard Integration

```python
import streamlit as st
from pathlib import Path
import json

# Load latest executive snapshot
snapshot_file = Path("data/snapshots/exec_snapshot_latest.json")
if snapshot_file.exists():
    with open(snapshot_file) as f:
        snapshot_data = json.load(f)
    
    st.metric("Average Rating", snapshot_data["national_kpis"]["avg_rating"])
    st.metric("Total Stores", snapshot_data["national_kpis"]["total_stores"])
```

### Example 4: Custom Alert Generation

```python
from google_business_analytics.aggregation_agent.aggregator import DataAggregator

# Initialize aggregator
aggregator = DataAggregator()

# Set custom alert thresholds
aggregator.alert_thresholds.update({
    "rating_drop_critical": 0.3,  # More sensitive
    "low_rating_threshold": 3.5   # Higher standard
})

# Generate alerts with custom thresholds
alerts = aggregator._generate_alerts(store_insights)
```

---

## Support and Troubleshooting

### Common Issues

1. **Google API Authentication Errors**:
   - Verify service account permissions
   - Check API quotas and billing
   - Ensure correct project ID

2. **Azure OpenAI Connection Issues**:
   - Validate endpoint URL and API key
   - Check deployment name and API version
   - Review Azure OpenAI service status

3. **MCP Server Connection Issues**:
   - Verify server is running on correct port
   - Check network connectivity
   - Review server logs for errors

### Logging and Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

- Use appropriate batch sizes for API calls
- Implement caching for frequently accessed data
- Monitor API quotas and rate limits
- Use async operations for better throughput

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run quality checks
5. Submit a pull request

For detailed deployment to Azure, see the accompanying [Azure Deployment Example](azure_deployment_example.bicep) file.
