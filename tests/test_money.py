from decimal import Decimal

import pytest

from app.services.money import parse_money_to_paisa


def test_decimal_supplier_price_to_integer_paisa():
    assert parse_money_to_paisa("84250.50") == 8425050
    assert parse_money_to_paisa("100") == 10000
    assert parse_money_to_paisa("100.00") == 10000
    assert parse_money_to_paisa("100.50") == 10050
    assert parse_money_to_paisa("0.01") == 1


def test_invalid_price_rejected():
    for value in ["", "abc", "1.2.3", "-1", "NaN", "Infinity", "1e2"]:
        with pytest.raises(ValueError):
            parse_money_to_paisa(value)


def test_number_like_values_are_not_float_based():
    value = parse_money_to_paisa("123.45")
    assert value == 12345
    assert isinstance(value, int)
