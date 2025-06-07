#!/usr/bin/env python3

import os
import sys
from py_clob_client.client import ClobClient

# Load smartproxy
os.environ['SMARTPROXY_USER'] = 'spl3xt28hm'
os.environ['SMARTPROXY_PASS'] = '2+nOn0Qr65sffSsuuL'  
os.environ['SMARTPROXY_ENDPOINT'] = 'gate.decodo.com:10001'

# Import smartproxy after setting env vars
import smartproxy_integration

def main():
    print("🔍 DEBUG: Testing balance retrieval")
    
    # Test market
    condition_id = "0x178dee952f29fb0a77f63df1d59514d15009caeb7c011a5c086aad80e6369f8d"
    
    # Create client
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=137,
        key="3bd3d35ffd64c7f4a9dc58db585d4ac6d52ffb0b5cc4c9dcd052388c8874cb95"
    )
    
    print(f"✅ Client created")
    print(f"📊 Testing condition_id: {condition_id}")
    
    # Test 1: Direct balance call
    try:
        print("\n1️⃣ Testing direct balances...")
        balances = client.get_balances()
        print(f"Direct balances: {balances}")
    except Exception as e:
        print(f"❌ Direct balances failed: {e}")
    
    # Test 2: Balance for specific market
    try:
        print("\n2️⃣ Testing market-specific balances...")
        market_balances = client.get_balances_for_market(condition_id)
        print(f"Market balances: {market_balances}")
        
        # Show detailed analysis
        if market_balances:
            total = sum(market_balances.values()) if market_balances.values() else 0
            print(f"📈 Total balance sum: {total}")
            print(f"🧮 Individual balances:")
            for token, balance in market_balances.items():
                print(f"   {token}: {balance}")
                
    except Exception as e:
        print(f"❌ Market balances failed: {e}")
    
    # Test 3: Check market tokens
    try:
        print("\n3️⃣ Testing market info...")
        market = client.get_market(condition_id)
        print(f"Market info: {market}")
    except Exception as e:
        print(f"❌ Market info failed: {e}")

if __name__ == "__main__":
    main() 