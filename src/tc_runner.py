import os
from src.broker import Broker
from src.environment import Environment
from src.matching_engine import MatchingEngine
from src.order import Order
from src.shareholder import Shareholder


def print_output(output, clear_previous_content=False):
    os.system(
        "echo \"%s\" %s> %s" % (output, "" if clear_previous_content else ">", TCRunner.destination_file_path)
    )


def get_boolean(string):
    return True if string == "True" else False if string == "False" else "xxxx"


def get_order(order_attributes):
    order = Order(
        broker_id=int(order_attributes[0]), shareholder_id=int(order_attributes[1]), price=int(order_attributes[2]),
        quantity=int(order_attributes[3]), is_buy=get_boolean(order_attributes[4]), min_qty=int(order_attributes[5]),
        fill_and_kill=get_boolean(order_attributes[6]), peak_size=int(order_attributes[7]))
    return order


class TCRunner:
    destination_file_path = None

    def __init__(self, input_file_path, output_file_path):
        TCRunner.destination_file_path = output_file_path
        self.environment = Environment()
        self.matching_engine = MatchingEngine(self.environment)
        with open(input_file_path) as txt_file:
            lines = txt_file.read().strip().splitlines()
            self.environment.__init__()
            self.matching_engine.__init__(self.environment)
            print_output(len(lines), True)
            for line in lines:
                self.execute_line(line)

    def execute_line(self, line):
        rq_args = line.replace("\t", " ").split(" ")
        request = rq_args[0]
        args = list(filter(lambda x: x != '', rq_args[1:]))
        match request:
            case "SetTickSizeRq":
                self.environment.set_tick_size_rq(int(args[0]))
            case "SetLotSizeRq":
                self.environment.set_lot_size_rq(int(args[0]))
            case "SetReferencePriceRq":
                self.environment.set_reference_price_request(int(args[0]))
            case "SetStaticPriceBandLowerLimitRq":
                self.environment.set_static_price_band_lower_limit_rq(float(args[0]))
            case "SetStaticPriceBandUpperLimitRq":
                self.environment.set_static_price_band_upper_limit_rq(float(args[0]))
            case "SetTotalSharesRq":
                self.environment.set_total_shares_rq(int(args[0]))
            case "SetOwnershipUpperLimitRq":
                self.environment.set_ownership_upper_limit_rq(float(args[0]))
            case "SetCreditRq":
                Broker(int(args[0]), int(args[1]))
            case "SetOwnershipRq":
                Shareholder(int(args[0]), int(args[1]))
            case "NewOrderRq":
                self.new_order_rq(args)
            case "ReplaceOrderRq":
                self.replace_order_rq(args)
            case "CancelOrderRq":
                self.cancel_order_rq(args)

    def print_matching_engine_state(self):
        print_output(self.matching_engine)

    def new_order_rq(self, args):
        new_order = get_order(args)
        self.matching_engine.new_order_request(new_order)
        self.print_matching_engine_state()

    def replace_order_rq(self, args):
        replace_order = get_order(args[1:])
        self.matching_engine.replace_order_request(int(args[0]), replace_order)
        self.print_matching_engine_state()

    def cancel_order_rq(self, args):
        next(Order.counter)
        self.matching_engine.cancel_order_request(int(args[0]), get_boolean(args[1]))
        self.print_matching_engine_state()
