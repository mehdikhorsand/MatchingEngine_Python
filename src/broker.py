from src import tc_runner


class Broker:

    list = []

    def __init__(self, broker_id, credit):
        tc_runner.print_output("SetCreditRs\tAccepted")
        self.id = broker_id
        self.credit = credit
        self.free_credit = credit
        self.total_buy_orders_quantity = 0
        Broker.list.append(self)

    def __repr__(self):
        return "\tCredit\t%s\t%s" % (self.id, self.credit)

    def increase_credit(self, trade):
        # sell order -> trade : increase credit of sell orders broker
        self.free_credit += trade.value
        self.credit += trade.value
        self.report_broker("increase_credit", trade)

    def decrease_credit(self, trade):
        # buy order -> trade : decrease credit of buy orders broker
        self.credit -= trade.value
        if not trade.buy_order_id.is_in_queue:
            self.free_credit -= trade.value
        self.report_broker("decrease_credit", trade)

    def credit_validation(self, order):
        # just before adding to the queue
        return not order.is_buy or self.free_credit >= order.quantity * order.price

    def added_new_order(self, order):
        if order.is_buy:
            order_value = order.quantity * order.price
            self.free_credit -= order_value

    def rollback_increase_credit(self, trade):
        self.free_credit -= trade.value
        self.credit -= trade.value
        self.report_broker("rollback_increase_credit", trade)

    def rollback_decrease_credit(self, trade):
        self.credit += trade.value
        if not trade.buy_order_id.is_in_queue:
            self.free_credit += trade.value
        self.report_broker("rollback_decrease_credit", trade)

    def report_broker(self, function_name, function_input):
        # if self.id == 6:
        #     print("broker_id: %s\n%s:" % (self.id, function_name), function_input)
        #     print("\t credit:", self.credit)
        #     print("\t free_credit:", self.free_credit)
        # self.assert_credit()
        pass


def get_broker_by_id(broker_id):
    return [x for x in Broker.list if x.id == broker_id][0]


def print_credits():
    result = "\n\tCredits\t%s" % len(Broker.list)
    for credit in Broker.list:
        result += "\n" + credit.__repr__()
    return result
