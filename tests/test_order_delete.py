import pytest
import requests
from helpers import default_order_payload, random_order_id


# DELETE /store/order/{orderId} (удаление заказа)

@pytest.mark.smoke
@pytest.mark.critical_path
def test_delete_existing_order(base_url):
    """
    Positive: удаление существующего заказа возвращает 200
    """
    oid = random_order_id()
    requests.post(f"{base_url}/store/order", json=default_order_payload(oid))
    response = requests.delete(f"{base_url}/store/order/{oid}")
    assert response.status_code == 200

@pytest.mark.critical_path
def test_delete_then_get_returns_404(base_url):
    """
    Positive: после удаления GET на тот же заказ возвращает 404
    """
    oid = random_order_id()
    requests.post(f"{base_url}/store/order", json=default_order_payload(oid))
    requests.delete(f"{base_url}/store/order/{oid}")

    response = requests.get(f"{base_url}/store/order/{oid}")
    assert response.status_code == 404

def test_delete_twice(base_url):
    """
    Negative: повторное удаление уже удалённого заказа возвращает 404, заказа не существует
    """
    oid = random_order_id()
    requests.post(f"{base_url}/store/order", json=default_order_payload(oid))
    requests.delete(f"{base_url}/store/order/{oid}")

    response = requests.delete(f"{base_url}/store/order/{oid}")
    assert response.status_code == 404

@pytest.mark.xfail(reason="Возвращает 404 вместо 400 на невалидный orderId не соответствует спецификации")
def test_delete_string_id(base_url):
    """
    Negative: строка вместо orderId
    """
    response = requests.delete(f"{base_url}/store/order/abc")
    assert response.status_code == 400