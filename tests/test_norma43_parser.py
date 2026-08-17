"""Unit tests for the Spanish Norma 43 Bank Statement Parser."""

import pytest
from app.services.business.norma43_parser import Norma43Parser


@pytest.fixture
def sample_norma43_text():
    # 11: Header (Bank 0182, Branch 1234, Account 0123456789, Initial Balance +10000.00 EUR)
    # 22: Movement (+5000.00 EUR credit)
    # 23: Concept extension
    # 22: Movement (-1200.50 EUR debit)
    # 33: Summary
    # 88: End
    return (
        "11018212340123456789240501240531200000001000000EUR2\n"
        "221234240510240510010012000000005000000000000001  TRANSFERENCIA CLIENTE ACME    \n"
        "2301FACTURA 2024-088 PAGO COMPLETO                                              \n"
        "221234240515240515010021000000001200500000000002  PAGO SUMINISTRO ELECTRICO     \n"
        "3301821234012345678900001000000001200500000100000005000000200000001379950EUR\n"
        "8899999999999999999900000400000000000000                                       \n"
    )


def test_norma43_parser_basic(sample_norma43_text):
    parser = Norma43Parser()
    result = parser.parse(sample_norma43_text)

    assert result.bank_code == "0182"
    assert result.branch_code == "1234"
    assert result.account_number == "0123456789"
    assert result.initial_balance == 10000.00
    assert result.movements_count == 2

    # Movement 1: Credit +5000.00
    m1 = result.movements[0]
    assert m1.debit_or_credit == "C"
    assert m1.amount == 5000.00
    assert m1.operation_date == "2024-05-10"
    assert "TRANSFERENCIA CLIENTE ACME" in m1.extended_concept
    assert "FACTURA 2024-088" in m1.extended_concept

    # Movement 2: Debit -1200.50
    m2 = result.movements[1]
    assert m2.debit_or_credit == "D"
    assert m2.amount == 1200.50
    assert m2.operation_date == "2024-05-15"
