class OrderBook:
    def __init__(self):
        self.buy_order_ids = []
        self.sell_order_ids = []

    def __repr__(self):
        all_orders = self.buy_order_ids + self.sell_order_ids
        output = "\tOrders\t%s" % len(all_orders)
        for order in all_orders:
            output += order.__repr__()
        return output

    def add_order(self, order):
        if order.is_buy:
            self.buy_order_ids.append(order)
            self.sort_buy_orders()
        else:
            self.sell_order_ids.append(order)
            self.sort_sell_orders()
        order.order_added_to_queue()

    def sort_buy_orders(self):
        self.buy_order_ids.sort(key=lambda x: x.price, reverse=True)

    def sort_sell_orders(self):
        self.sell_order_ids.sort(key=lambda x: x.price, reverse=False)

    def remove_order(self, order):
        if order.is_buy:
            self.buy_order_ids.remove(order)
            self.sort_buy_orders()
        else:
            self.sell_order_ids.remove(order)
            self.sort_sell_orders()
        order.order_removed_from_queue()

    def get_first_buy_order(self):
        valid_buy_orders = list(filter(lambda order: order.quantity > 0, self.buy_order_ids))
        return valid_buy_orders[0] if len(valid_buy_orders) > 0 else None

    def get_first_sell_order(self):
        valid_sell_orders = list(filter(lambda order: order.quantity > 0, self.sell_order_ids))
        return valid_sell_orders[0] if len(valid_sell_orders) > 0 else None

    def remove_empty_orders(self):
        remove_list = list(filter(lambda x: x.quantity == 0, self.sell_order_ids + self.buy_order_ids))
        for order in remove_list:
            self.remove_order(order)

    def rollback_order_book(self, trade):
        order = trade.sell_order_id if trade.sell_order_id.is_in_queue else trade.buy_order_id
        queue = self.buy_order_ids if order.is_buy else self.sell_order_ids
        queue.remove(order)
        queue.insert(0, order)

    def get_order(self, order_id):
        order = list(filter(lambda x: x.id == order_id,
                            self.buy_order_ids + self.sell_order_ids))
        return False if not order else order[0]

    def get_order_index(self, order):
        return self.buy_order_ids.index(order) if order.is_buy else self.sell_order_ids.index(order)

    def insert_order(self, order, index):
        if order.is_buy:
            self.buy_order_ids.insert(index, order)
        else:
            self.sell_order_ids.insert(index, order)
        order.order_added_to_queue()
