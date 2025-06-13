#!/bin/bash
# Unix/Linux shell script to start Google Business Analytics MCP servers

echo "Starting Google Business Analytics MCP Servers..."
echo

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT/src"
export USE_MOCK_DATA=true
export DEBUG_MODE=false

# Change to project directory
cd "$PROJECT_ROOT"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
if ! python3 -c "import mcp, pydantic, streamlit" &> /dev/null; then
    echo "Error: Required packages not installed. Run: pip install -e .[dev]"
    exit 1
fi

# Make the script executable
chmod +x "$0"

# Start the services using the Python script
python3 scripts/start.py
