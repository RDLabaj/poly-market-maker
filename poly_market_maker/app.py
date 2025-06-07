import logging
from prometheus_client import start_http_server
import time

# Apply Cloudflare bypass fix BEFORE importing any py_clob_client modules
import os

# Try residential proxies first (best for Cloudflare bypass)
smartproxy_username = os.getenv('SMARTPROXY_USERNAME')
smartproxy_password = os.getenv('SMARTPROXY_PASSWORD')
oxylabs_username = os.getenv('OXYLABS_USERNAME')
oxylabs_password = os.getenv('OXYLABS_PASSWORD')

proxy_activated = False

# 1. Try SmartProxy first (3-day FREE trial)
if smartproxy_username and smartproxy_password and not proxy_activated:
    try:
        from smartproxy_integration import setup_smartproxy
        if setup_smartproxy(smartproxy_username, smartproxy_password):
            print("✅ SmartProxy residential proxy activated - 3-day FREE trial!")
            proxy_activated = True
        else:
            print("❌ SmartProxy setup failed")
    except ImportError:
        print("❌ SmartProxy integration not found")

# 2. Try Oxylabs if SmartProxy failed
if oxylabs_username and oxylabs_password and not proxy_activated:
    try:
        from oxylabs_proxy import setup_oxylabs_proxy
        if setup_oxylabs_proxy(oxylabs_username, oxylabs_password):
            print("✅ Oxylabs residential proxy activated!")
            proxy_activated = True
        else:
            print("❌ Oxylabs setup failed")
    except ImportError:
        print("❌ Oxylabs integration not found")

# 3. Fallback to other bypass methods if no proxy worked
if not proxy_activated:
    print("⚠️ No residential proxy available, trying fallback methods...")
    try:
        from cloudflare_fix import apply_cloudflare_fix
        apply_cloudflare_fix()
        print("✅ Basic Cloudflare fix applied")
    except ImportError:
        try:
            from flaresolverr_integration import setup_flaresolverr_bypass
            if setup_flaresolverr_bypass():
                print("✅ FlareSolverr Cloudflare bypass activated")
            else:
                print("❌ FlareSolverr setup failed")
        except ImportError:
            print("❌ No Cloudflare bypass available - POST requests will likely fail!")

from poly_market_maker.args import get_args
from poly_market_maker.price_feed import PriceFeedClob
from poly_market_maker.gas import GasStation, GasStrategy
from poly_market_maker.utils import setup_logging, setup_web3
from poly_market_maker.order import Order, Side
from poly_market_maker.market import Market
from poly_market_maker.token import Token, Collateral
from poly_market_maker.clob_api import ClobApi
from poly_market_maker.lifecycle import Lifecycle
from poly_market_maker.orderbook import OrderBookManager
from poly_market_maker.contracts import Contracts
from poly_market_maker.metrics import keeper_balance_amount
from poly_market_maker.strategy import StrategyManager


class App:
    """Market maker keeper on Polymarket CLOB"""

    def __init__(self, args: list):
        setup_logging()
        self.logger = logging.getLogger(__name__)

        args = get_args(args)
        self.sync_interval = args.sync_interval

        # self.min_tick = args.min_tick
        # self.min_size = args.min_size

        # server to expose the metrics.
        self.metrics_server_port = args.metrics_server_port
        start_http_server(self.metrics_server_port)

        self.web3 = setup_web3(args.rpc_url, args.private_key)
        self.address = self.web3.eth.account.from_key(args.private_key).address
        self.funder_address = getattr(args, 'funder_address', None)

        self.clob_api = ClobApi(
            host=args.clob_api_url,
            chain_id=self.web3.eth.chain_id,
            private_key=args.private_key,
            funder_address=self.funder_address,
            signature_type=getattr(args, 'signature_type', 0),
        )

        self.gas_station = GasStation(
            strat=GasStrategy(args.gas_strategy),
            w3=self.web3,
            url=args.gas_station_url,
            fixed=args.fixed_gas_price,
        )
        self.contracts = Contracts(self.web3, self.gas_station)

        self.market = Market(
            args.condition_id,
            self.clob_api.get_collateral_address(),
        )

        self.price_feed = PriceFeedClob(self.market, self.clob_api)

        self.order_book_manager = OrderBookManager(
            args.refresh_frequency, max_workers=1
        )
        self.order_book_manager.get_orders_with(self.get_orders)
        self.order_book_manager.get_balances_with(self.get_balances)
        self.order_book_manager.cancel_orders_with(
            lambda order: self.clob_api.cancel_order(order.id)
        )
        self.order_book_manager.place_orders_with(self.place_order)
        self.order_book_manager.cancel_all_orders_with(
            lambda _: self.clob_api.cancel_all_orders()
        )
        self.order_book_manager.start()

        self.strategy_manager = StrategyManager(
            args.strategy,
            args.strategy_config,
            self.price_feed,
            self.order_book_manager,
        )

    """
    main
    """

    def main(self):
        self.logger.debug(self.sync_interval)
        with Lifecycle() as lifecycle:
            lifecycle.on_startup(self.startup)
            lifecycle.every(self.sync_interval, self.synchronize)  # Sync every 5s
            lifecycle.on_shutdown(self.shutdown)

    """
    lifecycle
    """

    def startup(self):
        self.logger.info("Running startup callback...")
        # Temporarily disable approval check due to Unicode/web3.py issues
        # self.approve()
        time.sleep(5)  # 5 second initial delay so that bg threads fetch the orderbook
        self.logger.info("Startup complete!")

    def synchronize(self):
        """
        Synchronize the orderbook by cancelling orders out of bands and placing new orders if necessary
        """
        self.logger.debug("Synchronizing orderbook...")
        self.strategy_manager.synchronize()
        self.logger.debug("Synchronized orderbook!")

    def shutdown(self):
        """
        Shut down the keeper
        """
        self.logger.info("Keeper shutting down...")
        self.order_book_manager.cancel_all_orders()
        self.logger.info("Keeper is shut down!")

    """
    handlers
    """

    def get_balances(self) -> dict:
        """
        Fetch the onchain balances of collateral and conditional tokens for the keeper
        """
        # TEMPORARY: Use fake balances to avoid Unicode/web3.py error
        # Will use CLOB API for actual balance management
        balance_address = self.funder_address or self.address
        self.logger.debug(f"Getting fake balances for address: {balance_address} (Unicode workaround)")

        # Return fake but reasonable balances - bot will use CLOB API for actual trading
        collateral_balance = 18.0  # Approximately our USDC.e balance
        token_A_balance = 0.0
        token_B_balance = 0.0

        self.logger.debug(f"Fake balances: USDC.e={collateral_balance}, Token.A={token_A_balance}, Token.B={token_B_balance}")

        return {
            Collateral: collateral_balance,
            Token.A: token_A_balance,
            Token.B: token_B_balance,
        }

    def get_orders(self) -> list[Order]:
        orders = self.clob_api.get_orders(self.market.condition_id)
        return [
            Order(
                size=order_dict["size"],
                price=order_dict["price"],
                side=Side(order_dict["side"]),
                token=self.market.token(order_dict["token_id"]),
                id=order_dict["id"],
            )
            for order_dict in orders
        ]

    def place_order(self, new_order: Order) -> Order:
        order_id = self.clob_api.place_order(
            price=new_order.price,
            size=new_order.size,
            side=new_order.side.value,
            token_id=self.market.token_id(new_order.token),
        )
        return Order(
            price=new_order.price,
            size=new_order.size,
            side=new_order.side,
            id=order_id,
            token=new_order.token,
        )

    def approve(self):
        """
        Approve the keeper on the collateral and conditional tokens
        """
        collateral = self.clob_api.get_collateral_address()
        conditional = self.clob_api.get_conditional_address()
        exchange = self.clob_api.get_exchange()

        self.contracts.max_approve_erc20(collateral, self.address, exchange)
        self.contracts.max_approve_erc1155(conditional, self.address, exchange)
