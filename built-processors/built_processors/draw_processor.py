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
        res = requests.get(f'{self.budgets_url}/budgets').json()

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
        res = requests.get(f'{self.budgets_url}/items').json()

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
        return requests.get(f'{self.draws_url}/requests').json()


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
