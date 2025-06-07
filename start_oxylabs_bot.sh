#!/bin/bash

echo "🚀 Starting Polymarket Bot with Residential Proxy"
echo "=================================================="

# Check for SmartProxy credentials first (FREE trial)
if [ -n "$SMARTPROXY_USERNAME" ] && [ -n "$SMARTPROXY_PASSWORD" ]; then
    echo "✅ SmartProxy credentials found (3-day FREE trial)"
    proxy_type="SmartProxy"
elif [ -n "$OXYLABS_USERNAME" ] && [ -n "$OXYLABS_PASSWORD" ]; then
    echo "✅ Oxylabs credentials found"
    proxy_type="Oxylabs"
else
    echo "❌ No proxy credentials found!"
    echo ""
    echo "OPTION 1 - SmartProxy (3-day FREE trial, recommended):"
    echo "export SMARTPROXY_USERNAME='user-12345678-country-PL'"
    echo "export SMARTPROXY_PASSWORD='your_password'"
    echo ""
    echo "OPTION 2 - Oxylabs (7-day trial, requires signup):"
    echo "export OXYLABS_USERNAME='customer-YOUR_ID'"
    echo "export OXYLABS_PASSWORD='your_password'"
    echo ""
    echo "Choose which proxy to configure:"
    echo "1) SmartProxy (FREE 3-day trial)"
    echo "2) Oxylabs (7-day trial)"
    read -p "Enter choice (1 or 2): " choice
    
    if [ "$choice" = "1" ]; then
        echo "Setting up SmartProxy..."
        read -p "Enter SmartProxy username: " username
        read -s -p "Enter SmartProxy password: " password
        echo ""
        export SMARTPROXY_USERNAME="$username"
        export SMARTPROXY_PASSWORD="$password"
        proxy_type="SmartProxy"
    else
        echo "Setting up Oxylabs..."
        read -p "Enter Oxylabs username: " username
        read -s -p "Enter Oxylabs password: " password
        echo ""
        export OXYLABS_USERNAME="$username"
        export OXYLABS_PASSWORD="$password"
        proxy_type="Oxylabs"
    fi
fi

echo "✅ $proxy_type credentials configured"

# Test proxy first
echo "🧪 Testing proxy connection..."
if [ "$proxy_type" = "SmartProxy" ]; then
    python3 -c "
from smartproxy_integration import setup_smartproxy
import os
username = os.getenv('SMARTPROXY_USERNAME')
password = os.getenv('SMARTPROXY_PASSWORD')
result = setup_smartproxy(username, password)
exit(0 if result else 1)
"
else
    python3 test_oxylabs.py
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Proxy test successful! Starting trading bot..."
    echo ""
    
    # Run the bot
    python3 poly_market_maker/app.py \
        --strategy=bands \
        --strategy-config=config/bands.json \
        --condition-id=0x178dee952f29fb0a77f63df1d59514d15009caeb7c011a5c086aad80e6369f8d \
        --sync-interval=15 \
        --refresh-frequency=5
else
    echo ""
    echo "❌ Proxy test failed! Check your credentials and try again."
    echo ""
    echo "Troubleshooting:"
    echo "1. Verify Oxylabs credentials in dashboard"
    echo "2. Check if trial credits are available"
    echo "3. Try different endpoint (edit oxylabs_endpoints.py)"
    exit 1
fi 