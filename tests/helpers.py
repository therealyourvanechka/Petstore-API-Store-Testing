import random


def random_order_id():
    """Генерирует случайный id заказа"""
    return random.randint(10000, 99999)


def default_order_payload(order_id, **kwargs):
    """
    Базовый payload для создания заказа.
    """
    payload = {
        "id": order_id,
        "petId": 1,
        "quantity": 1,
        "status": "placed",
        "complete": True
    }
    # перезаписываем дефолтные значения переданными
    payload.update(kwargs)
    return payload