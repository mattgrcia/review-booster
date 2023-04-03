import base64
import json
import os
import requests
from tqdm import tqdm


class Shipstation:
    def __init__(self):
        self.key = os.environ.get("SHIPSTATION_API_KEY")
        self.secret_key = os.environ.get("SHIPSTATION_API_SECRET_KEY")
        self.auth_header = base64.b64encode(
            bytes(f"{self.key}:{self.secret_key}".encode("ascii"))
        ).decode("utf-8")
        self.headers = {
            "Host": "ssapi.shipstation.com",
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json",
        }

    def get_order(self, order_id):

        endpoint = f"https://ssapi.shipstation.com/orders/{order_id}"
        order_response = json.loads(requests.get(endpoint, headers=self.headers).text)

        return order_response

    def get_shipment_pages(self):

        endpoint = "https://ssapi.shipstation.com/shipments"
        response_dict = json.loads(requests.get(endpoint, headers=self.headers).text)
        num_pages = response_dict["pages"]

        return num_pages

    def get_shipments(self):

        shipments = []

        for page in tqdm(
            range(1, self.get_shipment_pages() + 1), position=0, leave=True
        ):
            endpoint = f"https://ssapi.shipstation.com/shipments?page={page}"
            response_dict = json.loads(
                requests.get(endpoint, headers=self.headers).text
            )
            page_shipments = response_dict["shipments"]

            shipments += page_shipments

        return shipments
