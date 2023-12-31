from src import tc_runner
from src.broker import print_credits
from src.order_book import OrderBook
from src.shareholder import print_ownerships
from src.trade import Trade


class MatchingEngine:
    def __init__(self, environment):
        self.trades = []
        self.order_book = OrderBook()
        self.environment = environment
        self.last_request_type = None

    def new_request(self, req_type, order=False):
        self.last_request_type = req_type
        order_info = order.__repr__().replace("\n\tOrder\t", "") if order else ""
        tc_runner.print_output(order_info)
        self.trades.clear()

    def cancel_order_request(self, order_id, is_buy_order):
        self.new_request("Cancel")
        order = self.order_book.get_order(order_id)
        if order and order.is_buy == is_buy_order:
            self.order_book.remove_order(order)
            tc_runner.print_output("CancelOrderRs\tAccepted")
        else:
            tc_runner.print_output("CancelOrderRs\tRejected")

    def replace_order_request(self, old_order_id, new_order):
        def can_replace():
            return old_order.broker_id.id == new_order.broker_id.id \
                and old_order.shareholder_id.id == new_order.shareholder_id.id\
                and old_order.is_buy == new_order.is_buy\
                and new_order.min_qty == 0

        self.new_request("Replace", new_order)
        old_order = self.order_book.get_order(old_order_id)
        if old_order and can_replace():
            old_order_index = self.order_book.get_order_index(old_order)
            self.order_book.remove_order(old_order)
            new_order_response = self.add_order(new_order)
            if new_order_response == "Rejected":
                self.order_book.insert_order(old_order, old_order_index)
            tc_runner.print_output("ReplaceOrderRs\t%s" % new_order_response)
        else:
            tc_runner.print_output("ReplaceOrderRs\tRejected")

    def new_order_request(self, order):
        self.new_request("New", order)
        response = self.add_order(order)
        tc_runner.print_output("NewOrderRs\t%s" % response)

    def add_order(self, order):
        # no fields value are changing in this sub functions
        def can_have_trades():
            return order.has_valid_attrs() \
                and self.environment.validate_order_price_limit(order) \
                and self.environment.validate_order_quantity_limit(order) \
                and order.shareholder_id.ownership_validation(order)

        def is_order_eliminated():
            return total_traded_qty < order.min_qty or (order.fill_and_kill and total_traded_qty == 0)

        def is_order_accepted():
            return order.broker_id.credit_validation(order) or (
                        order.fill_and_kill and order.broker_id.free_credit >= 0)

        def can_be_added_to_the_queue():
            return order.quantity > 0 and not order.fill_and_kill

        first_state = self.__repr__()
        if can_have_trades():
            self.match(order)
            total_traded_qty = sum([trade.quantity for trade in self.trades])
            if is_order_eliminated():
                self.rollback_by_trades(first_state)
                return "Eliminated"
            elif is_order_accepted():
                if can_be_added_to_the_queue():
                    self.order_book.add_order(order)
                self.order_book.remove_empty_orders()
                return "Accepted"
            else:
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
                    if old_order.disclosed_quantity == trade_qty:
                        self.order_book.remove_order(old_order)
                        self.order_book.add_order(old_order)
                    self.trades.append(Trade(trade_qty, buy_order, sell_order))
                    self.match(new_order)

    def rollback_by_trades(self, first_state):
        def assert_rollback():
            after_rollback = self.__repr__()
            assert after_rollback == first_state, "\n%s\nROLLBACK ERROR:\n" \
                                                  "expected:\n%s\n" \
                                                  "output:\n%s" % (trades, first_state, after_rollback)

        trades = self.print_trades()
        while self.trades:
            last_trade = self.trades[-1]
            last_trade.rollback_trade()
            self.order_book.rollback_order_book(last_trade)
            self.trades.remove(last_trade)
        assert_rollback()

    def __repr__(self):
        output = "" if self.last_request_type == "Cancel" else self.print_trades() + "\n"
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
