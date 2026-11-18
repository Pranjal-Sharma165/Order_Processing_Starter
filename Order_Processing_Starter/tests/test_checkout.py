import pytest

from cart import ShoppingCart
from checkout import CheckoutService
from payments import FakePaymentGateway
from repository import StoreRepository
from setup_db import initialize


@pytest.fixture
def checkout_setup(tmp_path):
    db = tmp_path / 'test.db'
    initialize(str(db))

    repository = StoreRepository(str(db))
    cart = ShoppingCart('student', repository)
    gateway = FakePaymentGateway()

    service = CheckoutService(repository, gateway)

    return repository, cart, gateway, service

def test_successful_checkout(checkout_setup):
    repository, cart, gateway, service = checkout_setup

    cart.add_item('USB-01', 2)

    result = service.checkout(cart, 'test-token', 'request-001')

    assert result.status == 'paid'
    assert result.total == 24.98
    assert len(cart.lines) == 0
    assert repository.get_product('USB-01').stock == 48
    assert len(repository.list_orders('student')) == 1

def test_empty_cart_checkout(checkout_setup):
    repository, cart, gateway, service = checkout_setup

    result = service.checkout(cart, 'test-token', 'request-002')

    assert result.status == 'empty'
    assert result.order_id is None
    assert len(gateway.calls) == 0
    assert repository.list_orders('student') == []

def test_declined_payment(checkout_setup):
    repository, cart, gateway, service = checkout_setup

    gateway.should_approve = False
    cart.add_item('USB-01', 2)

    result = service.checkout(cart, 'test-token', 'request-003')

    assert result.status == 'declined'
    assert len(cart.lines) == 1
    assert cart.lines[0].quantity == 2
    assert repository.get_product('USB-01').stock == 50
    assert len(repository.list_orders('student')) == 1

def test_checkout_with_unavailable_stock(checkout_setup):
    repository, cart, gateway, service = checkout_setup

    cart.add_item('USB-01', 2)

    # Simulate another customer purchasing the remaining stock
    repository.update_stock('USB-01', 50)

    result = service.checkout(cart, 'test-token', 'request-004')

    assert result.status == 'out_of_stock'
    assert result.order_id is None
    assert len(cart.lines) == 1
    assert len(gateway.calls) == 0
    assert repository.list_orders('student') == []

def test_duplicate_checkout_request(checkout_setup):
    repository, cart, gateway, service = checkout_setup

    cart.add_item('USB-01', 2)

    first_result = service.checkout(
        cart, 'test-token', 'request-005'
    )

    second_result = service.checkout(
        cart, 'test-token', 'request-005'
    )

    assert first_result.status == 'paid'
    assert second_result.order_id == first_result.order_id
    assert second_result.status == 'paid'
    assert len(gateway.calls) == 1
    assert repository.get_product('USB-01').stock == 48
    assert len(repository.list_orders('student')) == 1

def test_payment_gateway_error(checkout_setup, monkeypatch):
    repository, cart, gateway, service = checkout_setup

    cart.add_item('USB-01', 2)

    def raise_error(amount, payment_token):
        raise RuntimeError("Payment service unavailable")

    monkeypatch.setattr(gateway, 'charge', raise_error)

    result = service.checkout(
        cart, 'test-token', 'request-006'
    )

    assert result.status == 'payment_error'
    assert len(cart.lines) == 1
    assert repository.get_product('USB-01').stock == 50
    assert len(repository.list_orders('student')) == 1
