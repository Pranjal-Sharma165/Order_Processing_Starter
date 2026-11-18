"""Business logic. Several design and correctness issues are intentional."""
from models import CartLine


class ShoppingCart:
    VALID_CODES = ['WELCOME10', 'STUDENT20', 'SAVE15', 'FREESHIP']
    SHIPPING_FEE = 5.0

    def __init__(self, user_id, repository):
        self.user_id = user_id
        self.repository = repository
        self.lines = []
        self.discount_code = None

    @staticmethod
    def _valid_quantity(quantity):
        # bool is a subclass of int in Python, so reject True/False explicitly
        return isinstance(quantity, int) and not isinstance(quantity, bool) and quantity > 0

    def add_item(self, sku, quantity):
        if not self._valid_quantity(quantity):
            print('Invalid quantity')
            return False
        product = self.repository.get_product(sku)
        if not product:
            print('Unknown product')
            return False
        existing = next((x for x in self.lines if x.sku == sku), None)
        already_in_cart = existing.quantity if existing else 0
        if product.stock < already_in_cart + quantity:
            print('Not enough stock')
            return False
        if existing:
            existing.quantity += quantity
        else:
            self.lines.append(CartLine(sku, product.name, product.price, quantity))
        return True

    def remove_item(self, sku, quantity=None):
        if quantity is not None and not self._valid_quantity(quantity):
            print('Invalid quantity')
            return False
        for line in self.lines:
            if line.sku == sku:
                if quantity is None or quantity >= line.quantity:
                    self.lines.remove(line)
                else:
                    line.quantity -= quantity
                return True
        print('Item not found')
        return False

    def subtotal(self):
        return round(sum(line.unit_price * line.quantity for line in self.lines), 2)

    def discount_amount(self):
        subtotal = self.subtotal()
        if self.discount_code == 'WELCOME10':
            return round(subtotal * 0.1, 2)
        elif self.discount_code == 'STUDENT20':
            return round(subtotal * 0.2, 2)
        elif self.discount_code == 'SAVE15':
            return min(subtotal, 15.0)
        return 0.0

    def total(self):
        return round(self.subtotal() - self.discount_amount() + self.shipping(), 2)

    def apply_discount(self, code):
        if code not in self.VALID_CODES:
            print('Invalid discount code')
            return False
        self.discount_code = code
        return True

    def load(self):
        self.lines.clear()
        skipped = []
        for sku, quantity in self.repository.get_saved_cart(self.user_id):
            if not self.add_item(sku, quantity):
                skipped.append(sku)
        return skipped

    def save(self):
        self.repository.save_cart(self.user_id, self.lines)

    def shipping(self):
        if not self.lines or self.discount_code == 'FREESHIP':
            return 0.0
        return self.SHIPPING_FEE