from src import tc_runner


class Shareholder:

    list = []

    def __init__(self, shareholder_id, ownership):
        tc_runner.print_output("SetOwnershipRs\tAccepted")
        self.id = shareholder_id
        self.ownership = ownership
        self.free_ownership = ownership
        self.booked_buy_orders_qty = 0
        Shareholder.list.append(self)

    def increase_ownership(self, trade):
        self.ownership += trade.quantity
        self.free_ownership += trade.quantity
        if trade.buy_order_id.is_in_queue:
            self.booked_buy_orders_qty -= trade.quantity

    def decrease_ownership(self, trade):
        self.ownership -= trade.quantity
        if not trade.sell_order_id.is_in_queue:
            self.free_ownership -= trade.quantity

    def ownership_validation(self, order):
        # just before calling match function
        return order.is_buy or self.free_ownership >= order.quantity

    def added_new_order(self, order):
        if order.is_buy:
            self.booked_buy_orders_qty += order.quantity
        else:
            self.free_ownership -= order.quantity

    def deleted_old_order(self, order):
        if order.is_buy:
            self.booked_buy_orders_qty -= order.quantity
        else:
            self.free_ownership += order.quantity

    def rollback_increase_ownership(self, trade):
        self.ownership -= trade.quantity
        self.free_ownership -= trade.quantity
        if trade.buy_order_id.is_in_queue:
            self.booked_buy_orders_qty += trade.quantity

    def rollback_decrease_ownership(self, trade):
        self.ownership += trade.quantity
        if not trade.sell_order_id.is_in_queue:
            self.free_ownership += trade.quantity

    def __repr__(self):
        return "\tOwnership\t%s\t%s" % (self.id, self.ownership)


def get_shareholder_by_id(shareholder_id):
    return [x for x in Shareholder.list if x.id == shareholder_id][0]


def print_ownerships():
    result = "\n\tOwnerships\t%s" % len(Shareholder.list)
    for ownership in Shareholder.list:
        result += "\n" + ownership.__repr__()
    return result
