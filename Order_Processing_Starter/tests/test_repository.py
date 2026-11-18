import pytest

from repository import StoreRepository
from setup_db import initialize
from models import CartLine


@pytest.fixture
def repository(tmp_path):
    db = tmp_path / 'test.db'
    initialize(str(db))
    return StoreRepository(str(db))

def test_get_existing_product(repository):
    product = repository.get_product('MOU-01')

    assert product is not None
    assert product.name == 'Wireless mouse'
    assert product.price == 29.95
    assert product.stock == 20

def test_get_unknown_product(repository):
    product = repository.get_product('UNKNOWN')

    assert product is None

def test_save_and_get_cart(repository):
    lines = [
        CartLine('MOU-01', 'Wireless mouse', 29.95, 2),
        CartLine('USB-01', 'USB cable', 9.99, 3)
    ]

    repository.save_cart('student', lines)

    saved_cart = repository.get_saved_cart('student')

    assert len(saved_cart) == 2
    assert ('MOU-01', 2) in saved_cart
    assert ('USB-01', 3) in saved_cart

def test_save_empty_cart(repository):
    lines = [
        CartLine('USB-01', 'USB cable', 9.99, 2)
    ]

    repository.save_cart('student', lines)
    repository.save_cart('student', [])

    assert repository.get_saved_cart('student') == []

def test_update_stock(repository):
    repository.update_stock('MOU-01', 2)

    product = repository.get_product('MOU-01')

    assert product.stock == 18

def test_save_and_get_order(repository):
    order_id = repository.save_order(
        'student', 59.90, 'paid', 'request-001'
    )

    order = repository.get_order_by_request_id('request-001')

    assert order is not None
    assert order[0] == order_id
    assert order[1] == 59.90
    assert order[2] == 'paid'

def test_reserve_stock(repository):
    lines = [
        CartLine('MOU-01', 'Wireless mouse', 29.95, 3)
    ]

    result = repository.reserve_stock(lines)

    assert result is True
    assert repository.get_product('MOU-01').stock == 17

def test_reserve_insufficient_stock(repository):
    lines = [
        CartLine('LAP-01', 'Laptop', 999.99, 6)
    ]

    result = repository.reserve_stock(lines)

    assert result is False
    assert repository.get_product('LAP-01').stock == 5

def test_release_stock(repository):
    lines = [
        CartLine('MOU-01', 'Wireless mouse', 29.95, 3)
    ]

    repository.reserve_stock(lines)
    repository.release_stock(lines)

    assert repository.get_product('MOU-01').stock == 20
    