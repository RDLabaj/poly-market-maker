#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

def get_active_markets_direct():
    """
    Używa bezpośrednich wywołań API do CLOB żeby znaleźć aktywne rynki
    """
    
    base_url = "https://clob.polymarket.com"
    
    print("=" * 70)
    print("FINDING ACTIVE MARKETS - CLOB API DIRECT")
    print("=" * 70)
    
    try:
        # Get all markets
        print("Fetching all markets...")
        response = requests.get(f"{base_url}/markets", timeout=30)
        response.raise_for_status()
        
        data = response.json()
        markets = data['data']
        
        print(f"Total markets found: {len(markets)}")
        
        active_markets = []
        
        for market in markets:
            try:
                condition_id = market.get('condition_id', '')
                question = market.get('question', 'Unknown')
                active = market.get('active', False)
                closed = market.get('closed', True)
                category = market.get('category', 'Unknown')
                
                # Filtruj tylko aktywne, otwarte rynki
                if active and not closed and condition_id:
                    # Sprawdź order book dla tego rynku
                    try:
                        book_response = requests.get(f"{base_url}/book?token_id={market['tokens'][0]['token_id']}", timeout=10)
                        if book_response.status_code == 200:
                            book = book_response.json()
                            
                            bid_count = len(book.get('bids', []))
                            ask_count = len(book.get('asks', []))
                            
                            # Tylko rynki z aktywnymi orderami
                            if bid_count > 0 or ask_count > 0:
                                # Sprawdź spread
                                best_bid = float(book['bids'][0]['price']) if book.get('bids') else 0
                                best_ask = float(book['asks'][0]['price']) if book.get('asks') else 1
                                spread = best_ask - best_bid if best_bid > 0 and best_ask > 0 else 1
                                
                                market_info = {
                                    'condition_id': condition_id,
                                    'question': question,
                                    'category': category,
                                    'bid_count': bid_count,
                                    'ask_count': ask_count,
                                    'best_bid': best_bid,
                                    'best_ask': best_ask,
                                    'spread': spread,
                                    'token_ids': [token['token_id'] for token in market['tokens']]
                                }
                                
                                active_markets.append(market_info)
                                
                                print(f"\nFOUND ACTIVE MARKET:")
                                print(f"Question: {question}")
                                print(f"Category: {category}")
                                print(f"Condition ID: {condition_id}")
                                print(f"Order book: {bid_count} bids, {ask_count} asks")
                                print(f"Best bid: {best_bid}, Best ask: {best_ask}")
                                print(f"Spread: {spread:.4f}")
                                
                    except Exception as e:
                        # Kontynuuj bez order book info
                        pass
                        
            except Exception as e:
                print(f"Error processing market: {e}")
                continue
        
        return active_markets
        
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return []

def check_specific_markets():
    """
    Sprawdź konkretne condition_id które znamy
    """
    
    print("\n" + "=" * 70)
    print("CHECKING SPECIFIC KNOWN MARKETS")
    print("=" * 70)
    
    # Known markets from previous searches
    known_markets = [
        "0x178dee952f29fb0a77f63df1d59514d15009caeb7c011a5c086aad80e6369f8d",
        "0xdd22472e552920b8438158ea7238bfadfa4f736aa4cee91a6b86c39ead110917",  
        "0x0ebad42a93eedfa8c4ad032ea6a2b5e68e34dbd1f16d5261eabe242c3811ec39",
    ]
    
    base_url = "https://clob.polymarket.com"
    
    working_markets = []
    
    for condition_id in known_markets:
        try:
            print(f"\nChecking: {condition_id}")
            
            # Get market info
            market_response = requests.get(f"{base_url}/markets/{condition_id}", timeout=10)
            
            if market_response.status_code == 200:
                market = market_response.json()
                
                question = market.get('question', 'Unknown')
                active = market.get('active', False)
                closed = market.get('closed', True)
                
                print(f"Question: {question}")
                print(f"Active: {active}, Closed: {closed}")
                
                if active and not closed:
                    # Get order book
                    token_id = market['tokens'][0]['token_id']
                    book_response = requests.get(f"{base_url}/book?token_id={token_id}", timeout=10)
                    
                    if book_response.status_code == 200:
                        book = book_response.json()
                        bid_count = len(book.get('bids', []))
                        ask_count = len(book.get('asks', []))
                        
                        print(f"Order book: {bid_count} bids, {ask_count} asks")
                        
                        if bid_count > 0 or ask_count > 0:
                            working_markets.append({
                                'condition_id': condition_id,
                                'question': question,
                                'token_id': token_id,
                                'bid_count': bid_count,
                                'ask_count': ask_count
                            })
                            print("✅ MARKET IS ACTIVE AND HAS ORDERS!")
                        else:
                            print("❌ No orders in book")
                    else:
                        print(f"❌ Could not get order book: {book_response.status_code}")
                else:
                    print("❌ Market is not active or is closed")
            else:
                print(f"❌ Could not get market info: {market_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking {condition_id}: {e}")
    
    return working_markets

def find_markets_with_recent_trades():
    """
    Znajdź rynki z niedawnymi transakcjami
    """
    
    print("\n" + "=" * 70)
    print("FINDING MARKETS WITH RECENT TRADES")
    print("=" * 70)
    
    base_url = "https://clob.polymarket.com"
    
    try:
        # Get recent trades
        print("Fetching recent trades...")
        trades_response = requests.get(f"{base_url}/trades", timeout=30)
        
        if trades_response.status_code == 200:
            trades = trades_response.json()
            
            # Group trades by market
            market_activity = {}
            
            for trade in trades:
                market = trade.get('market', '')
                if market:
                    if market not in market_activity:
                        market_activity[market] = {
                            'trade_count': 0,
                            'total_volume': 0,
                            'latest_trade': None
                        }
                    
                    market_activity[market]['trade_count'] += 1
                    market_activity[market]['total_volume'] += float(trade.get('size', 0))
                    
                    # Keep latest trade timestamp
                    trade_time = trade.get('time')
                    if not market_activity[market]['latest_trade'] or trade_time > market_activity[market]['latest_trade']:
                        market_activity[market]['latest_trade'] = trade_time
            
            # Sort by trade count
            sorted_markets = sorted(market_activity.items(), 
                                  key=lambda x: x[1]['trade_count'], 
                                  reverse=True)
            
            print(f"\nTop markets by trade activity:")
            
            active_trading_markets = []
            
            for i, (condition_id, activity) in enumerate(sorted_markets[:20]):
                try:
                    # Get market details
                    market_response = requests.get(f"{base_url}/markets/{condition_id}", timeout=10)
                    
                    if market_response.status_code == 200:
                        market = market_response.json()
                        question = market.get('question', 'Unknown')
                        active = market.get('active', False)
                        closed = market.get('closed', True)
                        
                        if active and not closed:
                            print(f"\n{i+1}. {question}")
                            print(f"   Condition ID: {condition_id}")
                            print(f"   Trades: {activity['trade_count']}")
                            print(f"   Volume: ${activity['total_volume']:.2f}")
                            print(f"   Latest trade: {activity['latest_trade']}")
                            
                            active_trading_markets.append({
                                'condition_id': condition_id,
                                'question': question,
                                'trade_count': activity['trade_count'],
                                'volume': activity['total_volume']
                            })
                
                except Exception as e:
                    continue
            
            return active_trading_markets
        
    except Exception as e:
        print(f"Error fetching trades: {e}")
        return []

def test_market_endpoints():
    """
    Test różnych endpointów API
    """
    
    print("\n" + "=" * 70)
    print("TESTING MARKET ENDPOINTS")
    print("=" * 70)
    
    base_url = "https://clob.polymarket.com"
    
    endpoints = [
        "/markets",
        "/sampling-markets", 
        "/simplified-markets",
        "/sampling-simplified-markets"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}?limit=5", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    markets = data['data']
                    print(f"✅ Success: {len(markets)} markets")
                    
                    # Check first market
                    if markets:
                        first_market = markets[0]
                        print(f"   Sample: {first_market.get('question', 'Unknown')[:50]}...")
                        print(f"   Active: {first_market.get('active', False)}")
                        print(f"   Closed: {first_market.get('closed', True)}")
                else:
                    print(f"✅ Success: {len(data)} items (different format)")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE ACTIVE MARKETS SEARCH")
    print("=" * 70)
    
    # Method 1: Direct CLOB API scan
    direct_markets = get_active_markets_direct()
    
    # Method 2: Check known markets
    known_working = check_specific_markets()
    
    # Method 3: Find markets with recent trades
    trading_markets = find_markets_with_recent_trades()
    
    # Method 4: Test different endpoints
    test_market_endpoints()
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 FINAL SUMMARY")
    print("=" * 70)
    
    print(f"Direct scan found: {len(direct_markets)} active markets")
    print(f"Known markets working: {len(known_working)}")
    print(f"Markets with recent trades: {len(trading_markets) if trading_markets else 0}")
    
    # Combine all results (handle None values)
    all_markets = (direct_markets or []) + (known_working or []) + (trading_markets or [])
    
    # Remove duplicates by condition_id
    unique_markets = {}
    for market in all_markets:
        condition_id = market['condition_id']
        if condition_id not in unique_markets:
            unique_markets[condition_id] = market
    
    print(f"\nTotal unique active markets found: {len(unique_markets)}")
    
    if unique_markets:
        print("\n🚀 RECOMMENDED MARKETS FOR BOT:")
        for i, (condition_id, market) in enumerate(unique_markets.items(), 1):
            question = market.get('question', 'Unknown')
            print(f"{i}. {question}")
            print(f"   Condition ID: {condition_id}")
            
            if 'bid_count' in market and 'ask_count' in market:
                print(f"   Order book: {market['bid_count']} bids, {market['ask_count']} asks")
            
            if 'trade_count' in market:
                print(f"   Recent trades: {market['trade_count']}")
                
            print()
    else:
        print("\n❌ No active markets found!")
        print("This could mean:")
        print("1. All markets are currently closed")
        print("2. API endpoints have changed") 
        print("3. Network/authentication issues")
        print("\nTry running this script at different times or check Polymarket.com directly.") 