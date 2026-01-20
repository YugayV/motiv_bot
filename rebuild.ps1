# Rebuild and restart the Docker container
# Run this script after making changes to rebuild the bot

Write-Host "🛑 Stopping existing container..." -ForegroundColor Yellow
docker-compose down

Write-Host "🔨 Building new image..." -ForegroundColor Cyan
docker-compose build --no-cache

Write-Host "🚀 Starting container..." -ForegroundColor Green
docker-compose up -d

Write-Host "📋 Showing logs..." -ForegroundColor Magenta
docker-compose logs -f
