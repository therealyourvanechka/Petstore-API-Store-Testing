import pytest
import requests
from helpers import random_order_id, default_order_payload


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default="https://petstore.swagger.io/v2",
        help="Base URL for the Petstore API"
    )


@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url")


@pytest.fixture
def order_id(base_url):
    """
    Генерирует случайный id и гарантированно удаляет заказ после теста
    """
    oid = random_order_id() 
    yield oid
    requests.delete(f"{base_url}/store/order/{oid}")


@pytest.fixture
def created_order(base_url, order_id):
    """
    Создаёт готовый заказ перед тестом
    """
    payload = default_order_payload(order_id)  # используем хелпер
    requests.post(f"{base_url}/store/order", json=payload)
    yield payload
