# Store Management MCP Servers

A comprehensive Google Business Analytics MCP (Model Context Protocol) server system for store management, customer analytics, and executive insights.

## Overview

This project implements specialized MCP servers for Google Business data collection and executive analytics, featuring:

- **Collection Agent**: Gathers data from Google Business Profile API
## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Collection     │    │   Aggregation    │    │   Dashboard     │
│  Agent (8000)   │────│   Agent (8001)   │────│   (8501)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Google Business │    │ Azure OpenAI     │    │ Streamlit UI    │
│ Profile API     │    │ / TextBlob       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Features

### 🎯 Core Capabilities
- **Real-time Data Collection**: Automated gathering of reviews, Q&A, and store information
- **AI-Powered Analytics**: Sentiment analysis, theme extraction, and trend identification
- **Executive Dashboards**: Business intelligence for decision-making
- **Scalable Architecture**: Container-based deployment with Azure Container Apps

### 📊 Analytics Features
- Customer sentiment tracking
- Review trend analysis
- Question categorization
- Performance metrics
- Alert mechanisms for critical issues

## Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop
- Azure CLI (for deployment)
- Google Cloud Platform account with Business Profile API access

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/ashburn-young/store_management_mcp.git
   cd store_management_mcp
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   pip install -e .[dev]
   ```

4. **Run the services**
   ```bash
   # Start Collection Agent
   python -m google_business_analytics.collection_agent.server

   # Start Aggregation Agent (in another terminal)
   python -m google_business_analytics.aggregation_agent.server

   # Start Dashboard (in another terminal)
   streamlit run dashboard/app.py --server.port 8501
   ```

### Using VS Code Tasks

The project includes pre-configured VS Code tasks for easy development:

- **Start Collection Agent Server**: Runs the collection MCP server
- **Start Aggregation Agent Server**: Runs the aggregation MCP server  
- **Start Streamlit Dashboard**: Launches the dashboard
- **Run Tests**: Execute the test suite
- **Format Code**: Apply Black formatting
- **Lint Code**: Run Ruff linting
- **Type Check**: Run MyPy type checking

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01

# Google API Configuration  
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service-account.json

# Development Settings
ENVIRONMENT=development
USE_MOCK_DATA=true
LOG_LEVEL=INFO
```

### Google Business Profile API Setup

1. Create a Google Cloud Platform project
2. Enable the Google Business Profile API
3. Create service account credentials
4. Download the service account JSON file
5. Set the `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable

### Azure OpenAI Setup

1. Create an Azure OpenAI resource
2. Deploy a GPT-4 model
3. Configure the endpoint and deployment name in `.env`
4. Authentication uses DefaultAzureCredential (Azure CLI login)

## Azure Deployment

### Automated Deployment with AZD

1. **Install Azure Developer CLI (azd)**
   ```bash
   # Windows (PowerShell)
   winget install microsoft.azd
   
   # macOS
   brew install azure-cli
   ```

2. **Initialize and deploy**
   ```bash
   azd init
   azd up
   ```

3. **Access deployed services**
   - Dashboard: `https://{env-name}-dashboard.{region}.azurecontainerapps.io`
   - Collection API: `https://{env-name}-collection.{region}.azurecontainerapps.io`
   - Aggregation API: `https://{env-name}-aggregation.{region}.azurecontainerapps.io`

### Manual Docker Deployment

1. **Build images**
   ```bash
   docker build -f Dockerfile.dashboard -t store-management-dashboard .
   docker build -f Dockerfile.collection -t store-management-collection .
   docker build -f Dockerfile.aggregation -t store-management-aggregation .
   ```

2. **Run containers**
   ```bash
   docker run -p 8501:8501 store-management-dashboard
   docker run -p 8000:8000 store-management-collection
   docker run -p 8001:8001 store-management-aggregation
   ```

## API Documentation

### Collection Agent (Port 8000)
- `GET /health` - Health check
- `POST /tools/collect_reviews` - Collect business reviews
- `POST /tools/collect_qna` - Collect Q&A data
- `POST /tools/collect_store_info` - Collect store information

### Aggregation Agent (Port 8001)  
- `GET /health` - Health check
- `POST /tools/generate_insights` - Process collected data
- `POST /tools/create_snapshot` - Create executive snapshot
- `GET /resources/processed_data` - Get processed insights

### Dashboard (Port 8501)
- Interactive Streamlit web interface
- Real-time data visualization
- Executive summary reports
- Performance analytics

## Testing

Run the test suite:
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html -v

# Run specific test files
python -m pytest tests/test_aggregator.py -v
```

## Development Guidelines

### Code Style
- Use type hints throughout (Python 3.8+ compatible)
- Follow PEP 8 with Black formatting
- Use Pydantic models for data validation
- Implement proper async/await patterns

### Architecture Principles
- Modular separation between collection and aggregation
- Configuration-driven approach for parameters
- Proper error handling and logging
- JSON schema contracts for compatibility

### Data Flow
```
Raw Data → Store Insights → Executive Snapshots
```

1. **Raw Data**: Direct API responses from Google Business Profile
2. **Store Insights**: Processed data with sentiment analysis and themes
3. **Executive Snapshots**: High-level summaries for business decisions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the development guidelines
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Project Structure

```
├── src/google_business_analytics/
│   ├── collection_agent/          # Data collection MCP server
│   ├── aggregation_agent/         # Data processing MCP server
│   └── shared/                    # Common utilities and schemas
├── dashboard/                     # Streamlit web interface
├── infra/                        # Azure deployment templates (Bicep)
├── config/                       # Configuration files and schemas
├── data/                         # Sample data and mock files
├── tests/                        # Test suite
├── scripts/                      # Utility scripts
└── logs/                         # Application logs
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions:
- 📧 Email: ashburnyoung@outlook.com
- 🐛 Issues: [GitHub Issues](https://github.com/ashburn-young/store_management_mcp/issues)
- 📖 Documentation: [Project Wiki](https://github.com/ashburn-young/store_management_mcp/wiki)

## Acknowledgments

- Built with the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Powered by Azure OpenAI and Google Business Profile API
- UI built with Streamlit
- Deployed on Azure Container Apps

MIT License - see LICENSE file for details.
