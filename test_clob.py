#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')
from cloudflare_fix import apply_cloudflare_fix

# Apply fix first
apply_cloudflare_fix()

# Test basic CLOB connection
from py_clob_client.client import ClobClient

print("Testing CLOB connection...")
client = ClobClient(
    'https://clob.polymarket.com', 
    chain_id=137, 
    key='3bd3d35ffd64c7f4a9dc58db585d4ac6d52ffb0b5cc4c9dcd052388c8874cb95'
)

print('CLOB Status:', client.get_ok())
print('Address:', client.get_address())

# Test simple price fetch
try:
    token_id = 97335676421095248000879236735672623727863825668446448330851350298516318572302
    price = client.get_midpoint(token_id)
    print('✅ Price fetch successful:', price)
    
    # Test market info
    market = client.get_market("0x178dee952f29fb0a77f63df1d59514d15009caeb7c011a5c086aad80e6369f8d")
    print('✅ Market fetch successful')
    print('   Active:', market.get('active'))
    print('   Question:', market.get('question', '')[:50] + '...')
    
except Exception as e:
    print('❌ Error:', e) 