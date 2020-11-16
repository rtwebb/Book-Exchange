# ----------------------------------------------------------------------
# my_email.py 
# 
# Author: Emmandra 
# ----------------------------------------------------------------------
#

from flask_mail import Mail, Message
from sys import stderr


def sendEmail(mail, bidders, message):
    try:
        for i in range(len(bidders)):
            bidders[i] = bidders[i] + '@princeton.edu'

        for bidder in bidders:
            print(bidder)

        msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                      recipients=bidders, body=message)

        mail.send(msg)
    except Exception as e:
        print("Error: " + str(e), file=stderr)
        return -1
