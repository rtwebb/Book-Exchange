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
#fix automatic popup in seller page
#I edited my bid and two popped up

def validateUsername(venmoUsername):
    try:
        print('before client')
        venmo = Client(access_token='d095f97905ba8bb6a2b84477e411d08cc000f6eadf261624b29e88ef15ab4ada')
        print('after client')


        buyer = venmo.user.search_for_users(query=venmoUsername, page=1)

        if len(buyer) > 1:
            return 1
        else:
            return 0

    except Exception as e:
        print(argv[0] + ':', e, file=stderr)
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
        print('buyer: ', buyer)
        if len(buyer) != 0:
            print('buyer: ', buyer[0])
            print('buyer id: ', buyer[0].id)
            print(buyer[0].username)


            # Request money
            #add error check for this too
            venmo.payment.request_money(float(cost), "Book-Exchange bid for " + title , str(buyer[0].id))
        else:
            print('venmoUsername does not exist')

        transaction = database.addTransaction(venmoUsername, buyerId)
        if transaction == -1:
            return -1

 

    except Exception as e:
        print(argv[0] + ':', e, file=stderr)
        return -1


def checkTransactions(database, buyerId, cost):

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
        if len(buyer) != 0:
            userID = buyer[0].id
            
            transaction = venmo.user.get_transaction_between_two_users(myProfile.id, userID)
            #print("transaction: ", transaction)
            # if target.id = buyer.id, if amount = cost, if status == 'settled', if seller = seller and listing
            # note = BookExchange: buying book title form sellerID (listing ID)
            for trans in transaction:
                print('target.id: ', trans.target.id)
                print('userid: ', userID)
                print('note: ', trans.note)
                print('amount: ', trans.amount)
                print('cost: ', cost)
                print('status: ', trans.status)
                if str(trans.target.id) == str(userID) and str(trans.amount) == str(cost) and str(trans.status) == str('settled'):
                    return True
            #will this be a problem 
        else:
            print('venmoUsername does not exist')

        return False

    except Exception as e:
        print(argv[0] + ':', e, file=stderr)
        return -1


def sendMoney(database, sellerId, buyerId, title, cost):

    try:

        print('before client')
        venmo = Client(access_token='d095f97905ba8bb6a2b84477e411d08cc000f6eadf261624b29e88ef15ab4ada')
        print('after client')

        print('before getTrans')
        print('buyerId: ', buyerId)
        venmoUsername = database.getTransaction(sellerId)
        print('first venmoUsername: ', venmoUsername)
        print('after getTrans')
        if venmoUsername == -1:
            return -1

        print('before get UserId')
        print('venmoUsername: ', venmoUsername)
        buyer = venmo.user.search_for_users(query=venmoUsername, page=1)
        print('after get UserId')

        if len(buyer) != 0:
            userID = buyer[0].id

            print('before real send money')
            venmo.payment.send_money(float(cost), title, str(userID))
            print('after real send money')
        
        else:
            print('venmoUsername does not exist')


    except Exception as e:
        print(argv[0] + ':', e, file=stderr)
        return -1

def accessToken():

    access_token = Client.get_access_token(username='emmandrawright@yahoo.com',
                                               password='Darrell1')

    return access_token

#-------------------------------------------------------------------
