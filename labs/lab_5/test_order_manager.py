import pytest
from order_manager import Order

def test_total_various_sets():      #чи правильний підрахунок загальної суми замовлення
    items = [{"price": 10, "quantity": 2}, {"price": 5, "quantity": 3}]
    assert Order(1, items).total() == 10*2 + 5*3

    assert Order(2, []).total() == 0


def test_most_expensive():            #чи метод знаходить найдорожчий товар
    items = [{"price": 10}, {"price": 50}, {"price": 30}]
    assert Order(4, items).most_expensive()["price"] == 50

    assert Order(5, [{"price": 99}]).most_expensive()["price"] == 99

    with pytest.raises(ValueError):
        Order(6, []).most_expensive()


def test_apply_discount_valid_for_all():     #перевіряє чи правильно знижує ціни на 10%
    items = [
        {"price": 100, "quantity": 1},
        {"price": 200, "quantity": 2},
        {"price": 300, "quantity": 3},
    ]
    order = Order(7, items)
    order.apply_discount(10)
    for item in items:
        assert item["price"] == pytest.approx(item["price"] / 0.9 * 0.9)  


@pytest.mark.parametrize("discount", [-10, 101, 999])
def test_apply_discount_invalid(discount):      #перевіряє, що невірні знижки
    items = [{"price": 50, "quantity": 1}]
    order = Order(8, items)
    with pytest.raises(ValueError, match="Invalid discount"):
        order.apply_discount(discount)


def test_apply_discount_extreme():      # чи норм працює при 0% та 100%
    items = [{"price": 100, "quantity": 1}, {"price": 50, "quantity": 2}]
    order = Order(9, items)

    order.apply_discount(0)
    assert all(item["price"] in (100, 50) for item in items)

    order.apply_discount(100)
    assert all(item["price"] == 0 for item in items)


def test_repr():            #чи повертає коректний текстовий опис 
    items = [{"price": 1, "quantity": 1}]
    order = Order(10, items)
    r = repr(order)
    assert f"<Order {order.id}" in r
    assert f"{len(items)} items" in r




