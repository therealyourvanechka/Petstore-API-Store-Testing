import pytest
import requests
from helpers import default_order_payload, random_order_id


"""
POST /store/order (создание заказа на питомца)
Согласно доке у метода нет обязательных полей
по факту минимум petId должен быть обязательным:
заказ без привязки к питомцу лишён смысла
"""

@pytest.mark.smoke
@pytest.mark.critical_path
def test_create_order_success(base_url, order_id):
    """
    Positive: создание заказа с валидными данными возвращает 200
    """
    payload = default_order_payload(order_id)
    response = requests.post(f"{base_url}/store/order", json=payload)
    assert response.status_code == 200

@pytest.mark.critical_path
def test_create_order_data_persisted(base_url, order_id):
    """
    Positive: данные созданного заказа реально сохраняются в системе
    """
    payload = default_order_payload(order_id, petId=5, quantity=2)
    requests.post(f"{base_url}/store/order", json=payload)

    # проверяем через GET что данные сохранились
    response = requests.get(f"{base_url}/store/order/{order_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == order_id
    assert data["petId"] == 5
    assert data["quantity"] == 2
    assert data["status"] == "placed"
    assert data["complete"] == True


def test_create_order_returns_correct_fields(base_url, order_id):
    """
    Positive: тело ответа содержит именно те данные которые мы передали
    """
    payload = default_order_payload(order_id, petId=42, quantity=3, complete=False)
    response = requests.post(f"{base_url}/store/order", json=payload)
    data = response.json()

    assert data["id"] == order_id
    assert data["petId"] == 42
    assert data["quantity"] == 3
    assert data["status"] == "placed"
    assert data["complete"] == False

@pytest.mark.parametrize("status", ["placed", "approved", "delivered"])
def test_create_order_valid_statuses(base_url, order_id, status):
    """
    Positive: проверяем все три валидных статуса заказа
    """
    payload = default_order_payload(order_id, status=status)
    response = requests.post(f"{base_url}/store/order", json=payload)
    assert response.status_code == 200
    assert response.json().get("status") == status, \
        f"Ожидался статус {status}, но получен {response.json().get("status")}"

@pytest.mark.parametrize("status", ["zombie", "$%#", "123", ""])
@pytest.mark.xfail(reason="Принимает невалидный статус и возвращает 200 вместо 400")
def test_create_order_invalid_status(base_url, order_id, status):
    """
    Negative: невалидный статус
    """
    payload = default_order_payload(order_id, status=status)
    response = requests.post(f"{base_url}/store/order", json=payload)
    assert response.status_code == 400, \
        f"Создался заказ с невалидным статусом {response.json().get("status")}, вернулся {response.status_code} вместо 400"

@pytest.mark.xfail(reason="Принимает пустое тело и возвращает 200, создаёт запись с дефолтными значениями")
def test_create_order_empty_body(base_url):
    """
    Negative: пустое тело 
    """
    response = requests.post(f"{base_url}/store/order", json={})
    assert response.status_code == 400, \
        f"Пустое тело вернуло {response.status_code}, создана запись: {response.json()}"

@pytest.mark.xfail(reason="Принимает дублирующийся id при заказе")
def test_create_order_duplicate_id(base_url, order_id):
    """
    Negative: два заказа с одинаковым id
    """
    requests.post(f"{base_url}/store/order", json=default_order_payload(order_id))

    # второй с тем же id но другим petId
    response = requests.post(f"{base_url}/store/order", json=default_order_payload(order_id, petId=999))

    assert response.status_code == 400, \
        f"При заказе с дублирующимся id вернулся статус-код {response.status_code} вместо 400"

@pytest.mark.xfail(reason="Данные перезаписываются при дублирующемся id")
def test_duplicate_id_overwrites_data(base_url, order_id):
    requests.post(f"{base_url}/store/order", json=default_order_payload(order_id, petId=1))

    requests.post(f"{base_url}/store/order", json=default_order_payload(order_id, petId=999))

    response = requests.get(f"{base_url}/store/order/{order_id}")
    data = response.json()

    assert data["petId"] == 1, \
        f"Данные были перезаписаны, petId стал {data['petId']} вместо 1"

@pytest.mark.xfail(reason="Повторный заказ на того же питомца принимается без ошибки")
def test_create_order_duplicate_pet_id(base_url, order_id):
    """
    Negative: нельзя создать новый заказ на питомца который уже доставлен
    """
    second_id = random_order_id()

    # первый заказ и он доставлен
    requests.post(f"{base_url}/store/order", json=default_order_payload(order_id, status = "delivered"))

    # второй заказ на того же питомца
    response = requests.post(f"{base_url}/store/order", json=default_order_payload(second_id))

    requests.delete(f"{base_url}/store/order/{second_id}")

    assert response.status_code == 400, \
        f"Повторный заказ на petId = 1 вернул {response.status_code} вместо 400"

@pytest.mark.xfail(reason="Запросы без id получают одинаковый дефолтный id и перезаписывают друг друга")
def test_create_order_without_id_generates_unique_id(base_url):
    """
    Edge: два запроса без id должны создавать два разных заказа
    """
    payload_1 = {"petId": random_order_id(), "quantity": 1, "status": "placed", "complete": True}
    payload_2 = {"petId": random_order_id(), "quantity": 1, "status": "placed", "complete": True}

    response_1 = requests.post(f"{base_url}/store/order", json=payload_1)
    id_1 = response_1.json().get("id")
    print(f"\nПервый запрос: id={id_1}, petId={payload_1['petId']}")

    response_2 = requests.post(f"{base_url}/store/order", json=payload_2)
    id_2 = response_2.json().get("id")
    print(f"Второй запрос: id={id_2}, petId={payload_2['petId']}")

    assert id_1 != id_2, \
        f"Оба запроса без id получили одинаковый id={id_1}"