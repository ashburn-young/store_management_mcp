<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions for Google Business Analytics MCP Servers

## Project Overview
This is an MCP (Model Context Protocol) server project that implements two specialized servers for Google Business data collection and executive analytics.

## Key Guidelines

### MCP Server Development
- You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt
- Reference the official Python SDK: https://github.com/modelcontextprotocol/create-python-server
- Follow MCP protocol specifications for tool definitions and resource handling
- Implement proper error handling and logging for MCP operations

### Code Style & Structure
- Use type hints throughout the codebase (Python 3.8+ compatible)
- Follow the existing modular architecture with clear separation between collection and aggregation
- Implement proper async/await patterns for MCP server operations
- Use Pydantic models for all data validation and JSON schema generation

### Data Handling
- Always validate input/output data against the defined JSON schemas
- Implement proper error handling for API failures and data processing issues
- Use the established data flow: Raw Data → Store Insights → Executive Snapshots
- Maintain data freshness tracking and implement proper caching mechanisms

### Testing & Development
- Write tests for all MCP tools and resources
- Use mock data generators for testing without external API dependencies
- Implement proper logging with structured output
- Follow the configuration-driven approach for parameters

### Business Logic
- Focus on actionable insights for executive decision-making
- Implement robust sentiment analysis and theme extraction
- Design alert mechanisms that surface critical issues early
- Ensure all outputs are dashboard-ready with proper formatting

### Integration Guidelines
- Design for integration with multiple dashboard tools (Streamlit, Power BI, Tableau)
- Implement proper rate limiting for Google API calls
- Use environment variables for all sensitive configuration
- Follow the JSON schema contracts strictly to ensure compatibility
