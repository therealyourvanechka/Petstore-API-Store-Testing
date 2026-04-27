import pytest
import requests


# GET /store/inventory (получение количества питомцев по статусам)

@pytest.mark.smoke
def test_status_code_200(base_url):
    """
    Positive: базовый smoke-тест что API живой
    """
    response = requests.get(f"{base_url}/store/inventory")
    assert response.status_code == 200

@pytest.mark.xfail(reason="Принимаются невалидные статусы питомцев")
def test_inventory_contains_only_valid_statuses(base_url):
    """
    Positive: должен содержать только валидные статусы
    """
    response = requests.get(f"{base_url}/store/inventory")
    data = response.json()
    valid = {"available", "pending", "sold"}
    invalid_keys = set(data.keys()) - valid
    assert len(invalid_keys) == 0, f"Невалидные статусы: {invalid_keys}"

def test_values_are_integers(base_url):
    """
    Positive: значения в словаре целые числа (количество питомцев)
    """
    response = requests.get(f"{base_url}/store/inventory")
    data = response.json()
    for key, value in data.items():
        assert isinstance(value, int), \
            f"Значение для статуса '{key}' не является integer: {value}"
