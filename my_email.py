# ----------------------------------------------------------------------
# my_email.py 
# 
# Author: Emmandra 
# ----------------------------------------------------------------------
#

from flask_mail import Mail, Message
from sys import stderr


def sendEmail(mail, bidders: [], status, seller: None, highestBid: None, title: None):

    try:
        recipients = []

        if status == 'accept':
            recipients = bidders
            message = "Hello " + bidders[0] + "," + "\n" + "\n" + \
                "Congratulations! Your bid was accepted by" + seller + ".  "  + \
                "Please log into book-exchange-cos333herokuapp.com to confirm or deny your purchase of this book within the next 48hrs.  " + \
                "If you do not make a decision within the next 48hrs the seller is aythorized to delete your bid.  " + \
                "Below is the summary of your bid." + "\n" + "\n" + \
                "Book Title: " + title + "\n" + \
                "Cost: " + str(highestBid) + "\n" + \
                "SellerID: " + seller + "\n" + "\n" + \
                "Sincerely," + "\n" + \
                "The Book-Exchange team"
            

        #maybe change this to highest bid not cost
        elif status == 'decline':
            recipients = bidders
            message = "Hello " + bidders[0] + "," + "\n" + "\n" + \
                "Your bid was declined by" + seller + ".  "  + \
                "You may log into book-exchange-cos333herokuapp.com and place a bid on the same book or a different one. " +\
                "Below is the summary of your bid." + "\n" + "\n" + \
                "Book Title: " + title + "\n" + \
                "Highest Bid: " + str(highestBid) + "\n" + \
                "SellerID: " + seller + "\n" + "\n" + \
                "Sincerely," + "\n" + \
                "The Book-Exchange team"

        #maybe change this to highest bid not cost
        elif status == 'confirm':
            recipients = [seller]
            message = "Hello " + seller + "," + "\n" + "\n" + \
                bidders[0] + "confirmed their bid.  " + \
                "You should receive a confimration email from us within the next 48 hours, once the buyer has sent payment for the book.  " +\
                "If you do not recieve a confirmation email from us within the next 48 hours saying the book was purchased,  " +\
                "you are authorized to delete this bid.  " + \
                "Below is the summary of your Listing." + "\n" + "\n" + \
                "Book Title: " + title + "\n" + \
                "Cost: " + str(highestBid) + "\n" + \
                "SellerID: " + seller + "\n" + "\n" + \
                "Status: confirmed" + \
                "Sincerely," + "\n" + \
                "The Book-Exchange team"
                
            

        elif status == 'deny':
            recipients = [seller]
            message = "Hello " + seller + "," + "\n" + "\n" + \
                bidders[0] + "denied their bid.  " + \
                "You may log into book-exchange-cos333heroku.com and accept another bid if your listing has any.  " + \
                "Below is the summary of your listing." + "\n" + "\n" + \
                "Book Title: " + title + "\n" + \
                "Cost: " + str(highestBid) + "\n" + \
                "SellerID: " + seller + "\n" + "\n" + \
                "Status: confirmed" + \
                "Sincerely," + "\n" + \
                "The Book-Exchange team"

        #need to send seperate one to seller
        elif status == 'purchased':
            #recipients = bidders
            #message1 = "Hello," + "\n" + "\n" + \
            # "A listing you bidded on has been purchased. " + \
                #"Your bid for this book has been deleted, but if you have any other active bids they are still valid." + \
            # "You may log into book-exchange-cos333heroku.com and place more bids at any time." + \
            # "Below is the summary of this listing." + "\n" + "\n" + \
            # "Book Title: " + title + "\n" + \
            # "Highest Bid: " + str(highestBid) + "\n" + \
            # "SellerID: " + seller + "\n" + "\n" + \
            # "Status: confirmed" + \
            # "Sincerely," + "\n" + \
                #"The Book-Exchange team"
            
            #message to seller
            recipients = [seller]
            message = "Hello " + seller + ", " + "\n" + "\n" + \
                "Your listing has been purchased. " + \
                "Please log into book-exchange-cos333heroku.com and enter your venmo information  " + \
                "Once we recieve confirmation from the buyer that they recieved the book, your money will be released to you.  " + \
                "Below is the summary of this listing." + "\n" + "\n" + \
                "Book Title: " + title + "\n" + \
                "Cost: " + str(highestBid) + "\n" + \
                "SellerID: " + seller + "\n" + "\n" + \
                "Status: purchased" + \
                "Sincerely," + "\n" + \
                "The Book-Exchange team"


    
        for i in range(len(bidders)):
            bidders[i] = bidders[i] + '@princeton.edu'

        for bidder in bidders:
            print(bidder)


        msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                    recipients=recipients, body=message)

        mail.send(msg)

    except Exception as e:
        print("Error: " + str(e), file=stderr)
        return -1
