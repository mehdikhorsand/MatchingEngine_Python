import itertools

from src import broker, shareholder


class Order:
    counter = itertools.count(1)

    def __init__(self, broker_id, shareholder_id, price, quantity, is_buy, min_qty, fill_and_kill, peak_size):
        self.id = next(Order.counter)
        print("-----------------------------\norder_id:", self.id)
        self.broker_id = broker.get_broker_by_id(broker_id)
        self.shareholder_id = shareholder.get_shareholder_by_id(shareholder_id)
        self.quantity = quantity
        self.price = price
        self.is_buy = is_buy
        self.min_qty = min_qty
        self.fill_and_kill = fill_and_kill
        self.peak_size = peak_size
        self.disclosed_quantity = 0
        self.is_in_queue = False

    def __repr__(self):
        return "\n\tOrder\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
            "Limit" if self.peak_size == 0 else "Iceberg", self.id, self.broker_id.id, self.shareholder_id.id,
            self.price, self.quantity, "BUY " if self.is_buy else "SELL", self.min_qty,
            "FAK" if self.fill_and_kill else "---", 0 if self.peak_size == 0 else self.disclosed_quantity)

    def has_valid_attrs(self):
        if self.fill_and_kill and (self.peak_size > 0 or self.min_qty > 0):
            return False
        return self.peak_size <= self.quantity and self.min_qty <= self.quantity

    def set_disclosed_quantity(self):
        self.disclosed_quantity = min(self.quantity, self.disclosed_quantity)

    def get_maximum_quantity_to_trade(self):
        return self.quantity if self.peak_size == 0 else self.disclosed_quantity

    def update_order_quantities(self, trade):
        self.quantity -= trade.quantity

    def rollback_update_order_quantities(self, trade):
        self.quantity += trade.quantity
