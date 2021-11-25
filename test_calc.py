from datetime import date

import pytest

from . import calc


def test_get_bills_by_day():
    b1 = calc.Bill(1, 100, "bill 1")
    b2 = calc.Bill(1, 200, "bill 2")
    b3 = calc.Bill(2, 400, "bill 3")
    assert calc.get_bills_by_day([b1, b2, b3]) == {
        1: [b1, b2],
        2: [b3],
    }, "bills weren't ordered into daily lists"

    assert calc.get_bills_by_day([]) == {}, "didn't get expected value for empty bills"


def test_pay_period():
    pp = calc.PayPeriod(date(2021, 11, 12), 14)
    assert pp.start == date(2021, 11, 12)
    assert pp.end == date(2021, 11, 26)
    assert pp.length_in_days == 14
    assert pp.is_cross_month == False
    assert pp.last_day_of_start_month == 30

    # check the case when it crosses months
    pp = calc.PayPeriod(date(2021, 11, 26), 14)
    assert pp.is_cross_month == True

    # now crossing multiple months; not supported, but let's check its behavior
    pp = calc.PayPeriod(date(2021, 11, 26), 45)
    assert pp.is_cross_month == True
    assert pp.last_day_of_start_month == 30


def test_get_bills_in_pay_period():
    b1 = calc.Bill(1, 100, "bill 1")
    b2 = calc.Bill(1, 200, "bill 2")
    b3 = calc.Bill(12, 400, "bill 3")
    b4 = calc.Bill(25, 800, "bill 4")
    b5 = calc.Bill(26, 1600, "bill 5")
    b6 = calc.Bill(31, 3200, "bill 6")
    bills_by_day = {
        1: [b1, b2],
        12: [b3],
        25: [b4],
        26: [b5],
        31: [b6],
    }
    pp_mid_month = calc.PayPeriod(date(2021, 11, 12), 14)
    pp_cross_month = calc.PayPeriod(date(2021, 11, 26), 14)

    assert calc.get_bills_in_pay_period(bills_by_day, pp_mid_month) == [
        b3,
        b4,
    ], "bill collection failed even in the middle of the month"
    assert calc.get_bills_in_pay_period(bills_by_day, pp_cross_month) == [
        b5,
        b6,
        b1,
        b2,
    ], "bill collection across months failed"
