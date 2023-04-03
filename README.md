### Background

The goal behind this project is twofold:

1) To alert the C-suite to "successful" deliveries that arrived at their destinations during the previous business day, with success being defined as arriving within one week of the respective being ordered, and
2) To automatically push these delivery details to MailChimp for an email campaign to ask these affected customers to provide both product and seller reviews.

The thinking behind this approach is that successful deliveries breed happier customers, and thus, these may make up a segment of customers from which reviews may be more abundantly (especially in the positive) given.

### Requirements

You will need API credentials (and potentially, accounts) from the following organizations.

[USPS](https://www.usps.com/business/web-tools-apis/)

[UPS](https://www.ups.com/upsdeveloperkit?loc=en_US)

[ShipStation](https://ship9.shipstation.com/settings/api)

[MailChimp](https://mailchimp.com/)


### Installation

To get started, you can just install from the requirements.txt file, or you may choose to stick with your own environment versions of packages, in which case, the one package that you will most likely need to add would be from USPS.

`
pip install -r requirements.txt
`
OR
`
pip install usps-api
`

### Functionality

The order of operations is as follows:
1. Get all shipments from ShipStation
2. Filter for those marked as "confirmation" = "delivery" by ShipStation
3. Filter for those that were created in the last week
4. Filter for related orders that were created in the last week
5. Get tracking info from USPS and UPS (for better delivery confirmation)
6. Filter for those delivered during the previous business day
7. Export details to CSV
8. Send email with CSV attached to required parties
9. Push data to MailChimp (not yet integrated)
