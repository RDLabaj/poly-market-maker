#!/usr/bin/env python3
"""
Universal Multi-Market Manager for Polymarket
Automatycznie pobiera i zarządza marketami według konfigurowalnych filtrów.
"""

import asyncio
import logging
import json
import os
import requests
import time
import yaml
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass

from poly_market_maker.app import App
from poly_market_maker.constants import MAX_DECIMALS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MarketInfo:
    condition_id: str
    question: str
    end_date: str
    category: str = None
    active: bool = True
    tags: List[str] = None

@dataclass
class MarketFilter:
    """Configurable market filter"""
    name: str
    keywords: List[str] = None
    excluded_keywords: List[str] = None
    categories: List[str] = None
    tags: List[str] = None
    min_liquidity: float = 0.0
    custom_filter: Optional[Callable] = None
    enabled: bool = True

class UniversalMarketManager:
    """Universal manager for multiple market types"""
    
    def __init__(self, config_file: str = "market_config.yaml"):
        self.config_file = config_file
        self.load_config()
        self.load_market_filters()
        self.active_markets: Dict[str, MarketInfo] = {}
        self.market_makers: Dict[str, App] = {}
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
    def load_config(self):
        """Load configuration from environment and config file"""
        self.private_key = os.getenv('PRIVATE_KEY')
        self.rpc_url = os.getenv('RPC_URL')
        self.clob_api_url = os.getenv('CLOB_API_URL', 'https://clob.polymarket.com')
        self.strategy = os.getenv('STRATEGY', 'amm')
        self.config_path = os.getenv('CONFIG', './config/amm.json')
        self.refresh_interval = int(os.getenv('REFRESH_INTERVAL', '300'))  # 5 min
        self.max_markets = int(os.getenv('MAX_MARKETS', '10'))
        self.max_workers = int(os.getenv('MAX_WORKERS', '10'))
        
        if not all([self.private_key, self.rpc_url]):
            raise ValueError("PRIVATE_KEY and RPC_URL must be set")
    
    def load_market_filters(self):
        """Load market filters from config file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                        
                self.filters = [
                    MarketFilter(**filter_config) 
                    for filter_config in config_data.get('filters', [])
                ]
                logger.info(f"Loaded {len(self.filters)} market filters")
                
            except Exception as e:
                logger.error(f"Error loading config file {self.config_file}: {e}")
                self.filters = self.get_default_filters()
        else:
            logger.info(f"Config file {self.config_file} not found, using defaults")
            self.filters = self.get_default_filters()
            self.create_default_config()
    
    def get_default_filters(self) -> List[MarketFilter]:
        """Return default market filters"""
        return [
            MarketFilter(
                name="NBA",
                keywords=["NBA", "basketball", "Lakers", "Warriors", "Heat", "Bulls", "Celtics", "Finals"],
                excluded_keywords=["college", "NCAA", "high school"],
                enabled=True
            ),
            MarketFilter(
                name="NFL",
                keywords=["NFL", "football", "Super Bowl", "playoffs", "Chiefs", "Patriots", "Cowboys"],
                excluded_keywords=["college", "NCAA", "fantasy"],
                enabled=False  # Disabled by default
            ),
            MarketFilter(
                name="Elections",
                keywords=["election", "vote", "president", "candidate", "polling"],
                categories=["Politics", "US-current-affairs"],
                enabled=False
            ),
            MarketFilter(
                name="Crypto",
                keywords=["Bitcoin", "BTC", "Ethereum", "ETH", "crypto", "price"],
                categories=["Crypto"],
                min_liquidity=100.0,
                enabled=False
            )
        ]
    
    def create_default_config(self):
        """Create default config file"""
        try:
            config_data = {
                "filters": [
                    {
                        "name": "NBA",
                        "keywords": ["NBA", "basketball", "Lakers", "Warriors", "Heat", "Bulls", "Celtics", "Finals"],
                        "excluded_keywords": ["college", "NCAA", "high school"],
                        "enabled": True
                    },
                    {
                        "name": "NFL", 
                        "keywords": ["NFL", "football", "Super Bowl", "playoffs"],
                        "excluded_keywords": ["college", "NCAA"],
                        "enabled": False
                    },
                    {
                        "name": "Elections",
                        "keywords": ["election", "vote", "president", "candidate"],
                        "categories": ["Politics", "US-current-affairs"],
                        "enabled": False
                    },
                    {
                        "name": "Crypto",
                        "keywords": ["Bitcoin", "BTC", "Ethereum", "ETH", "crypto"],
                        "categories": ["Crypto"],
                        "min_liquidity": 100.0,
                        "enabled": False
                    }
                ]
            }
            
            with open(self.config_file, 'w') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    yaml.dump(config_data, f, default_flow_style=False)
                else:
                    json.dump(config_data, f, indent=2)
                    
            logger.info(f"Created default config file: {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error creating default config: {e}")
    
    def match_market(self, market_data: dict) -> List[str]:
        """Check if market matches any enabled filters"""
        matched_filters = []
        question = market_data.get('question', '').upper()
        category = market_data.get('category', '')
        liquidity = market_data.get('liquidity', 0)
        
        for filter_config in self.filters:
            if not filter_config.enabled:
                continue
                
            match = False
            
            # Check keywords
            if filter_config.keywords:
                if any(keyword.upper() in question for keyword in filter_config.keywords):
                    match = True
            
            # Check excluded keywords
            if filter_config.excluded_keywords and match:
                if any(excluded.upper() in question for excluded in filter_config.excluded_keywords):
                    match = False
                    continue
            
            # Check categories
            if filter_config.categories and category:
                if category in filter_config.categories:
                    match = True
            
            # Check minimum liquidity
            if filter_config.min_liquidity > 0:
                if liquidity < filter_config.min_liquidity:
                    match = False
            
            # Custom filter function
            if filter_config.custom_filter:
                match = match and filter_config.custom_filter(market_data)
            
            if match:
                matched_filters.append(filter_config.name)
        
        return matched_filters
            
    def fetch_markets(self) -> List[MarketInfo]:
        """Fetch all active markets matching configured filters"""
        logger.info("Fetching active markets...")
        
        try:
            url = "https://gamma-api.polymarket.com/markets"
            params = {
                'active': 'true',
                'closed': 'false',
                'limit': 200  # Increased limit for more coverage
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            markets_data = response.json()
            
            matching_markets = []
            filter_counts = {}
            
            for market in markets_data:
                matched_filters = self.match_market(market)
                
                if matched_filters:
                    # Count matches per filter
                    for filter_name in matched_filters:
                        filter_counts[filter_name] = filter_counts.get(filter_name, 0) + 1
                    
                    market_info = MarketInfo(
                        condition_id=market.get('conditionId'),
                        question=market.get('question'),
                        end_date=market.get('end_date'),
                        category=market.get('category'),
                        active=market.get('active', True),
                        tags=matched_filters
                    )
                    matching_markets.append(market_info)
                    
            # Log statistics
            logger.info(f"Found {len(matching_markets)} matching markets")
            for filter_name, count in filter_counts.items():
                logger.info(f"  {filter_name}: {count} markets")
                
            # SAFETY: Limit to 3 markets for testing
            test_limit = min(3, self.max_markets)
            if len(matching_markets) > test_limit:
                logger.warning(f"⚠️  LIMITED to {test_limit} markets for safety testing!")
                matching_markets = matching_markets[:test_limit]
            
            return matching_markets
            
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []
    
    def create_market_maker(self, market: MarketInfo) -> App:
        """Create a market maker instance for a specific market"""
        try:
            args = [
                '--private-key', self.private_key,
                '--rpc-url', self.rpc_url,
                '--clob-api-url', self.clob_api_url,
                '--condition-id', market.condition_id,
                '--strategy', self.strategy,
                '--strategy-config', self.config_path,
                '--sync-interval', '60',
                '--refresh-frequency', '10'
            ]
            
            logger.info(f"Creating market maker for: {market.question}")
            logger.info(f"  Tags: {', '.join(market.tags or [])}")
            
            market_maker = App(args)
            return market_maker
            
        except Exception as e:
            logger.error(f"Error creating market maker for {market.condition_id}: {e}")
            return None
    
    def run_market_maker(self, market: MarketInfo):
        """Run a market maker in a separate thread"""
        try:
            logger.info(f"Starting market maker for: {market.question}")
            market_maker = self.create_market_maker(market)
            
            if market_maker:
                self.market_makers[market.condition_id] = market_maker
                market_maker.main()
                
        except Exception as e:
            logger.error(f"Error running market maker for {market.condition_id}: {e}")
            if market.condition_id in self.market_makers:
                del self.market_makers[market.condition_id]
    
    def update_markets(self):
        """Update the list of active markets and start new market makers"""
        current_markets = self.fetch_markets()
        
        current_ids = {market.condition_id for market in current_markets}
        active_ids = set(self.active_markets.keys())
        
        # Start new markets
        new_markets = [m for m in current_markets if m.condition_id not in active_ids]
        for market in new_markets:
            logger.info(f"Starting new market: {market.question}")
            logger.info(f"  Categories: {', '.join(market.tags or [])}")
            self.active_markets[market.condition_id] = market
            
            future = self.executor.submit(self.run_market_maker, market)
            
        # Remove inactive markets
        inactive_ids = active_ids - current_ids
        for inactive_id in inactive_ids:
            if inactive_id in self.active_markets:
                logger.info(f"Removing inactive market: {self.active_markets[inactive_id].question}")
                del self.active_markets[inactive_id]
                
                if inactive_id in self.market_makers:
                    try:
                        del self.market_makers[inactive_id]
                    except Exception as e:
                        logger.error(f"Error stopping market maker {inactive_id}: {e}")
    
    def get_status(self) -> Dict:
        """Get current status of all market makers"""
        # Group markets by tags
        tag_stats = {}
        for market in self.active_markets.values():
            if market.tags:
                for tag in market.tags:
                    if tag not in tag_stats:
                        tag_stats[tag] = {'total': 0, 'running': 0}
                    tag_stats[tag]['total'] += 1
                    if market.condition_id in self.market_makers:
                        tag_stats[tag]['running'] += 1
        
        return {
            'active_markets': len(self.active_markets),
            'running_market_makers': len(self.market_makers),
            'enabled_filters': [f.name for f in self.filters if f.enabled],
            'tag_statistics': tag_stats,
            'markets': [
                {
                    'condition_id': market.condition_id,
                    'question': market.question[:100] + "..." if len(market.question) > 100 else market.question,
                    'tags': market.tags,
                    'end_date': market.end_date,
                    'has_market_maker': market.condition_id in self.market_makers
                }
                for market in self.active_markets.values()
            ]
        }
    
    def run(self):
        """Main run loop"""
        logger.info("🚀 Starting Universal Multi-Market Manager...")
        logger.info(f"Strategy: {self.strategy}")
        logger.info(f"Config file: {self.config_file}")
        logger.info(f"Config path: {self.config_path}")
        logger.info(f"Max markets: {self.max_markets}")
        logger.info(f"Refresh interval: {self.refresh_interval}s")
        
        enabled_filters = [f.name for f in self.filters if f.enabled]
        logger.info(f"Enabled filters: {', '.join(enabled_filters)}")
        
        try:
            while True:
                try:
                    self.update_markets()
                    
                    status = self.get_status()
                    logger.info(f"Status: {status['active_markets']} markets, {status['running_market_makers']} running")
                    
                    if status['tag_statistics']:
                        for tag, stats in status['tag_statistics'].items():
                            logger.info(f"  {tag}: {stats['running']}/{stats['total']} running")
                    
                    time.sleep(self.refresh_interval)
                    
                except KeyboardInterrupt:
                    logger.info("Received interrupt signal, shutting down...")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(60)
                    
        finally:
            logger.info("Shutting down market makers...")
            self.executor.shutdown(wait=True)

def main():
    """Main entry point"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Allow custom config file from environment
        config_file = os.getenv('MARKET_CONFIG', 'market_config.yaml')
        
        manager = UniversalMarketManager(config_file)
        manager.run()
        
    except Exception as e:
        logger.error(f"Failed to start Multi-Market Manager: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main()) 