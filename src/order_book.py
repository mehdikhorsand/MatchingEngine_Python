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
        order.set_disclosed_quantity()
        order.is_in_queue = True
        order.broker_id.added_new_order(order)
        order.shareholder_id.added_new_order(order)
        if order.is_buy:
            self.buy_order_ids.append(order)
            self.sort_buy_orders()
        else:
            self.sell_order_ids.append(order)
            self.sort_sell_orders()

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

    def get_first_buy_order(self):
        valid_buy_orders = list(filter(lambda order: order.quantity > 0, self.buy_order_ids))
        return valid_buy_orders[0] if len(valid_buy_orders) > 0 else None

    def get_first_sell_order(self):
        valid_sell_orders = list(filter(lambda order: order.quantity > 0, self.sell_order_ids))
        return valid_sell_orders[0] if len(valid_sell_orders) > 0 else None

    def contains(self, order):
        return order in (self.buy_order_ids + self.sell_order_ids)

    def update_order_in_order_book(self, order, had_new_trade):
        def should_order_be_added_to_the_order_book():
            return not order.is_in_queue and order.filled_min_qty() and not had_new_trade and not order.fill_and_kill and \
                (not order.is_buy or order.broker_id.credit_validation(order))

        if order:
            if should_order_be_added_to_the_order_book():
                self.add_order(order)
                order.accepted()
            if order.disclosed_quantity <= 0 < order.peak_size:
                order.set_disclosed_quantity()
                if order.is_in_queue:
                    self.remove_order(order)
                    self.add_order(order)

    def remove_empty_orders(self):
        remove_list = list(filter(lambda x: x.quantity == 0, self.sell_order_ids + self.buy_order_ids))
        for order in remove_list:
            self.remove_order(order)

    def booked_orders_qty_with_same_shareholder_and_side(self, order):
        return sum([o.quantity for o in
                    list(filter(lambda x: x.shareholder_id.id == order.shareholder_id.id, self.buy_order_ids))])

    def booked_orders_value_with_same_broker_and_side(self, order):
        return sum([o.quantity * o.price for o in
                    list(filter(lambda x: x.broker_id.id == order.broker_id.id, self.buy_order_ids))])

    def rollback_order_book(self, trade):
        order = trade.sell_order_id if not trade.buy_order_id.is_in_queue else trade.buy_order_id
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
