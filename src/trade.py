# CLEAN
class Trade:

    def __init__(self, quantity, buy_order_id, sell_order_id):
        self.buy_order_id = buy_order_id
        self.sell_order_id = sell_order_id
        self.price = self.get_price()
        self.quantity = quantity
        self.value = self.quantity * self.price
        # update order quantities
        buy_order_id.update_order_quantities(self)
        sell_order_id.update_order_quantities(self)
        # update credits and ownerships
        buy_order_id.broker_id.decrease_credit(self)
        sell_order_id.broker_id.increase_credit(self)
        buy_order_id.shareholder_id.increase_ownership(self)
        sell_order_id.shareholder_id.decrease_ownership(self)

    def __repr__(self):
        return "\n\tTrade\t%s\t%s\t%s\t%s" \
            % (self.price, self.quantity, self.buy_order_id.id, self.sell_order_id.id)

    def get_price(self):
        return self.buy_order_id.price \
            if self.buy_order_id.is_in_queue \
            else self.sell_order_id.price

    def rollback_trade(self):
        self.buy_order_id.rollback_update_order_quantities(self)
        self.sell_order_id.rollback_update_order_quantities(self)
        self.buy_order_id.broker_id.rollback_decrease_credit(self)
        self.sell_order_id.broker_id.rollback_increase_credit(self)
        self.buy_order_id.shareholder_id.rollback_increase_ownership(self)
        self.sell_order_id.shareholder_id.rollback_decrease_ownership(self)
