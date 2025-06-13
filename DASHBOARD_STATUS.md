# Williams Sonoma Store Analytics Dashboard - Quick Start Guide

## Current Status

✅ **Completed Tasks:**
- ✅ Expanded Williams Sonoma store dataset (10 → 25 stores)
- ✅ Fixed dashboard UI with dark mode and improved map visualization
- ✅ Implemented collapsible state cards in Executive Overview
- ✅ Added interactive US map with state boundaries and store markers
- ✅ Fixed Azure OpenAI integration for "Ask About This Store" feature
- ✅ Created comprehensive documentation (README_MCP_SERVERS.md)
- ✅ Created Azure Bicep deployment template
- ✅ All code properly formatted and tested

## Dashboard Features

### 🎯 Executive Overview
- Store performance metrics and KPIs
- **Collapsible state cards** showing stores by state
- Real-time store count and geographic distribution

### 🗺️ Interactive Map
- **Dark mode US map** with state boundaries
- Store locations plotted with custom markers
- Hover information showing store details
- Color-coded by performance metrics

### 📊 Store Analysis
- Individual store performance metrics
- Review sentiment analysis
- Q&A insights and trends
- Performance comparisons

### 🤖 AI-Powered Analytics
- **"Ask About This Store"** feature using Azure OpenAI (GPT-4o)
- Natural language queries about store performance
- Intelligent insights and recommendations

## Quick Start Instructions

### Option 1: Using VS Code Task (Recommended)
1. Open VS Code in the project directory
2. Run task: `Start Streamlit Dashboard` (Ctrl+Shift+P → "Tasks: Run Task")
3. Dashboard will start on http://localhost:8501

### Option 2: Using Batch File
1. Double-click `start_streamlit.bat`
2. Dashboard will start automatically

### Option 3: Using Python Script
1. Run: `python start_dashboard_safe.py`
2. Follow the on-screen instructions

### Option 4: Manual Command
```powershell
cd "c:\Users\kimyo\.docker\wsmcpservers"
streamlit run dashboard/app.py --server.port 8501
```

## Troubleshooting

### Check System Status
Run the diagnostic script:
```powershell
python check_dashboard.py
```

This will check:
- ✅ Dependencies (Streamlit, Plotly, etc.)
- ✅ Environment variables (Azure OpenAI config)
- ✅ Data files (stores, reviews, Q&A)
- ✅ Port availability (8501)
- ✅ Store data integrity

### Common Issues

#### 1. Port 8501 Already in Use
```powershell
# Find and kill the process
netstat -ano | findstr :8501
taskkill /PID <PID_NUMBER> /F
```

#### 2. Missing Dependencies
```powershell
pip install -e .[dev]
```

#### 3. Missing Environment Variables
Create a `.env` file in the project root:
```env
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

#### 4. Import Errors
Ensure you're in the correct directory:
```powershell
cd "c:\Users\kimyo\.docker\wsmcpservers"
```

## Project Structure

```
wsmcpservers/
├── dashboard/
│   └── app.py                    # Main Streamlit dashboard
├── data/
│   ├── williams_sonoma_stores.json     # 25 store locations
│   ├── williams_sonoma_reviews.json    # Customer reviews
│   └── williams_sonoma_qna.json       # Q&A data
├── src/google_business_analytics/
│   ├── collection_agent/         # Data collection MCP server
│   ├── aggregation_agent/        # Analytics MCP server
│   └── shared/                   # Shared services (Azure OpenAI, config)
├── config/
│   └── config.yaml              # Configuration settings
└── scripts/                     # Utility scripts
```

## Current Store Coverage

The dashboard now includes **25 Williams Sonoma stores** across **13 states**:

- **California**: 8 stores (San Francisco, Los Angeles, Beverly Hills, etc.)
- **New York**: 3 stores (Manhattan, Brooklyn, etc.)
- **Texas**: 3 stores (Dallas, Houston, Austin)
- **Florida**: 2 stores (Miami, Orlando)
- **Illinois**: 2 stores (Chicago)
- **Massachusetts**: 2 stores (Boston)
- **Washington**: 2 stores (Seattle)
- **Colorado**: 1 store (Denver)
- **Georgia**: 1 store (Atlanta)
- **Nevada**: 1 store (Las Vegas)

## Next Steps

1. **Start the dashboard** using one of the methods above
2. **Access at**: http://localhost:8501
3. **Explore features**:
   - Check the Executive Overview with collapsible state cards
   - View the interactive US map
   - Try the AI-powered analytics feature
4. **Monitor logs** for any issues

## Support

- **Documentation**: See `README_MCP_SERVERS.md` for complete setup guide
- **Azure Deployment**: Use `azure_deployment_example.bicep` for cloud deployment
- **Issues**: Check logs in the `logs/` directory
- **Development**: Run tests with `pytest tests/` or use VS Code tasks

---

**Dashboard URL**: http://localhost:8501
**Status**: Ready to run ✅
**Last Updated**: ${new Date().toISOString()}
