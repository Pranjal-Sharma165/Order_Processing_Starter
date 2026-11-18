import pytest

from cart import ShoppingCart
from repository import StoreRepository
from setup_db import initialize


@pytest.fixture
def cart(tmp_path):
    db = tmp_path / 'test.db'
    initialize(str(db))
    repository = StoreRepository(str(db))
    return ShoppingCart('student', repository)

@pytest.mark.parametrize('quantity', [0, -1, 1.5, True, False, '2'])
def test_add_invalid_quantity(cart, quantity):
    assert cart.add_item('USB-01', quantity) is False
    assert len(cart.lines) == 0

def test_add_unknown_product(cart):
    assert cart.add_item('UNKNOWN', 1) is False
    assert len(cart.lines) == 0

def test_add_duplicate_product(cart):
    cart.add_item('USB-01', 2)
    cart.add_item('USB-01', 3)

    assert len(cart.lines) == 1
    assert cart.lines[0].quantity == 5

def test_add_more_than_available_stock(cart):
    assert cart.add_item('LAP-01', 6) is False
    assert len(cart.lines) == 0

def test_remove_partial_quantity(cart):
    cart.add_item('USB-01', 5)

    assert cart.remove_item('USB-01', 2) is True
    assert cart.lines[0].quantity == 3

def test_remove_entire_item(cart):
    cart.add_item('USB-01', 3)

    assert cart.remove_item('USB-01') is True
    assert len(cart.lines) == 0

@pytest.mark.parametrize('quantity', [0, -1, 1.5, True, '2'])
def test_remove_invalid_quantity(cart, quantity):
    cart.add_item('USB-01', 5)

    assert cart.remove_item('USB-01', quantity) is False
    assert cart.lines[0].quantity == 5

def test_remove_more_than_cart_quantity(cart):
    cart.add_item('USB-01', 2)

    assert cart.remove_item('USB-01', 5) is True
    assert len(cart.lines) == 0

def test_subtotal(cart):
    cart.add_item('MOU-01', 2)
    cart.add_item('USB-01', 3)

    assert cart.subtotal() == 89.87

def test_welcome_discount(cart):
    cart.add_item('MOU-01', 2)
    cart.apply_discount('WELCOME10')

    assert cart.discount_amount() == 5.99

def test_save15_discount(cart):
    cart.add_item('MOU-01', 1)
    cart.apply_discount('SAVE15')

    assert cart.discount_amount() == 15.0

def test_discount_updates_after_adding_item(cart):
    cart.add_item('MOU-01', 1)
    cart.apply_discount('WELCOME10')

    cart.add_item('USB-01', 1)

    assert cart.subtotal() == 39.94
    assert cart.discount_amount() == 3.99

def test_free_shipping(cart):
    cart.add_item('USB-01', 1)
    cart.apply_discount('FREESHIP')

    assert cart.shipping() == 0.0

def test_invalid_discount_code(cart):
    result = cart.apply_discount('INVALID')

    assert result is False
    assert cart.discount_code is None

def test_empty_cart_totals(cart):
    assert cart.subtotal() == 0.0
    assert cart.discount_amount() == 0.0
    assert cart.shipping() == 0.0
    assert cart.total() == 0.0

def test_total_with_discount_and_shipping(cart):
    cart.add_item('MOU-01', 2)
    cart.apply_discount('WELCOME10')

    assert cart.total() == 58.91