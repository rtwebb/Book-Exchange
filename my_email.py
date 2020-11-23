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
                      "Congratulations! Your bid was accepted by " + seller + ". " + \
                      "Please log into book-exchange-cos333.herokuapp.com to confirm or deny your purchase of this " \
                      "book within the next 48hrs. " + \
                      "If you do not make a decision within the next 48hrs the seller is authorized to delete your " \
                      "bid. " + \
                      "Below is a summary of your bid." + "\n" + "\n" + \
                      "Book Title: " + title + "\n" + \
                      "Cost: " + str(highestBid) + "\n" + \
                      "SellerID: " + seller + "\n" + "\n" + \
                      "Best," + "\n" + \
                      "The Book-Exchange Team"

        elif status == 'decline':
            recipients = bidders
            message = "Hello " + bidders[0] + "," + "\n" + "\n" + \
                      "Your bid was declined by " + seller + ". " + \
                      "You may log into book-exchange-cos333.herokuapp.com and place a bid on the same book or a " \
                      "different one. " + \
                      "Below is the summary of your bid." + "\n" + "\n" + \
                      "Book Title: " + title + "\n" + \
                      "Your Bid: " + str(highestBid) + "\n" + \
                      "SellerID: " + seller + "\n" + "\n" + \
                      "Best," + "\n" + \
                      "The Book-Exchange Team"

        # maybe change this to highest bid not cost
        elif status == 'confirm':
            recipients = [seller]
            message = "Hello " + seller + "," + "\n" + "\n" + \
                      bidders[0] + " confirmed their bid.  " + \
                      "You should receive a confirmation email from us within the next 48 hours, once the buyer has " \
                      "sent payment for the book. " + \
                      "If you do not receive a confirmation email from us within the next 48 hours saying the book " \
                      "was purchased, " + \
                      "you are authorized to delete this bid. " + \
                      "Below is the summary of your Listing." + "\n" + "\n" + \
                      "Book Title: " + title + "\n" + \
                      "Cost: " + str(highestBid) + "\n" + \
                      "SellerID: " + seller + "\n" + "\n" + \
                      "Best," + "\n" + \
                      "The Book-Exchange Team"
            for i in range(len(recipients)):
                recipients[i] = recipients[i] + '@princeton.edu'
            msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                          recipients=recipients, body=message)
            mail.send(msg)

            recipients = bidders[1:]
            message1 = "Hello," + "\n" + "\n" + \
                       "A listing you bid on has been purchased. " + \
                       "Your bid for this book has been deleted, but if you have any other active bids, they are still " \
                       "valid." + \
                       "You may log into book-exchange-cos333.heroku.com and place more bids at any time. " + \
                       "Below is the summary of this listing." + "\n" + "\n" + \
                       "Book Title: " + title + "\n" + \
                       "Highest Bid: " + str(highestBid) + "\n" + \
                       "SellerID: " + seller + "\n" + "\n" + \
                       "Best," + "\n" + \
                       "The Book-Exchange Team"
            for i in range(len(recipients)):
                recipients[i] = recipients[i] + '@princeton.edu'
            msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                          recipients=recipients, body=message1)
            mail.send(msg)
            return

        # update seller and other bidders about withdrawn highest bid
        elif status == 'deny':
            recipients = [seller]
            message = "Hello " + seller + "," + "\n" + "\n" + \
                      bidders[0] + " denied their bid. " + \
                      "You may log into book-exchange-cos333.heroku.com and accept another bid if your listing has " \
                      "any.  " + \
                      "Below is the summary of your listing." + "\n" + "\n" + \
                      "Book Title: " + title + "\n" + \
                      "Cost: " + str(highestBid) + "\n" + \
                      "SellerID: " + seller + "\n" + "\n" + \
                      "Best," + "\n" + \
                      "The Book-Exchange Team"
            for i in range(len(recipients)):
                recipients[i] = recipients[i] + '@princeton.edu'
            msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                          recipients=recipients, body=message)
            mail.send(msg)

            recipients = bidders[1:]
            if len(recipients) >= 1:
                message1 = "Hello," + "\n" + "\n" + \
                           "The highest bidder on a book you have interacted with has withdrawn their bid. " + \
                           "You now have another chance to win the auction! " + \
                           "You may log into book-exchange-cos333.heroku.com and edit your bid. " + \
                           "Below is the summary of this listing." + "\n" + "\n" + \
                           "Book Title: " + title + "\n" + \
                           "SellerID: " + seller + "\n" + "\n" + \
                           "Best," + "\n" + \
                           "The Book-Exchange Team"
                for i in range(len(recipients)):
                    recipients[i] = recipients[i] + '@princeton.edu'
                msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                              recipients=recipients, body=message1)
                mail.send(msg)
            return

        elif status == 'remove':
            recipients = bidders
            message = "Hello," + "\n" + "\n" + \
                      seller + " has deleted a listing that you recently bid on. " + \
                      "Below is the summary of the listing." + "\n" + "\n" + \
                      "Book Title: " + title + "\n" + \
                      "SellerID: " + seller + "\n" + "\n" + "Someone else may be selling the book are looking for--" \
                                                            "log into book-exchange-cos333.herokuapp.com to find out!" + "\n" + "\n" + \
                      "Best," + "\n" + \
                      "The Book-Exchange Team"

        elif status == 'received':
            recipients = [seller]
            message = "Hello " + seller + ", " + "\n" + "\n" + \
                      "You have successfully sold your book titled " + title + " for $" + highestBid + "! " + \
                      "We know that it is a long process, but congrats! " + \
                      "You should be receiving the funds in your venmo shortly." + "\n" + "\n" + \
                      "Best," + "\n" + \
                      "The Book-Exchange Team"

        elif status == 'sendBook':
            recipients = [seller]
            message = "Hello " + seller + ", " + "\n" + "\n" + \
                      "We have received the funds from the buyer, please send the book to the buyer. " + \
                      "Once the buyer receives the book, funds will be released to your venmo account." + "\n" + "\n" + \
                      "Best," + "\n" + \
                      "The Book-Exchange Team"

        for i in range(len(recipients)):
            recipients[i] = recipients[i] + '@princeton.edu'

        for bidder in bidders:
            print(bidder)

        msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                      recipients=recipients, body=message)

        mail.send(msg)

    except Exception as e:
        print("Error: " + str(e), file=stderr)
        return -1
