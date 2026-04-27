import pytest
import requests


# GET /store/order/{orderId} (получение заказа по ID)

@pytest.mark.smoke
@pytest.mark.critical_path
def test_get_existing_order(base_url, created_order):
    """
    Positive: получение существующего заказа возвращает 200
    """
    response = requests.get(f"{base_url}/store/order/{created_order['id']}")
    assert response.status_code == 200

@pytest.mark.critical_path
def test_get_order_correct_data(base_url, created_order):
    """
    Positive: ответ содержит именно те данные которые были переданы при создании
    """
    response = requests.get(f"{base_url}/store/order/{created_order["id"]}")
    data = response.json()

    assert data["id"] == created_order["id"]
    assert data["petId"] == created_order["petId"]
    assert data["quantity"] == created_order["quantity"]
    assert data["status"] == created_order["status"]
    assert data["complete"] == created_order["complete"]

def test_get_order_not_found(base_url):
    """
    Negative: несуществующий orderId 
    """
    response = requests.get(f"{base_url}/store/order/999999999")
    assert response.status_code == 404

@pytest.mark.xfail(reason="Возвращает 404 вместо 400 на невалидный orderId не соответствует спецификации")
def test_get_order_string_id(base_url):
    """
    Negative: строка вместо числового orderId
    """
    response = requests.get(f"{base_url}/store/order/abc")
    assert response.status_code == 400

@pytest.mark.xfail(reason="Возвращает 404 вместо 400 на отрицательный orderId не соответствует спецификации")
def test_get_order_negative_id(base_url):
    """
    Edge: отрицательный orderId
    """
    response = requests.get(f"{base_url}/store/order/-1")
    assert response.status_code == 400
