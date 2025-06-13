#!/bin/bash

# GitHub Repository Setup Script
# This script initializes git, sets up the remote repository, and pushes the cleaned codebase

echo "🚀 Setting up GitHub repository for Store Management MCP Servers..."

# Configure git user (you can modify these if needed)
git config user.name "ashburn-young"
git config user.email "ashburnyoung@outlook.com"

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
fi

# Add all files to staging
echo "📦 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Store Management MCP Servers

- Clean codebase with sensitive information removed
- MCP servers for Google Business Analytics
- Azure Container Apps deployment ready
- Streamlit dashboard for visualization
- Complete documentation and setup guides"

# Add remote repository
echo "🌐 Adding remote repository..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/ashburn-young/store_management_mcp.git

# Set default branch to main
git branch -M main

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo "✅ Repository successfully set up!"
echo "📍 Your repository is now available at: https://github.com/ashburn-young/store_management_mcp"
echo ""
echo "🎯 Next steps:"
echo "1. Visit your repository on GitHub"
echo "2. Configure any additional repository settings"
echo "3. Set up environment variables for deployment"
echo "4. Follow the README for local development setup"
