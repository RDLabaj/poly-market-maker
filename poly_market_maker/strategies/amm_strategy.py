from poly_market_maker.orderbook import OrderBook
from poly_market_maker.constants import MIN_SIZE
from poly_market_maker.order import Order

from poly_market_maker.strategies.amm import AMMManager, AMMConfig
from poly_market_maker.strategies.base_strategy import BaseStrategy


class OrderType:
    def __init__(self, order: Order):
        self.price = order.price
        self.side = order.side
        self.token = order.token

    def __eq__(self, other):
        if isinstance(other, OrderType):
            return (
                self.price == other.price
                and self.side == other.side
                and self.token == other.token
            )
        return False

    def __hash__(self):
        return hash((self.price, self.side, self.token))

    def __repr__(self):
        return f"OrderType[price={self.price}, side={self.side}, token={self.token}]"


class AMMStrategy(BaseStrategy):
    def __init__(
        self,
        config_dict: dict,
    ):
        assert isinstance(config_dict, dict)

        super().__init__()
        self.amm_manager = AMMManager(self._get_config(config_dict))

    @staticmethod
    def _get_config(config: dict):
        required_params = ['p_min', 'p_max', 'spread', 'delta', 'depth', 'max_collateral']
        missing_params = [param for param in required_params if param not in config]
        
        if missing_params:
            raise ValueError(f"Missing required AMM config parameters: {missing_params}")
        
        # Validate parameter ranges
        if config['p_min'] >= config['p_max']:
            raise ValueError("p_min must be less than p_max")
        if config['spread'] < 0:
            raise ValueError("spread must be non-negative")
        if config['max_collateral'] <= 0:
            raise ValueError("max_collateral must be positive")
            
        return AMMConfig(
            p_min=config.get("p_min"),
            p_max=config.get("p_max"),
            spread=config.get("spread"),
            delta=config.get("delta"),
            depth=config.get("depth"),
            max_collateral=config.get("max_collateral"),
        )

    def get_orders(self, orderbook: OrderBook, target_prices):
        orders_to_cancel = []
        orders_to_place = []

        try:
            expected_orders = self.amm_manager.get_expected_orders(
                target_prices,
                orderbook.balances,
            )
            expected_order_types = set(OrderType(order) for order in expected_orders)

            orders_to_cancel += list(
                filter(
                    lambda order: OrderType(order) not in expected_order_types,
                    orderbook.orders,
                )
            )

            for order_type in expected_order_types:
                open_orders = [
                    order for order in orderbook.orders if OrderType(order) == order_type
                ]
                open_size = sum(order.size for order in open_orders)
                expected_size = sum(
                    order.size
                    for order in expected_orders
                    if OrderType(order) == order_type
                )

                # if open_size too big, cancel all orders of this type
                if open_size > expected_size:
                    orders_to_cancel += open_orders
                    new_size = expected_size
                # otherwise get the remaining size
                else:
                    new_size = round(expected_size - open_size, 2)

                if new_size >= MIN_SIZE:
                    orders_to_place += [
                        self._new_order_from_order_type(order_type, new_size)
                    ]
        except Exception as e:
            self.logger.error(f"Error generating AMM orders: {e}")
            # Return empty lists to prevent strategy crash
            return ([], [])

        return (orders_to_cancel, orders_to_place)

    @staticmethod
    def _new_order_from_order_type(order_type: OrderType, size: float) -> Order:
        return Order(
            price=order_type.price,
            size=size,
            side=order_type.side,
            token=order_type.token,
        )
