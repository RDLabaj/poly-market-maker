#!/bin/bash

echo "Setting up FlareSolverr for Polymarket Cloudflare bypass..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Pull FlareSolverr image
echo "Pulling FlareSolverr Docker image..."
docker pull flaresolverr/flaresolverr:latest

# Stop and remove existing container if it exists
echo "Stopping existing FlareSolverr container (if any)..."
docker stop flaresolverr 2>/dev/null || true
docker rm flaresolverr 2>/dev/null || true

# Run FlareSolverr container
echo "Starting FlareSolverr container..."
docker run -d \
  --name=flaresolverr \
  -p 8191:8191 \
  -e LOG_LEVEL=info \
  -e LOG_HTML=false \
  -e CAPTCHA_SOLVER=none \
  --restart unless-stopped \
  flaresolverr/flaresolverr:latest

# Wait for container to start
echo "Waiting for FlareSolverr to start..."
sleep 10

# Test if FlareSolverr is running
if curl -s http://localhost:8191 > /dev/null; then
    echo "✅ FlareSolverr is running successfully on http://localhost:8191"
    echo ""
    echo "Now you can run the bot with FlareSolverr integration:"
    echo "python -m poly_market_maker --use-flaresolverr --private-key YOUR_KEY --rpc-url YOUR_RPC --clob-api-url https://clob.polymarket.com"
else
    echo "❌ FlareSolverr failed to start properly"
    docker logs flaresolverr
    exit 1
fi

echo ""
echo "To stop FlareSolverr later, run:"
echo "docker stop flaresolverr"
echo ""
echo "To check logs:"
echo "docker logs flaresolverr" 