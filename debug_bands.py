#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from poly_market_maker.strategies.bands import Bands
from poly_market_maker.token import Token
from poly_market_maker.order import Order, Side

# Load config
config = {
    "bands": [
        {
            "minMargin": 0.005,
            "avgMargin": 0.01,
            "maxMargin": 0.02,
            "minAmount": 5.0,
            "avgAmount": 6.0,
            "maxAmount": 8.0
        },
        {
            "minMargin": 0.02,
            "avgMargin": 0.03,
            "maxMargin": 0.04,
            "minAmount": 5.0,
            "avgAmount": 7.0,
            "maxAmount": 10.0
        }
    ]
}

# Initialize bands strategy
bands = Bands(config["bands"])

# Test parameters
target_price = 0.085  # 8.5 cents
collateral_balance = 18.0  # USDC
token_balance = 0.0  # No tokens
orders = []  # No existing orders

print("🔍 DEBUGGING BANDS STRATEGY")
print(f"Target price: {target_price}")
print(f"Collateral balance: {collateral_balance}")
print(f"Token balance: {token_balance}")
print(f"Existing orders: {len(orders)}")
print()

# Test TokenA (YES)
print("📊 TESTING TOKEN A (YES):")
new_orders_a = bands.new_orders(
    orders=orders,
    collateral_balance=collateral_balance,
    token_balance=token_balance,
    target_price=target_price,
    buy_token=Token.A
)

print(f"New orders for Token A: {len(new_orders_a)}")
for i, order in enumerate(new_orders_a):
    print(f"  Order {i+1}: {order.side} {order.size:.2f} @ {order.price:.3f} (Cost: {order.size * order.price:.2f} USDC)")

print()

# Test TokenB (NO) 
print("📊 TESTING TOKEN B (NO):")
target_price_b = 1.0 - target_price  # 0.915
new_orders_b = bands.new_orders(
    orders=orders,
    collateral_balance=collateral_balance,
    token_balance=token_balance,
    target_price=target_price_b,
    buy_token=Token.B
)

print(f"New orders for Token B: {len(new_orders_b)}")
for i, order in enumerate(new_orders_b):
    print(f"  Order {i+1}: {order.side} {order.size:.2f} @ {order.price:.3f} (Cost: {order.size * order.price:.2f} USDC)")

print()
print("✅ DEBUG COMPLETE") 