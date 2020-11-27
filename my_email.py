# ----------------------------------------------------------------------
# my_email.py 
# 
# Author: Emmandra, Tiana, Toussaint
# ----------------------------------------------------------------------
#

from flask_mail import Mail, Message
from sys import stderr


def sendEmail(mail, bidders: [], status, seller=None, highestBid=None, title=None):
    print(bidders, status, seller, highestBid, title)
    try:
        recipients = []
        message = ""

        if status == 'accept':
            recipients = bidders
            message += "Hello " + bidders[0] + "," + "\n" + "\n" + \
                       "Congratulations! Your bid was accepted by " + seller + ". " + \
                       "Please log into book-exchange-cos333.herokuapp.com to confirm or deny your purchase of this " \
                       "book within the next 48 hours. " + \
                       "If you do not make a decision within the next 48 hours, the seller is authorized to delete your " \
                       "bid. " + \
                       "Below is a summary of your bid." + "\n" + "\n" + \
                       "Book Title: " + title + "\n" + \
                       "Accepted Price: " + str(highestBid) + "0\n" + \
                       "Seller ID: " + seller + "\n" + "\n" + \
                       "Best," + "\n" + \
                       "The Book-Exchange Team"

        elif status == 'decline':
            recipients = bidders
            message += "Hello " + bidders[0] + "," + "\n" + "\n" + \
                       "Your bid was declined by " + seller + ". " + \
                       "You may log into book-exchange-cos333.herokuapp.com and place a bid on the same book, or you can" \
                       " explore different ones. " + \
                       "Below is the summary of your bid." + "\n" + "\n" + \
                       "Book Title: " + title + "\n" + \
                       "Your Bid: " + str(highestBid) + "0\n" + \
                       "Seller ID: " + seller + "\n" + "\n" + \
                       "Best," + "\n" + \
                       "The Book-Exchange Team"

        # maybe change this to highest bid not cost
        elif status == 'confirm':
            recipients = [seller]
            message += "Hello " + seller + "," + "\n" + "\n" + \
                       bidders[0] + " confirmed their bid!  " + \
                       "Once the buyer confirms that they have recieved the book, the money they sent us will be " \
                       "released to you ONLY if the buyer has sent the money requested through venmo to a Book-Exchange team member. " \
                       "We recommend that you gain proof of a money transaction (e.g. screenshot) before you give/send the book to the buyer. " \
                       "The Book-Exchange team is NOT responsible for releasing money to you if the seller has not yet sent it. " \
                       "Below is the summary of your Listing." + "\n" + "\n" + \
                       "Book Title: " + title + "\n" + \
                       "Accepted Price: " + str(highestBid) + "0\n" + \
                       "Buyer ID: " + bidders[0] + "\n" + "\n" + \
                       "Best," + "\n" + \
                       "The Book-Exchange Team"
            for i in range(len(recipients)):
                recipients[i] = recipients[i] + '@princeton.edu'
            msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                          recipients=recipients, body=message)
            mail.send(msg)

            buyer = bidders[0]
            recipients = [person for person in bidders if person != buyer]
            if len(recipients) >= 1:
                message1 = "Hello," + "\n" + "\n" + \
                           "A listing you bid on has been purchased. " + \
                           "Your bid for this book has been deleted, but if you have any other active bids, they are still " \
                           "valid. " + \
                           "You may log into book-exchange-cos333.herokuapp.com and place more bids at any time. " + \
                           "Below is the summary of this listing." + "\n" + "\n" + \
                           "Book Title: " + title + "\n" + \
                           "Highest Bid: " + str(highestBid) + "0\n" + \
                           "Seller ID: " + seller + "\n" + "\n" + \
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
            message += "Hello " + seller + "," + "\n" + "\n" + \
                       bidders[0] + " denied their bid. " + \
                       "You may log into book-exchange-cos333.herokuapp.com and accept another bid if your listing has " \
                       "any.  " + \
                       "Below is the summary of your listing." + "\n" + "\n" + \
                       "Book Title: " + title + "\n" + \
                       "Cost: " + str(highestBid) + "0\n" + \
                       "SellerID: " + seller + "\n" + "\n" + \
                       "Best," + "\n" + \
                       "The Book-Exchange Team"
            for i in range(len(recipients)):
                recipients[i] = recipients[i] + '@princeton.edu'
            msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                          recipients=recipients, body=message)
            mail.send(msg)

            buyer = bidders[0]
            recipients = [person for person in bidders if person != buyer]
            if len(recipients) >= 1:
                message1 = "Hello," + "\n" + "\n" + \
                           "The highest bidder on a book you have interacted with has withdrawn their bid. " + \
                           "You now have another chance to win the auction! " + \
                           "You may log into book-exchange-cos333.herokuapp.com and edit your bid. " + \
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

        elif status == 'removeListing':
            recipients = bidders
            message += "Hello," + "\n" + "\n" + \
                       seller + " has deleted a listing that you recently bid on. " + \
                       "Below is the summary of the listing." + "\n" + "\n" + \
                       "Book Title: " + title + "\n" + \
                       "SellerID: " + seller + "\n" + "\n" + "Someone else may be selling the book are looking for--" \
                                                             "log into book-exchange-cos333.herokuapp.com to find out!" + "\n" + "\n" + \
                       "Best," + "\n" + \
                       "The Book-Exchange Team"

        elif status == 'removeHighest':
            removed = bidders[0]
            recipients = [person for person in bidders if person != removed]
            message += "Hello," + "\n" + "\n" + \
                       "The highest bid on a listing you have recently bid on has been deleted. " + \
                       "Below is the summary of the listing." + "\n" + "\n" + \
                       "Book Title: " + title + "\n" + \
                       "Deleted Bid: " + str(highestBid) + '\n' + \
                       "SellerID: " + seller + "\n" + "\n" + "You can update your bid for a chance to win the " \
                                                             "auction! Good luck!" + "\n" + "\n" + \
                       "Best," + "\n" + \
                       "The Book-Exchange Team"

        elif status == 'received':
            recipients = [seller]
            message += "Hello " + seller + ", " + "\n" + "\n" + \
                       "You have successfully sold your book titled " + title + " for $" + highestBid + "0! " + \
                       "We know that it is a long process, but congratulations! " + \
                       "You should be receiving the funds in your venmo shortly." + "\n" + "\n" + \
                       "Best," + "\n" + \
                       "The Book-Exchange Team"

        elif status == 'sendBook':
            recipients = [seller]
            message += "Hello " + seller + ", " + "\n" + "\n" + \
                       "We have received the funds from the buyer. Please send the book to the buyer. " + \
                       "Once the buyer receives the book, funds will be released to your venmo account." + "\n" + "\n" + \
                       "Best," + "\n" + \
                       "The Book-Exchange Team"

        elif status == 'beatBid':
            currentHighest = bidders[0]
            recipients = [person for person in bidders if person != currentHighest]
            message += "Hello, " + "\n" + "\n" + \
                       "One of your recent bids has been beat. You still have a chance to win the auction, though --" + \
                       "simply update your bid at book-exchange-cos333.herokuapp.com! Below is a summary of the " \
                       "listing." + "\n" + "\n" + \
                       "Book Title: " + title + "\n" + \
                       "Highest Bid: " + str(highestBid) + '\n' + \
                       "SellerID: " + seller + "\n" + "\n" + \
                       "Best," + "\n" + \
                       "The Book-Exchange Team"

        for i in range(len(recipients)):
            recipients[i] = recipients[i] + '@princeton.edu'

        for bidder in bidders:
            print(bidder)

        if len(recipients) >= 1:
            msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                          recipients=recipients, body=message)
            mail.send(msg)

    except Exception as e:
        print("my_email.py Error: " + str(e), file=stderr)
        return -1
