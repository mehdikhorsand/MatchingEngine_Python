from src import tc_runner


class Broker:

    list = []

    def __init__(self, broker_id, credit):
        tc_runner.print_output("SetCreditRs\tAccepted")
        self.id = broker_id
        self.credit = credit
        self.free_credit = credit
        Broker.list.append(self)

    def __repr__(self):
        return "\tCredit\t%s\t%s" % (self.id, self.credit)

    def increase_credit(self, trade):
        # sell order -> trade : increase credit of sell orders broker
        self.free_credit += trade.value
        self.credit += trade.value

    def decrease_credit(self, trade):
        # buy order -> trade : decrease credit of buy orders broker
        self.credit -= trade.value
        if not trade.buy_order_id.is_in_queue:
            self.free_credit -= trade.value

    def credit_validation(self, order):
        # just before adding to the queue
        return not order.is_buy or self.free_credit >= order.value()

    def added_new_order(self, order):
        if order.is_buy:
            self.free_credit -= order.value()

    def deleted_old_order(self, order):
        if order.is_buy:
            self.free_credit += order.value()

    def rollback_increase_credit(self, trade):
        self.free_credit -= trade.value
        self.credit -= trade.value

    def rollback_decrease_credit(self, trade):
        self.credit += trade.value
        if not trade.buy_order_id.is_in_queue:
            self.free_credit += trade.value


def get_broker_by_id(broker_id):
    return [x for x in Broker.list if x.id == broker_id][0]


def print_credits():
    result = "\n\tCredits\t%s" % len(Broker.list)
    for credit in Broker.list:
        result += "\n" + credit.__repr__()
    return result
