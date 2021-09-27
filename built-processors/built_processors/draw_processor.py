#!/usr/bin/env python3
from datetime import datetime
import requests

BUDGETS_URL = 'http://built-budgets'
DRAWS_URL = 'http://built-draws/'


class ServiceHelpers:
    def __init__(self, budgets_url=BUDGETS_URL, draws_url=DRAWS_URL):
        self.budgets_url = budgets_url
        self.draws_url = draws_url

    def get_budgets(self) -> dict:
        """Retrieves all budgets from built-budgets

        :return: A mapping of all budget amounts and remaining balances mapped to a budget ID
        :rtype: dict
        """
        # res = requests.get(f'{self.budgets_url}/budgets').json()

        res = [
            {
                "amount": "126000",
                "balance_remaining": "108500",
                "budget_id": 1
            },
            {
                "amount": "252000",
                "balance_remaining": "217000",
                "budget_id": 2
            }
        ]

        budgets = dict()
        for budget in res:
            budget_id = budget.pop('budget_id')
            budgets[budget_id] = {key: int(val) for key, val in budget.items()}
        return budgets

    def get_budget_items(self) -> dict:
        """Retrieves all budget items from built-budgets

        :return: A mapping of all budget items and funding info mapped to a budget item ID
        :rtype: dict
        """
        # res = requests.get(f'{self.budgets_url}/items').json()

        res = [
            {
                "budget_id": 1,
                "budget_item_id": 1,
                "funded_to_date": "2500",
                "original_amount": "10000"
            },
            {
                "budget_id": 1,
                "budget_item_id": 2,
                "funded_to_date": "15000",
                "original_amount": "16000"
            },
            {
                "budget_id": 1,
                "budget_item_id": 3,
                "funded_to_date": "0",
                "original_amount": "100000"
            },
            {
                "budget_id": 2,
                "budget_item_id": 4,
                "funded_to_date": "5000",
                "original_amount": "20000"
            },
            {
                "budget_id": 2,
                "budget_item_id": 5,
                "funded_to_date": "30000",
                "original_amount": "32000"
            },
            {
                "budget_id": 2,
                "budget_item_id": 6,
                "funded_to_date": "0",
                "original_amount": "200000"
            }
        ]

        items = dict()
        for item in res:
            item_id = item.pop('budget_item_id')
            items[item_id] = item
        return items

    def get_draw_requests(self) -> list:
        """Retrieves all outstanding draw requests from built-draws

        :return: A list of all outstanding draw requests
        :rtype: list
        """
        # return requests.get(f'{self.draws_url}/requests').json()

        return [
            {
                "amount": "750",
                "budget_id": 1,
                "budget_item_id": 2,
                "draw_request_id": 1,
                "effective_date": "11/15/2015"
            },
            {
                "amount": "2000",
                "budget_id": 1,
                "budget_item_id": 1,
                "draw_request_id": 2,
                "effective_date": "11/20/2015"
            },
            {
                "amount": "50000",
                "budget_id": 1,
                "budget_item_id": 3,
                "draw_request_id": 3,
                "effective_date": "10/5/2015"
            },
            {
                "amount": "60000",
                "budget_id": 1,
                "budget_item_id": 3,
                "draw_request_id": 4,
                "effective_date": "10/6/2015"
            },
            {
                "amount": "500",
                "budget_id": 1,
                "budget_item_id": 2,
                "draw_request_id": 5,
                "effective_date": "10/31/2015"
            },
            {
                "amount": "50000",
                "budget_id": 1,
                "budget_item_id": 3,
                "draw_request_id": 6,
                "effective_date": "10/7/2015"
            },
            {
                "amount": "1000",
                "budget_id": 1,
                "budget_item_id": 2,
                "draw_request_id": 7,
                "effective_date": "11/16/2015"
            },
            {
                "amount": "10000",
                "budget_id": 2,
                "budget_item_id": 4,
                "draw_request_id": 8,
                "effective_date": "12/17/2020"
            },
            {
                "amount": "8000",
                "budget_id": 2,
                "budget_item_id": 4,
                "draw_request_id": 9,
                "effective_date": "12/18/2020"
            },
            {
                "amount": "5000",
                "budget_id": 2,
                "budget_item_id": 4,
                "draw_request_id": 10,
                "effective_date": "12/18/2020"
            },
            {
                "amount": "500",
                "budget_id": 2,
                "budget_item_id": 5,
                "draw_request_id": 11,
                "effective_date": "12/1/2020"
            },
            {
                "amount": "2500",
                "budget_id": 2,
                "budget_item_id": 5,
                "draw_request_id": 12,
                "effective_date": "11/25/2020"
            },
            {
                "amount": "150000",
                "budget_id": 2,
                "budget_item_id": 6,
                "draw_request_id": 13,
                "effective_date": "12/15/2020"
            },
            {
                "amount": "75000",
                "budget_id": 2,
                "budget_item_id": 6,
                "draw_request_id": 14,
                "effective_date": "12/16/2020"
            },
            {
                "amount": "50000",
                "budget_id": 2,
                "budget_item_id": 6,
                "draw_request_id": 15,
                "effective_date": "12/25/2020"
            }
        ]


class DrawProcessor:
    def __init__(self):
        self.budgets = dict()
        self.items = dict()
        self.service = ServiceHelpers()
        self.item_balances = dict()

    def handler(self) -> dict:
        """Handles processing a list of draw requests. Requests are processed in chronological order by effective date
        and only if funds are available in both an item's remaining funding and its corresponding budget's remaining
        balance.

        :returns: A mapping of budget IDs to a list of processed draw request IDs
        :rtype: dict
        """
        # retrieve values from services
        self.budgets = self.service.get_budgets()
        self.items = self.service.get_budget_items()
        _draw_requests = self.service.get_draw_requests()
        draw_requests = self.sort_draw_requests(_draw_requests)
        self.set_remaining_item_budgets()

        # process draw requests
        processed_requests = dict()
        for req in draw_requests:
            # obtain values from draw request
            amount = int(req.get('amount'))
            budget_id = req.get('budget_id')
            item_id = req.get('budget_item_id')
            req_id = req.get('draw_request_id')

            # process draw request if funds are available
            if self.is_drawable(req):
                if processed_requests.get(budget_id, None):
                    processed_requests[budget_id].append(req_id)
                else:
                    processed_requests[budget_id] = [req_id]
                self.item_balances[item_id] -= amount
                self.budgets[budget_id]['balance_remaining'] -= amount

        return processed_requests

    def is_drawable(self, req: dict) -> bool:
        """Determines if a draw request is drawable based on its remaining funding.

        :param req: draw request
        :type req: dict
        :return: indication that the request is drawable
        :rtype: bool
        """
        item_id = req.get('budget_item_id')
        amount_requested = int(req.get('amount'))
        return amount_requested <= self.item_balances[item_id]

    @staticmethod
    def sort_draw_requests(draw_requests: list) -> list:
        """Sorts a list of draw requests by date.

        :param draw_requests: list of draw requests
        :type draw_requests: list
        :return: sorted list of draw requests
        :rtype: list
        """

        def draw_request_key(req: dict) -> datetime:
            return datetime.strptime(req.get('effective_date'), '%m/%d/%Y')

        draw_requests.sort(key=draw_request_key)
        return draw_requests

    def set_remaining_item_budgets(self):
        for item_id in self.items.keys():
            item = self.items[item_id]
            self.item_balances[item_id] = int(item.get('original_amount')) - int(item.get('funded_to_date'))


if __name__ == '__main__':
    draw_processor = DrawProcessor()
    print(draw_processor.handler())
