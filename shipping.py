import datetime
import os
import requests
from usps import USPSApi


class Shipping:
    def __init__(self):

        self.usps_key = os.environ.get("USPS_KEY")
        self.ups_key = os.environ.get("UPS_KEY")

    def get_usps_tracking(self, tracking_number):

        usps = USPSApi(self.usps_key)

        track = usps.track(tracking_number)
        tracking_data = track.result

        event_time = tracking_data["TrackResponse"]["TrackInfo"]["TrackSummary"][
            "EventTime"
        ]
        event_date = tracking_data["TrackResponse"]["TrackInfo"]["TrackSummary"][
            "EventDate"
        ]
        event_datetime = datetime.datetime.strptime(
            event_date + " " + event_time, "%B %d, %Y %H:%M %p"
        )
        event_datetime = event_datetime.strftime("%Y-%m-%d %H:%M")
        delivered = (
            "delivered"
            in tracking_data["TrackResponse"]["TrackInfo"]["TrackSummary"][
                "Event"
            ].lower()
        )

        return event_datetime, delivered

    def get_ups_tracking(self, tracking_number):

        url = "https://onlinetools.ups.com/track/v1/details/{0}".format(tracking_number)
        headers = {
            "transId": "1",
            "transactionSrc": "test",
            "AccessLicenseNumber": self.ups_key,
        }
        data = requests.get(url, headers=headers)

        delivery_date = "unknown"
        delivered = False

        try:
            delivery_date = data.json()["trackResponse"]["shipment"][0]["package"][0][
                "deliveryDate"
            ][0]["date"]
            delivery_date = (
                delivery_date[:4] + "_" + delivery_date[4:6] + "_" + delivery_date[6:8]
            )
        except KeyError:
            pass

        try:
            delivered = (
                "delivered"
                in data.json()["trackResponse"]["shipment"][0]["package"][0][
                    "activity"
                ][0]["status"]["description"].lower()
            )
        except KeyError:
            pass

        return delivery_date, delivered
