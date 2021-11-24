import calendar
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
import json
import sys
from typing import Dict, List


@dataclass
class Bill:
    day_of_month: int
    amount: int
    name: str

    def __str__(self):
        return f"{self.name}: {self.amount} on {self.day_of_month}"


def bills_as_dict(bills: List[Bill]) -> Dict[int, Bill]:
    bills_by_day = defaultdict(lambda: [])
    for b in bills:
         bills_by_day[b.day_of_month].append(b)
    return bills_by_day


PAY_PERIOD_DAYS = 14


def main():
    try:
        with open("bills.json") as f:
            bills_raw = json.load(f)
    except KeyError:
        print("You must add your bills to bills.json before using this.")
        sys.exit(2)

    bills = [Bill(*b) for b in bills_raw["monthly"]]
    bills_by_day = bills_as_dict(bills)

    start_date = date.today()
    end_date = start_date + timedelta(days=PAY_PERIOD_DAYS)
    print(f"{start_date} - {end_date}")

    # will we cross into the next month?
    is_cross_month = start_date.month != end_date.month
    last_day_of_month = calendar.monthrange(start_date.year, start_date.month)[1]

    # collect bills from the start (inclusive) to end date (exclusive)
    current_date = None
    relevant_bills = []
    for i in range(0, PAY_PERIOD_DAYS):
        # add today's bills
        current_date = start_date + timedelta(days=i)
        relevant_bills.extend(bills_by_day[current_date.day])
        
        # don't miss bills on days 29-31
        if is_cross_month and current_date.day == last_day_of_month:
            while current_date.day < last_day_of_month:
                current_date += timedelta(days=1)
                relevant_bills.extend(bills_by_day[current_date.day])

    # collect bills that vary
    for b in relevant_bills:
        if b.amount is None:
            b.amount = int(input(f"Input amount for {b.name}: "))

    # summarize
    total = sum([b.amount for b in relevant_bills])
    print(f"\nTotal: {total}")

if __name__ == "__main__":
    main()
