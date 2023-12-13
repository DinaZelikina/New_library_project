import pytest
from customer import Customer

def test_customer_init():
    customer_id = "99"
    name = "John Smith"
    city = "Haifa"
    birth_date = "01.01.1990"

    customer = Customer(
        customer_id=customer_id,
        name=name,
        city=city,
        birth_date=birth_date
    )

    assert customer.customer_id == customer_id
    assert customer.name == name
    assert customer.city == city
    assert customer.birth_date == birth_date
    assert customer.loaned_books == []
    assert customer.late_loans == []
    assert customer.is_removed == False