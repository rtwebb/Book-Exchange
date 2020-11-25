# --------------------------------------------------------------------------
# bookExchange.py
# book-exchange flask file, that works as web-framework
# Author: Toussaint, Tiana, Emmandra
# -----------------------------------------------------------------------

from venmo_api import Client, get_user_id
from queryDatabase import QueryDatabase
from sys import stderr, argv


#make venmo username pop up in congrats page 
#create update venmo Username

def validateUsername(venmoUsername):

    print('before client')
    venmo = Client(access_token='d095f97905ba8bb6a2b84477e411d08cc000f6eadf261624b29e88ef15ab4ada')
    print('after client')


    buyer = venmo.user.search_for_users(query=venmoUsername, page=1)

    if len(buyer) > 1:
        return -1
    

def sendRequest(database, venmoUsername, buyerId, cost, title, sellerId, listingID ):
    try:
        error = validateUsername(venmoUsername)
        if error == -1:
            return -1

        print('before client')
        venmo = Client(access_token='d095f97905ba8bb6a2b84477e411d08cc000f6eadf261624b29e88ef15ab4ada')
        print('after client')

        buyer = venmo.user.search_for_users(query=venmoUsername, page=1)

        print('buyer: ', buyer[0])
        print('buyer id: ', buyer[0].id)
        print(buyer[0].username)

        # Request money
        #add error check for this too
        #venmo.payment.request_money(float(cost), "Book-Exchange bid for " + title , str(buyer[0].id))

        transaction = database.getTransaction(buyerId)
        if transaction == None:
            return database.addTransaction(venmoUsername, buyerId)

    except Exception as e:
        print(argv[0] + ':', e, file=stderr)
        return -1


def checkTransactions(database, buyerId, cost ):

    try:

        print('before client')
        venmo = Client(access_token='d095f97905ba8bb6a2b84477e411d08cc000f6eadf261624b29e88ef15ab4ada')
        print('after client')

        myProfile = venmo.user.get_my_profile()
        print('my profile', myProfile)

        venmoUsername = database.getTransaction(buyerId)
        if venmoUsername == -1:
            return -1

        buyer = venmo.user.search_for_users(query=venmoUsername, page=1)
        userID = buyer[0].id
        
        transaction = venmo.user.get_transaction_between_two_users(myProfile.id, userID)
        print("transaction: ", transaction)
        # if target.id = buyer.id, if amount = cost, if status == 'settled', if seller = seller and listing
        # note = BookExchange: buying book title form sellerID (listing ID)
        for trans in transaction:
            print('target: ', trans.target)
            print('note: ', trans.note)
            print('amount: ', trans.amount)
            print('status: ', trans.status)
            if trans.target.id == venmoUsername and trans.amount == cost and trans.status == 'settled':
                return True
            else:
                return False

    except Exception as e:
        print(argv[0] + ':', e, file=stderr)
        return -1


def sendMoney(database, sellerId, buyerId, title, cost):

    try:

        print('before client')
        venmo = Client(access_token='d095f97905ba8bb6a2b84477e411d08cc000f6eadf261624b29e88ef15ab4ada')
        print('after client')

        venmoUsername = database.getTransaction(buyerId)
        if venmoUsername == -1:
            return -1
        
        buyer = venmo.user.search_for_users(query=venmoUsername, page=1)
        userID = buyer[0].id

        venmo.payment.send_money(.01, title, userID)

    except Exception as e:
        print(argv[0] + ':', e, file=stderr)
        return -1

def accessToken():

    access_token = Client.get_access_token(username='emmandrawright@yahoo.com',
                                               password='Darrell1')

    return access_token

#-------------------------------------------------------------------
