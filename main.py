import datetime
import pandas as pd
from tqdm import tqdm
from emailer import Emailer
from shipping import Shipping
from shipstation import Shipstation


def main():

    # Instantiate objects to be used throughout the script
    shipstation = Shipstation()
    shipping = Shipping()

    # Get all shipment information from ShipStation
    print("\nGetting shipments...", end="")
    all_shipments = shipstation.get_shipments()
    print("done!\n")

    # Filter shipments for only those that were delivered, per ShipStation
    print("\nFiltering for delivered shipments...", end="")
    delivered_shipments = [
        shipment for shipment in all_shipments if shipment["confirmation"] == "delivery"
    ]
    print("done!\n")

    # Filter delivered shipments created in the last week for those with orders created in the last week
    print("\nFiltering for orders within the last week...", end="")
    good_shipments = []
    for shipment in tqdm(delivered_shipments, position=0, leave=True):

        order_response = shipstation.get_order(shipment["orderId"])
        order_date = datetime.datetime.strptime(
            order_response["orderDate"], "%Y-%m-%dT%H:%M:%S.%f0"
        )

        if order_date > datetime.datetime.now() - datetime.timedelta(days=8):
            if len(order_response["items"]) == 1:
                good_shipments.append((shipment, order_response))
    print("done!\n")

    # Get tracking info from USPS and UPS
    print("\nGetting tracking info...", end="")
    usps_info = {}
    usps_tracking_numbers = [
        s[0]["trackingNumber"] for s in good_shipments if "usps" in s[0]["serviceCode"]
    ]
    for tracking_number in usps_tracking_numbers:
        usps_info[tracking_number] = shipping.get_ups_tracking(tracking_number)

    ups_info = {}
    ups_tracking_numbers = [
        s[0]["trackingNumber"] for s in good_shipments if "ups" in s[0]["serviceCode"]
    ]
    for tracking_number in ups_tracking_numbers:
        ups_info[tracking_number] = shipping.get_ups_tracking(tracking_number)

    # Combine tracking info into one dictionary
    tracking_info = {**ups_info, **usps_info}

    print("done!\n")

    # Filter shipments for those that were confirmed as delivered during the previous business day by USPS or UPS
    print("\nFiltering for deliveries confirmed by the carrier...", end="")
    actually_delivered = [
        s
        for s in good_shipments
        if tracking_info.get(s[0]["trackingNumber"], [0, False])[1]
        and datetime.datetime.strptime(
            tracking_info.get(s[0]["trackingNumber"], ["2023-01-01 00:00", False])[0],
            "%Y-%m-%d %H:%M",
        ).date()
        == (datetime.datetime.now() - datetime.timedelta(days=3)).date()
    ]
    print("done!\n")

    # Create pandas DataFrame for data to be exported
    print("\nSending to CSV...", end="")
    filename = "shipstation_delivered.csv"
    values = []

    for i in range(len(actually_delivered)):
        shipment_id = actually_delivered[i][0]["shipmentId"]
        order_id = actually_delivered[i][0]["orderId"]
        email = actually_delivered[i][0]["customerEmail"]
        ship_date = actually_delivered[i][0]["shipDate"]

        order_date = actually_delivered[i][1]["createDate"]
        bill_to = actually_delivered[i][1]["billTo"]
        ship_to = actually_delivered[i][1]["shipTo"]
        item = actually_delivered[i][1]["items"][0]["sku"]
        quantity = actually_delivered[i][1]["items"][0]["quantity"]
        tracking_number = actually_delivered[i][0]["trackingNumber"]

        values.append(
            (
                shipment_id,
                order_id,
                email,
                ship_date,
                order_date,
                bill_to,
                ship_to,
                item,
                quantity,
                tracking_number,
            )
        )

    df = pd.DataFrame(
        values,
        columns=[
            "shipmentId",
            "orderId",
            "customerEmail",
            "shipDate",
            "orderDate",
            "billTo",
            "shipTo",
            "sku",
            "quantity",
            "trackingNumber",
        ],
    )
    df["deliveryDate"] = df["trackingNumber"].map(
        {k: v[0] for k, v in usps_info.items()}
    )
    df["deliveryDate"] = pd.to_datetime(df["deliveryDate"])
    df.to_csv(filename, index=False)
    print("done!\n")

    # Sending email to relevant parties
    emailer = Emailer(to_address="matt@jmac.com")
    print("\nSending email...", end="")
    subject = "ShipStation Daily Report"
    body = f"""
           Attached are the {len(df)} cherry-picked orders/shipments that were delivered during the 
           previous business day.
           """
    emailer.send_email(subject, body, filename)
    print("done!\n")


if __name__ == "__main__":
    main()
