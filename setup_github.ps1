# GitHub Repository Setup Script for Windows PowerShell
# This script initializes git, sets up the remote repository, and pushes the cleaned codebase

Write-Host "🚀 Setting up GitHub repository for Store Management MCP Servers..." -ForegroundColor Green

# Configure git user
Write-Host "👤 Configuring git user..." -ForegroundColor Blue
git config user.name "ashburn-young"
git config user.email "ashburnyoung@outlook.com"

# Initialize git repository if not already initialized
if (-not (Test-Path ".git")) {
    Write-Host "📝 Initializing git repository..." -ForegroundColor Blue
    git init
}

# Add all files to staging
Write-Host "📦 Adding files to git..." -ForegroundColor Blue
git add .

# Create initial commit
Write-Host "💾 Creating initial commit..." -ForegroundColor Blue
git commit -m "Initial commit: Store Management MCP Servers

- Clean codebase with sensitive information removed
- MCP servers for Google Business Analytics  
- Azure Container Apps deployment ready
- Streamlit dashboard for visualization
- Complete documentation and setup guides"

# Add remote repository
Write-Host "🌐 Adding remote repository..." -ForegroundColor Blue
try {
    git remote remove origin 2>$null
} catch {
    # Remote doesn't exist, that's fine
}
git remote add origin https://github.com/ashburn-young/store_management_mcp.git

# Set default branch to main
Write-Host "🌟 Setting default branch to main..." -ForegroundColor Blue
git branch -M main

# Push to GitHub
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Blue
git push -u origin main

Write-Host "✅ Repository successfully set up!" -ForegroundColor Green
Write-Host "📍 Your repository is now available at: https://github.com/ashburn-young/store_management_mcp" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit your repository on GitHub" -ForegroundColor White
Write-Host "2. Configure any additional repository settings" -ForegroundColor White  
Write-Host "3. Set up environment variables for deployment" -ForegroundColor White
Write-Host "4. Follow the README for local development setup" -ForegroundColor White
