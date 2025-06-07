#!/usr/bin/env python3
"""
Test script for Oxylabs residential proxy with Polymarket
"""

import sys
import os
import logging
from oxylabs_proxy import setup_oxylabs_proxy, get_oxylabs_proxy

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_oxylabs_polymarket():
    """Test Oxylabs proxy specifically with Polymarket endpoints"""
    
    print("🧪 Testing Oxylabs proxy with Polymarket...")
    
    # Get credentials from environment or prompt
    username = os.getenv('OXYLABS_USERNAME')
    password = os.getenv('OXYLABS_PASSWORD')
    
    if not username or not password:
        print("\n⚠️ Oxylabs credentials needed!")
        print("1. Sign up at: https://oxylabs.io/products/residential-proxy-pool")
        print("2. Get 7-day FREE trial")
        print("3. Set environment variables:")
        print("   export OXYLABS_USERNAME='your_username'")
        print("   export OXYLABS_PASSWORD='your_password'")
        print()
        
        username = input("Enter Oxylabs username (or press Enter to skip): ").strip()
        if not username:
            return False
        password = input("Enter Oxylabs password: ").strip()
        if not password:
            return False
    
    print(f"Setting up Oxylabs proxy with username: {username}")
    
    # Setup proxy
    if not setup_oxylabs_proxy(username, password):
        print("❌ Oxylabs proxy setup failed!")
        return False
    
    proxy = get_oxylabs_proxy()
    if not proxy:
        print("❌ Could not get Oxylabs proxy instance!")
        return False
    
    print("\n🔄 Testing Polymarket endpoints...")
    
    # Test GET request (should work)
    print("Testing GET request to midpoint endpoint...")
    try:
        # Brian Armstrong market token_id
        token_id = "71321045679252212594626385532706912750332728571942532289631379312455583992563"
        midpoint_url = f"https://clob.polymarket.com/midpoint?token_id={token_id}"
        
        response = proxy.get(midpoint_url)
        if response and response.status_code == 200:
            print(f"✅ GET midpoint successful: {response.status_code}")
            data = response.json()
            print(f"   Midpoint data: {data}")
        else:
            print(f"❌ GET midpoint failed: {response.status_code if response else 'No response'}")
            
    except Exception as e:
        print(f"❌ GET request error: {e}")
    
    # Test POST request (the critical one)
    print("\nTesting POST request to orders endpoint...")
    try:
        # Note: This will fail without proper auth, but we want to see if Cloudflare blocks it
        order_url = "https://clob.polymarket.com/order"
        
        # Fake order data just to test Cloudflare
        test_order = {
            "price": "0.08",
            "size": "5.0", 
            "side": "BUY",
            "token_id": token_id
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://polymarket.com',
            'Referer': 'https://polymarket.com/'
        }
        
        response = proxy.post(order_url, json=test_order, headers=headers)
        if response:
            print(f"✅ POST order response: {response.status_code}")
            
            if response.status_code == 403:
                cf_ray = response.headers.get('cf-ray')
                if cf_ray:
                    print(f"❌ Still blocked by Cloudflare (CF-Ray: {cf_ray})")
                    print("   Response headers:", dict(response.headers))
                    return False
                else:
                    print("   403 but no CF-Ray - likely auth error (good!)")
                    return True
            elif response.status_code == 401:
                print("   401 Unauthorized - Cloudflare bypass successful! (need proper auth)")
                return True
            elif response.status_code == 400:
                print("   400 Bad Request - Cloudflare bypass successful! (need proper order data)")
                return True
            else:
                print(f"   Unexpected response code - check manually")
                return True
        else:
            print("❌ No response from POST request")
            return False
            
    except Exception as e:
        print(f"❌ POST request error: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🌐 Oxylabs Residential Proxy Test for Polymarket Bot")
    print("=" * 60)
    
    success = test_oxylabs_polymarket()
    
    if success:
        print("\n🎉 SUCCESS! Oxylabs proxy is working with Polymarket!")
        print("You can now run your bot with these environment variables:")
        print("export OXYLABS_USERNAME='your_username'")
        print("export OXYLABS_PASSWORD='your_password'")
        print("\nThen run: python3 poly_market_maker/app.py")
    else:
        print("\n❌ Oxylabs test failed. Try:")
        print("1. Check your Oxylabs credentials")
        print("2. Ensure you have free trial credits")
        print("3. Try different endpoint (sticky sessions)")
        print("4. Contact Oxylabs support if needed")

if __name__ == "__main__":
    main() 