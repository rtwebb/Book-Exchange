# --------------------------------------------------------------------------
# bookExchange.py
# book-exchange flask file, that works as web-framework
# Author: Toussaint, Tiana, Emmandra
# -----------------------------------------------------------------------

from sys import stderr, argv
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from flask_mail import Mail, Message
from queryDatabase import QueryDatabase
from datetime import datetime
from CASClient import CASClient
from json import dumps
from venmo_api import Client, get_user_id
from my_email import sendEmail
#from wtforms import TextField, Form

# -----------------------------------------------------------------------

app = Flask(__name__, template_folder='template')


# Do we need this/ how do we use this??????
# Generated by os.urandom(16)
app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'

# email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tigerbookexchange@gmail.com'
app.config['MAIL_PASSWORD'] = '123Book-Exchange'
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

database = QueryDatabase()

# -----------------------------------------------------------------------


@app.route('/', methods=['GET', 'POST'])
@app.route('/homePage', methods=['GET', 'POST'])
def homePageTemplate():
    username = CASClient().authenticate()

    # need to get recently listed books to show
    results = []
    try:
        results = database.homeRecents()
        if results == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    except Exception as e:
        print("Error: " + str(e), file=stderr)
        html = render_template('errorPage.html')
        response = make_response(html)
        return response

    # getting images corresponding to each book
    # if no image was uploaded - using a stock photo
    images = []

    # Acessing images
    i = 0
    for dict in results:
        if dict["images"]:
            image = dict["images"]
            images.append(image[0].url)
            dict["images"] = i
            i += 1
        else:
            images.append(
                "http://res.cloudinary.com/dijpr9qcs/image/upload/bxtyvg9pnuwl11ahkvhg.png")
            dict["images"] = i
            i += 1
    
    html = render_template('homePage.html', results=results, images=images,
                           username=username)
    response = make_response(html)
    return response


# -----------------------------------------------------------------------
@app.route('/searchResults', methods=['GET'])
def searchResultsTemplate():
    username = CASClient().authenticate()

    # need to get results based on search query
    # once get object send to searchResults
    # each book needs to link to buyerPage with more information
    # set cookies on search query to follow through searchResults and buyerPage

    # drop down
    # check if it is equal to value
    dropDown = request.args.get('dropDown')
    print("Drop-down: ", dropDown)
    if dropDown == "isbn":
        searchType = 1
    elif dropDown == "title":
        searchType = 2
    elif dropDown == "crscode":
        searchType = 3
    else:
        searchType = 4

    query = request.args.get('query')

    if dropDown is None:
        searchType = 0
    if query == '' or query is None:
        query = ''

    results = []

    # checking for null inputs and not interacting with drop-down
    if searchType == 0 or query == '':
        if not results:
            results = None
            images = None
        html = render_template('searchResults.html', results=results, searchType=searchType,
                               username=username, query=query, image=images)
        response = make_response(html)
        return response
    # proper input (drop-down filled in and query sent)
    else:
        uniqueIds = []
        images = []
        try:
            results = database.search(searchType, query, "1")
            if results == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            # Acessing images
            i = 0
            for dict in results:
                if dict["images"]:
                    image = dict["images"]
                    images.append(image[0].url)
                    dict["images"] = i
                    i += 1

                else:
                    images.append(
                        "http://res.cloudinary.com/dijpr9qcs/image/upload/bxtyvg9pnuwl11ahkvhg.png")
                    dict["images"] = i
                    i += 1

        except Exception as e:
            print(argv[0] + ": " + str(e), file=stderr)
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

        html = render_template('searchResults.html', results=results,
                               username=username, query=query, searchType=searchType,
                               images=images)
        response = make_response(html)
        return response


# -----------------------------------------------------------------------

@app.route('/sellerPage', methods=['GET', 'POST'])
def sellerPageTemplate():
    username = CASClient().authenticate()

    # when sending to profile page have a "successful" message display
    html = render_template('sellerPage.html', method='GET', username=username)

    response = make_response(html)
    return response

# -----------------------------------------------------------------------


@app.route('/buyerPage', methods=['GET', 'POST'])
def buyerPageTemplate():
    username = CASClient().authenticate()

    uniqueId = request.args.get('bookid')
    print('uniqueID', uniqueId)

    # if check for if uniqueID is none
    # if (uniqueId == None):
    #     return errorMsg('Invalid book ID')
    results = []
    try:
        
        results = database.getDescription(uniqueId)
        print("results: ", results)

        # error checking - if error render errorPage
        if results == -1:
            print("inside error")
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    except Exception as e:
        # error checking - if error render errorPage
        print("inside except")
        print("Error: " + str(e), file=stderr)
        html = render_template('errorPage.html')
        response = make_response(html)
        return response


    # Acessing images
    images = []

    i = 0
    for dict in results:
        if dict["images"]:
            image = dict["images"]
            images.append(image[0].url)
            print("image: ", image[0].url)
            dict["images"] = i
            print("image value: ", dict["images"])
            i += 1
        else:
            images.append(
                "http://res.cloudinary.com/dijpr9qcs/image/upload/bxtyvg9pnuwl11ahkvhg.png")
            dict["images"] = i
            print("image value: ", dict["images"])
            i += 1

            
    # whatever she called it and pass args
        
    # buyerPage needs link back to home page
    # If user makes a bid
    # check to make sure if they are sure about the amount
    # if it is correct show success page and have a link to go back to homePage
    # if no stay on buyer page

    html = render_template('buyerPage.html', results=results, images=images, uniqueId=uniqueId)
    response = make_response(html)
    return response


# ----------------------------------------------------------------------

@app.route('/profilePage', methods=['GET', 'POST'])
def profilePageTemplate():
    username = CASClient().authenticate()
    username = username.strip()
    listingID = request.args.get('list')
    sellerID = request.args.get('sellerID')
    bidder = request.args.get('bidder')
    title = request.args.get('title')
    highestBid = request.args.get('highest')

    try:
        # link to site to confirm
        # give time limit

        # send to bidder
        if 'accept' in request.form:

            error1 = database.updateStatus(listingID, bidder, 'accepted')
            if error1 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            error2 = sendEmail(mail, bidder, 'accept', username, highestBid, title)
            if error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response


        #send to bidder -> if it was the highest bidder send to everyone 
        elif 'decline' in request.form:
            error1 = database.updateStatus(listingID, bidder, 'declined')
            if error1 == -1 :
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            #need to update highest bid 
            error2 = database.removeMyBid(bidder, listingID)
            if error1 == -1 or error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            error3 = sendEmail(mail, bidder, 'decline', username, highestBid, title)
            if error3 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

        #confirm button should stay up
        #dont send to all bidders until it'spurchased
        # send email to all bidders and seller
        elif 'confirm' in request.form:
            error1 = database.updateStatus(listingID, username, 'confirmed')
            if error1 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            #later need to distinguish between confirm and purchase so can delete bids
            error2 = sendEmail(mail, username, 'confirm', sellerID, highestBid, title)
            if error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            return redirect(url_for('checkout'))

        #tell what the next highest bid is
        #send to seller and bidders
        elif 'deny' in request.form:
            error1 = database.updateStatus(listingID, username, 'declined')
            if error1 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            error2 = database.removeMyBid(username, listingID)
            if error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response
            
            allBidders = database.getAllBids(listingID)
            if allBidders == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            error3 = sendEmail(mail, allBidders, 'deny', sellerID, highestBid, title)
            if error3 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response


        #if it's the highest bid need to notify everyone
        # user wants to delete their bid
        deleteBidBuyerID = request.args.get('deleteBidBuyerID')
        deleteBidListingID = request.args.get('deleteBidListingID')
        if deleteBidBuyerID is not None and deleteBidListingID is not None:
            database.removeMyBid(deleteBidBuyerID, deleteBidListingID)

        #Need to notify bidders
        # user wants to delete their listing
        deleteListingID = request.args.get('deleteListingID')
        if deleteListingID is not None:
            database.removeListing(deleteListingID)

        # query database for the given user to update profilePage
        listings = database.myListings(username)
        if listings == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response
        # use this to reset the forms in mylistings in the profilepage
        # for book in listings:
        # database.updateStatus(book[5], book[2], 'pending')
        purchases = database.myPurchases(username)
        if purchases == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response
        bids = database.myBids(username)
        if listings == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    except Exception as e:
        print("Error: " + str(e), file=stderr)
        html = render_template('errorPage.html')
        response = make_response(html)
        return response

    html = render_template('profilePage.html', username=username, listings=listings,
                           purchases=purchases, bids=bids)
    response = make_response(html)
    return response

# ----------------------------------------------------------------------


@app.route('/aboutUs', methods=['GET'])
def aboutUsTemplate():
    username = CASClient().authenticate()
    client_token = generate_client_token()

    html = render_template(
        'aboutUs.html', client_token=client_token, username=username)

    response = make_response(html)
    return response


# ----------------------------------------------------------------------
@app.route('/autoComplete', methods=['GET'])
def autoComplete():
    username = CASClient().authenticate()

    dropDown = request.args.get('searchType')
    query = request.args.get('query')

    query = request.args.get('query')

    # ask Tiana to return ISBN
    if dropDown == "isbn":
        index = 'isbn'
        searchType = 1
    elif dropDown == "title":
        index = 'title'
        searchType = 2
    elif dropDown == "crscode":
        index = 'crscode'
        searchType = 3
    else:
        index = 'crstitle'
        searchType = 4

    results = []
    try:
        results = database.search(searchType, query, 0)
        if results == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response
    except Exception as e:
        print("Error: " + str(e), file=stderr)
        html = render_template('errorPage.html')
        response = make_response(html)
        return response

    # make the list of possible automcomplete
    values = []  # past values
    if results is not None:
        autoComplete = []
        for dict in results:
            if dict[index] not in values:
                values.append(dict[index])
                autoComplete.append(dict[index])

    autoComplete.sort(key=lambda v: v.upper())

    jsonStr = dumps(autoComplete)
    response = make_response(jsonStr)
    response.headers['Content-Type'] = 'application/json'
    return response


# ----------------------------------------------------------------------
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    username = CASClient().authenticate()

    #access_token = Client.get_access_token(username='emmandrawright@yahoo.com',
                                      # password='Darrell1')

    #venmo = Client(access_token=access_token)

    #bac = venmo.user.search_for_users(query="BACDance", page=1)
    #i = 0
    #for user in bac:
        #print("user ", i, ": ", user.username)
    
    #userID = get_user_id(bac[0], None)
    
    # Request money
    #venmo.payment.request_money(32.5, "house expenses", str(userID))


    html = render_template('checkout.html', username=username)
    response = make_response(html)

    return response

# ----------------------------------------------------------------------
@app.route('/congratsPage', methods=['GET', 'POST'])
def congratsPage():
    username = CASClient().authenticate()
    username = username.strip()
    msg = ""

    # profile page: accepting a bid on your listing; confirming your bid to purchase book
        # Congrats you have accepted a bid, now we just need bidder to confirm
        # Congrats you and the seller have agreed on purchase, proceed to checkout

    # bid update 
    if request.args.get('bookid'):
        buyerID = username
        buyNow = request.args.get('buyNow')
        uniqueId = request.args.get('bookid')
        if buyNow is not None:
            print('buyNow')
            database.buyNow(buyerID, uniqueId, buyNow)
            msg += "You have succesfully placed your bid, now we are just waiting on the sellers confirmation!"
        else:
            bid = request.form.get('bid')
            print('bid: ', bid)
            database.addBid(buyerID, uniqueId, bid)
            msg += "You have succesfully placed your bid, now we are just waiting on the sellers confirmation!"
    elif request.method == 'POST':  
        isbn = request.form.get('isbn')
        print("isbn: ", isbn)
        title = request.form.get('title')
        print("title: ", title)
        minprice = request.form.get('minPrice')
        print("minPrice: ", minprice)
        buynow = request.form.get('buyNow')
        print("buyNow: ", buynow)
        image1 = request.files.get('image1')
        image2 = request.files.get('image2')
        image3 = request.files.get('image3')
        # authors as a list; coursename vs coursenumber
        author = request.form.get('prof1')
        print("author: ", author)
        crscode = request.form.get('crscode')
        print('Coursecode:', crscode)
        crstitle = request.form.get('crstitle')
        print('Coursetitle:', crstitle)
        condition = request.form.get('bookCondition')
        print('condition: ', condition)
        time = datetime.now()
        listTime = time.strftime("%m:%d:%Y:%H:%M:%S")


        # hardcode
        crscode = "COS340"
        crstitle = "The practice of life"
        condition = "Poor"
        minprice = 24
        buynow = 34
        # confirmation JS stuff

        # passing to database
        try:
            images = []
            if image1:
                images.append(database.imageToURL(image1))
            if image2:
                images.append(database.imageToURL(image2))
            if image3:
                images.append(database.imageToURL(image3))

            database.add(isbn, title, [author], crscode, crstitle, username, condition,
                         minprice, buynow, listTime, images)
            msg += "You have sucessfully created a listing! It won't be long until the bids start rolling in!"
        except Exception as e:
            print("Error: " + str(e), file=stderr)
            html = render_template('errorPage.html')
            response = make_response(html)
            return response


    html = render_template('congratsPage.html', username=username, msg=msg)
    response = make_response(html)

    return response

# ----------------------------------------------------------------------
# MAKE LOGOUT A DROP DOWN FROM THE TIGER ICON
@app.route('/collapse', methods=['GET'])
def collapse():
    username = CASClient().authenticate()
    username = username.strip()

    listingID = request.args.get('list')
    sellerID = request.args.get('sellerID')
    bidder = request.args.get('bidder')
    title = request.args.get('title')
    highestBid = request.args.get('highest')

    try:
        # link to site to confirm
        # give time limit

        # send to bidder
        if 'accept' in request.form:

            error1 = database.updateStatus(listingID, bidder, 'accepted')
            if error1 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            error2 = sendEmail(mail, bidder, 'accept', username, highestBid, title)
            if error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response


        #send to bidder -> if it was the highest bidder send to everyone 
        elif 'decline' in request.form:
            error1 = database.updateStatus(listingID, bidder, 'declined')
            if error1 == -1 :
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            #need to update highest bid 
            error2 = database.removeMyBid(bidder, listingID)
            if error1 == -1 or error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            error3 = sendEmail(mail, bidder, 'decline', username, highestBid, title)
            if error3 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

        #confirm button should stay up
        #dont send to all bidders until it'spurchased
        # send email to all bidders and seller
        elif 'confirm' in request.form:
            error1 = database.updateStatus(listingID, username, 'confirmed')
            if error1 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            #later need to distinguish between confirm and purchase so can delete bids
            error2 = sendEmail(mail, username, 'confirm', sellerID, highestBid, title)
            if error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            return redirect(url_for('checkout'))

        #tell what the next highest bid is
        #send to seller and bidders
        elif 'deny' in request.form:
            error1 = database.updateStatus(listingID, username, 'declined')
            if error1 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            error2 = database.removeMyBid(username, listingID)
            if error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response
            
            allBidders = database.getAllBids(listingID)
            if allBidders == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            error3 = sendEmail(mail, allBidders, 'deny', sellerID, highestBid, title)
            if error3 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response


        #if it's the highest bid need to notify everyone
        # user wants to delete their bid
        deleteBidBuyerID = request.args.get('deleteBidBuyerID')
        deleteBidListingID = request.args.get('deleteBidListingID')
        if deleteBidBuyerID is not None and deleteBidListingID is not None:
            database.removeMyBid(deleteBidBuyerID, deleteBidListingID)

        #Need to notify bidders
        # user wants to delete their listing
        deleteListingID = request.args.get('deleteListingID')
        if deleteListingID is not None:
            database.removeListing(deleteListingID)

        # query database for the given user to update profilePage
        listings = database.myListings(username)
        if listings == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response
        # use this to reset the forms in mylistings in the profilepage
        # for book in listings:
        # database.updateStatus(book[5], book[2], 'pending')
        purchases = database.myPurchases(username)
        if purchases == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response
        bids = database.myBids(username)
        if listings == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    except Exception as e:
        print("Error: " + str(e), file=stderr)
        html = render_template('errorPage.html')
        response = make_response(html)
        return response

    html = render_template('collapse.html', username=username, listings=listings,
                           purchases=purchases, bids=bids)
    response = make_response(html)
    return response

# ----------------------------------------------------------------------
# MAKE LOGOUT A DROP DOWN FROM THE TIGER ICON
@app.route('/logout', methods=['GET'])
def logout():
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
