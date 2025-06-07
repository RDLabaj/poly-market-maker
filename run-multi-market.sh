#!/usr/bin/env bash

echo "🚀 Starting Universal Multi-Market Manager..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with required variables"
    exit 1
fi

# Source environment variables
source .env

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "❌ Error: Virtual environment not found"
    echo "Please run ./install.sh first"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install additional dependencies for multi-market manager
echo "📦 Installing additional dependencies..."
pip install requests python-dotenv PyYAML

# Check required environment variables
if [ -z "$PRIVATE_KEY" ]; then
    echo "❌ Error: PRIVATE_KEY not set in .env"
    exit 1
fi

if [ -z "$RPC_URL" ]; then
    echo "❌ Error: RPC_URL not set in .env"
    exit 1
fi

# Create config file if it doesn't exist
if [ ! -f market_config.yaml ]; then
    echo "📝 Creating default market configuration..."
    echo "You can edit market_config.yaml to enable/disable different market types"
fi

echo "✅ Environment OK"

# Show current configuration
echo ""
echo "🔧 Current Configuration:"
echo "  Strategy: ${STRATEGY:-amm}"
echo "  Config: ${CONFIG:-./config/amm.json}"
echo "  Max Markets: ${MAX_MARKETS:-10}"
echo "  Refresh Interval: ${REFRESH_INTERVAL:-300}s"
echo ""

echo "📋 Available Market Types (edit market_config.yaml to enable):"
echo "  🏀 NBA       - Basketball markets"
echo "  🏈 NFL       - American football markets"  
echo "  ⚽ Soccer    - International football markets"
echo "  🗳️  Elections - Political prediction markets"
echo "  💰 Crypto    - Cryptocurrency price markets"
echo "  🎬 Entertainment - Pop culture & awards"
echo "  🏎️  Formula1  - Racing markets"
echo "  🏒 Hockey    - NHL markets"
echo "  📈 Finance   - Stock & economic markets"
echo "  🌡️  Climate   - Weather & climate markets"
echo ""

echo "🚀 Starting Multi-Market Manager..."

# Run the multi-market manager
python3 multi_market_manager.py 