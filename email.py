# --------------------------------------------------------------------------
# email.py
# 
# Author: Emmandra
# -----------------------------------------------------------------------
#

from flask_mail import Mail, Message


def massEmail(mail, bidders, message):

    for bidder in bidders:
        bidder = bidder + '@princeton.edu'

    for bidder in bidders:
        print(bidder)

    msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                          recipients=bidders, body=message)

    mail.send(msg)
