from src import tc_runner


class Environment:

    def __init__(self):
        self.ownership_upper_limit = None
        self.total_shares = None
        self.static_price_band_upper_limit = None
        self.static_price_band_lower_limit = None
        self.reference_price = None
        self.lot_size = None
        self.tick_size = None

    def __repr__(self):
        return "\tReferencePrice\t%s\n" \
               "\tStaticPriceBandLowerLimit\t%s\n" \
               "\tStaticPriceBandUpperLimit\t%s\n" \
               "\tTotalShares\t%s\n" \
               "\tOwnershipUpperLimit\t%s\n" \
               "\tTickSize\t%s\n" \
               "\tLotSize\t%s" % (
                self.reference_price,
                self.static_price_band_lower_limit,
                self.static_price_band_upper_limit,
                self.total_shares,
                self.ownership_upper_limit,
                self.tick_size,
                self.lot_size
                )

    def set_tick_size_rq(self, tick_size):
        tc_runner.print_output("SetTickSizeRs\tAccepted")
        self.tick_size = tick_size

    def set_lot_size_rq(self, lot_size):
        tc_runner.print_output("SetLotSizeRs\tAccepted")
        self.lot_size = lot_size

    def set_reference_price_request(self, reference_price):
        tc_runner.print_output("SetReferencePriceRs\tAccepted")
        self.reference_price = reference_price

    def set_static_price_band_lower_limit_rq(self, static_price_band_lower_limit):
        tc_runner.print_output("SetStaticPriceBandLowerLimitRs\tAccepted")
        self.static_price_band_lower_limit = static_price_band_lower_limit

    def set_static_price_band_upper_limit_rq(self, static_price_band_upper_limit):
        tc_runner.print_output("SetStaticPriceBandUpperLimitRs\tAccepted")
        self.static_price_band_upper_limit = static_price_band_upper_limit

    def set_total_shares_rq(self, total_shares):
        tc_runner.print_output("SetTotalSharesRs\tAccepted")
        self.total_shares = total_shares

    def set_ownership_upper_limit_rq(self, ownership_upper_limit):
        tc_runner.print_output("SetOwnershipUpperLimitRs\tAccepted")
        self.ownership_upper_limit = ownership_upper_limit

    def validate_order_price_limit(self, order):
        lower_price_limit = self.reference_price - int(self.reference_price * self.static_price_band_lower_limit)
        upper_price_limit = self.reference_price + int(self.reference_price * self.static_price_band_upper_limit)
        return lower_price_limit <= order.price <= upper_price_limit

    def validate_order_quantity_limit(self, order):
        if order.is_buy:
            owned_qty = order.shareholder_id.ownership
            booked_orders_qty = order.shareholder_id.booked_buy_orders_qty
            max_ownership = int(self.total_shares * self.ownership_upper_limit)
            return owned_qty + order.quantity + booked_orders_qty < max_ownership
        else:
            return True
