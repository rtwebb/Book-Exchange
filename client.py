# --------------------------------------------------------------------------
# client.py
# Author: Emmandra
# -----------------------------------------------------------------------

from venmo_api import Client

# Get your access token. You will need to complete the 2FA process
access_token = Client.get_access_token(username='emmandrawright@yahoo.com',
                                       password='Darrell1')

venmo = Client(access_token=access_token)

# Search for users. You get 50 results per page.
users = venmo.user.search_for_users(query="Peter", page=2)

i = 0
for user in users:
    print("user " + i + ": " + user.username)
    i += 1

# Or, you can pass a callback to make it multi-threaded
i = 0
def callback(users):
   for user in users:
       print("user " + i + ": " + user.username)
       i += 1
venmo.user.search_for_users(query="peter",
                            callback=callback,
                            page=2,
                            count=10)

bac = venmo.user.search_for_users(query="BACDance", page=1)
i = 0
for user in bac:
   print("user " + i + ": " + user.username)

# Request money
#venmo.payment.request_money(32.5, "house expenses", "1122334455667")