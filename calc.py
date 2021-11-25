import calendar
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
import json
import sys
from typing import Dict, List, Tuple


@dataclass
class Bill:
    day_of_month: int
    amount: int
    name: str

    def __str__(self):
        return f"{self.name}: {self.amount} on {self.day_of_month}"


def load_bills_from_file(filename: str) -> Dict[str, List]:
    """
    Use a JSON file to load the user's bills, with each key being the frequency
    and the key being a list of bills.
    """
    try:
        with open("bills.json") as f:
            bills_raw = json.load(f)
    except KeyError:
        print(f"You must add your bills to {filename} before using this.")
        sys.exit(2)
    else:
        return [Bill(*b) for b in bills_raw["monthly"]]


def get_bills_by_day(bills: List[Bill]) -> Dict[int, Bill]:
    """
    Turn monthly bills into a map of day -> list of bills.

    This approach may become too heavyweight if we ever support non-monthly bills. At
    the very least, it'll have to be called later, with pay period info.
    """
    bills_by_day = defaultdict(lambda: [])
    for b in bills:
        bills_by_day[b.day_of_month].append(b)
    return bills_by_day


class PayPeriod:
    start: date
    end: date
    length_in_days: int
    is_cross_month: bool
    last_day_of_start_month: int

    def __init__(self, start: date, length_in_days: int) -> None:
        self.start = start
        self.end = start + timedelta(days=length_in_days)
        self.length_in_days = length_in_days
        self.is_cross_month = start.month != self.end.month
        self.last_day_of_start_month = calendar.monthrange(
            self.start.year, self.start.month
        )[1]


def get_bills_in_pay_period(
    bills_by_day: Dict[int, List[Bill]], pp: PayPeriod
) -> List[Bill]:
    """
    Collect bills that fall within this pay period, from the start (inclusive) to end date (exclusive).
    """
    current_date = None
    relevant_bills = []
    for i in range(0, pp.length_in_days):
        # add today's bills
        current_date = pp.start + timedelta(days=i)
        relevant_bills.extend(bills_by_day.get(current_date.day, []))

        # don't miss bills on days 29-31
        if pp.is_cross_month and current_date.day == pp.last_day_of_start_month:
            nonexistent_day = current_date.day
            while nonexistent_day < 31:
                nonexistent_day += 1
                relevant_bills.extend(bills_by_day.get(nonexistent_day, []))
    return relevant_bills


def main():
    bills = load_bills_from_file("bills.json")
    bills_by_day = get_bills_by_day(bills)
    pp = PayPeriod(date.today(), 14)

    FORMAT = "%a %-d %b"  # Fri 26 Nov
    print(
        "Adding up bills for pay period: {} - {}\n".format(
            pp.start.strftime(FORMAT),
            pp.end.strftime(FORMAT),
        )
    )

    relevant_bills = get_bills_in_pay_period(bills_by_day, pp)

    # collect bills that vary
    variable_encountered = False
    for b in relevant_bills:
        if b.amount is None:
            if not variable_encountered:
                print("Looks like some bills' amounts vary...")
                variable_encountered = True
            b.amount = int(input(f"Input amount for {b.name}: "))

    # summarize
    total = sum([b.amount for b in relevant_bills])
    print(f"\nTotal: {total}")


if __name__ == "__main__":
    main()
