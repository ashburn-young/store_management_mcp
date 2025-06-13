# Google Business Analytics Dashboard

This interactive dashboard provides a comprehensive view of Google Business data across all your locations, powered by Model Context Protocol (MCP) servers and AI-enhanced analytics.

## Features

### 📊 Executive Overview
- Real-time metrics for all stores
- Performance rankings and trends
- Alert management system
- Rating and review volume analysis
- Customizable date ranges

### 🏪 Store Details
- Detailed store information and performance metrics
- Theme extraction from reviews
- Rating trend analysis
- Latest customer feedback

### 🧠 AI-Powered Analytics
- Advanced store analysis using Azure OpenAI
- Strengths and improvement areas identification
- Customer sentiment analysis
- Smart recommendations based on data
- Interactive Q&A for business insights

### 🔌 Server Health Monitoring
- Real-time MCP server status
- Activity logging and performance metrics
- API usage tracking

### 💬 FAQ & Customer Questions
- Categorized display of frequently asked questions
- Questions organized by business topics
- Question trends and analytics
- Insight-driven recommendations based on common questions
- Interactive question explorer with expandable answers

## Technical Implementation

### Modern UI Components
- Responsive card-based design
- Interactive charts and visualizations
- Tabbed interface for organized data access
- Custom CSS for enhanced visual appeal

### Data Processing
- Real-time data processing with caching
- Trend analysis and performance tracking
- Theme extraction from customer reviews
- Rating distribution analysis

### AI Integration
- Azure OpenAI integration for advanced analytics
- Intelligent summarization of store performance
- Question answering for business insights
- Smart alerts with root cause analysis

### Dashboard Architecture
- Modular component design
- Async operations for improved performance
- Session state management
- Configurable refresh rates

## How to Use

1. **Start the Dashboard**:
   ```
   python -m scripts.run_dashboard
   ```
   Or use the VS Code task: "Start Streamlit Dashboard"

2. **Dashboard Controls**:
   - Use the date selector to filter data by time range
   - Enable auto-refresh for real-time updates
   - Monitor MCP server health in the sidebar

3. **Store Analysis**:
   - Select a store from the dropdown menu
   - Explore performance metrics and customer feedback
   - Use the AI-powered Q&A to ask specific questions
   - Review AI-generated recommendations

4. **Executive Insights**:
   - Track top performers and underperforming stores
   - Monitor rating trends across all locations
   - Address critical alerts for immediate attention

## Future Enhancements

- Additional visualization options
- Custom report generation
- Comparative analysis between time periods
- Extended AI capabilities with Azure OpenAI
- Mobile-optimized layout
