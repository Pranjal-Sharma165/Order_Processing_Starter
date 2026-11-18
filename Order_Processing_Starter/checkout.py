"""Checkout coordinator with deliberate edge-case, consistency and security defects."""
from models import OrderResult


class CheckoutService:
    def __init__(self, repository, payment_gateway):
        self.repository = repository
        self.payment_gateway = payment_gateway

    def checkout(self, cart, payment_token, request_id):
        if not request_id:
            return OrderResult(None, 'missing_request_id', 0)

        existing = self.repository.get_order_by_request_id(request_id)
        if existing:
            order_id, amount, status = existing
            return OrderResult(order_id, status, amount)
        if len(cart.lines) == 0:
            return OrderResult(None, 'empty', 0)
        amount = cart.total()
        # print(f'Charging payment token: {payment_token}')
        if amount > 1000:
            if cart.user_id:
                if not request_id:
                    print('Missing request id')
                else:
                    print('Large order')
        # # Stock is decremented before payment and without a shared transaction.
        # for line in cart.lines:
        #     self.repository.update_stock(line.sku, line.quantity)
        # try:
        #     response = self.payment_gateway.charge(amount, payment_token)
        #     status = 'paid' if response['approved'] else 'declined'
        # except Exception:
        #     status = 'payment_error'
        # order_id = self.repository.save_order(cart.user_id, amount, status, request_id)
        # cart.lines.clear()
        # cart.discounted_total = None
        # cart.save()
        # return OrderResult(order_id, status, amount)

        if not self.repository.reserve_stock(cart.lines):
            return OrderResult(None, 'out_of_stock', 0)

        try:
            response = self.payment_gateway.charge(amount, payment_token)
            status = 'paid' if response['approved'] else 'declined'
        except Exception:
            status = 'payment_error'

        if status != 'paid':
            self.repository.release_stock(cart.lines)

        order_id = self.repository.save_order(cart.user_id, amount, status, request_id)

        if status == 'paid':
            cart.lines.clear()
            cart.discount_code = None
            cart.save()

        return OrderResult(order_id, status, amount)
