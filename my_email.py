# ----------------------------------------------------------------------
# my_email.py 
# 
# Author: Emmandra 
# ----------------------------------------------------------------------
#

from flask_mail import Mail, Message
from sys import stderr


def sendEmail(mail, bidders, message):
    bodyMsg = "Hello " + bidder + "," + "\n" + "\n" + \
        "Your bid was accepted by" + username + ". "  + \
        "Please log into book-exchange-cos333herokuapp.com to confirm or deny your purchase of this book within the next 48hrs." + \
        "If you do not make a decision within the next 48hrs your bid will automatically be deleted." + \
        "Below is the summary of your bid." + "\n" + "\n" + \
        "Book Title: " + title + "\n" + \
        "Cost: " + cost + "\n" + \
        "SellerID: " + username + "\n" + "\n" + \
        "Sincerely," + "\n" + \
        "The Book-Exchange team"


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
