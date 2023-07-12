from src import tc_runner
from src.broker import print_credits
from src.order_book import OrderBook
from src.shareholder import print_ownerships
from src.trade import Trade


class MatchingEngine:
    def new_order_request(self, order):
        self.last_order_type = "New"
        order_info = order.__repr__().replace("\n\tOrder\t", "")
        tc_runner.print_output(order_info)
        self.trades.clear()
        response = self.add_order(order)
        tc_runner.print_output("NewOrderRs\t%s" % response)

    def add_order(self, order):
        def can_have_trades():
            # no fields value are changing in this function
            return order.has_valid_attrs()\
                and self.environment.validate_order_price_limit(order)\
                and self.environment.validate_order_quantity_limit(order, self.order_book)\
                and order.shareholder_id.ownership_validation(order)

        def is_order_accepted():
            return order.broker_id.credit_validation(order)

        def can_be_added_to_the_queue():
            # no fields value are changing in this function
            return order.quantity > 0

        first_state = self.__repr__()
        if can_have_trades():
            self.match(order)
            if is_order_accepted():
                if can_be_added_to_the_queue():
                    self.order_book.add_order(order)
                self.order_book.remove_empty_orders()
                return "Accepted"
            self.rollback_by_trades(first_state)
        return "Rejected"

    def match(self, new_order):
        buy_order = new_order if new_order.is_buy else self.order_book.get_first_buy_order()
        sell_order = new_order if not new_order.is_buy else self.order_book.get_first_sell_order()
        old_order = buy_order if buy_order != new_order else sell_order
        if sell_order and buy_order:
            if sell_order.price <= buy_order.price:
                trade_qty = min(new_order.quantity, old_order.get_maximum_quantity_to_trade())
                if trade_qty > 0:
                    self.trades.append(Trade(trade_qty, buy_order, sell_order))
                    if old_order.disclosed_quantity == 0 < old_order.peak_size:
                        old_order.set_disclosed_quantity()
                        self.order_book.remove_order(old_order)
                        self.order_book.add_order(old_order)
                    self.match(new_order)

    # ////////////////////////////////////////////////////////////////////////////////////
    def cancel_order(self, order_id):
        #   like add_order returns the res of the cancel order
        pass

    def rollback_by_trades(self, first_state):
        trades = self.print_trades()
        while self.trades:
            last_trade = self.trades[-1]
            last_trade.rollback_trade()
            self.order_book.rollback_order_book(last_trade)
            self.trades.remove(last_trade)
        after_rollback = self.__repr__()
        assert after_rollback == first_state, "\n%s\nROLLBACK ERROR:\n" \
                                              "expected:\n%s\n" \
                                              "output:\n%s" % (trades, first_state, after_rollback)

    def __init__(self, environment):
        self.trades = []
        self.order_book = OrderBook()
        self.environment = environment
        self.last_order_type = None

    def __repr__(self):
        output = "" if self.last_order_type == "Cancel" else self.print_trades() + "\n"
        output += self.order_book.__repr__()
        output += print_credits()
        output += print_ownerships()
        output += "\n" + self.environment.__repr__()
        return output

    def print_trades(self):
        output = "\tTrades\t%s" % len(self.trades)
        for trade in self.trades:
            output += trade.__repr__()
        return output
