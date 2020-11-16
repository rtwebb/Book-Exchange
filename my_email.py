# ----------------------------------------------------------------------
# my_email.py 
# 
# Author: Emmandra 
# ----------------------------------------------------------------------
#

from flask_mail import Mail, Message
from sys import stderr


def sendEmail(mail, bidders: [], status, seller: None, cost: None, title: None):

    if status == 'accept':
        message = "Hello " + bidders[0] + "," + "\n" + "\n" + \
            "Congratulations! Your bid was accepted by" + seller + ". "  + \
            "Please log into book-exchange-cos333herokuapp.com to confirm or deny your purchase of this book within the next 48hrs." + \
            "If you do not make a decision within the next 48hrs the seller is aythorized to delete your bid." + \
            "Below is the summary of your bid." + "\n" + "\n" + \
            "Book Title: " + title + "\n" + \
            "Cost: " + str(cost) + "\n" + \
            "SellerID: " + seller + "\n" + "\n" + \
            "Sincerely," + "\n" + \
            "The Book-Exchange team"
    
    if status == 'decline':
        message = ""
    if status == 'confirm':
        message = ""
    if status == 'deny':
        message = ""

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
