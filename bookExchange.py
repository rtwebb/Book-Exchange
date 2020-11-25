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
from venmo import sendRequest, checkTransactions, sendMoney

# from wtforms import TextField, Form

# -----------------------------------------------------------------------

app = Flask(__name__, template_folder='template')

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
    username = username.strip()
    # need to get recently listed books to show
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

    # Accessing images
    i = 0
    for dict in results:
        if dict["images"]:
            image = dict["images"]
            images.append(image[0].url)
            dict["images"] = i
            i += 1
        else:
            images.append(
                "http://res.cloudinary.com/dijpr9qcs/image/upload/yah8siamtbmtg5wtnsdv.png")
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
    username = username.strip()
    # need to get results based on search query
    # once get object send to searchResults
    # each book needs to link to buyerPage with more information
    # set cookies on search query to follow through searchResults and buyerPage

    # drop down
    # check if it is equal to value
    dropDown = request.args.get('dropDown')
    query = request.args.get('query')
    sortBy = request.args.get('sortBy')

    if dropDown is None and query is None and sortBy is not None:
        dropDown = request.cookies.get('dropDown')
        query = request.cookies.get('query')

    if dropDown == "isbn":
        searchType = 1
    elif dropDown == "title":
        searchType = 2
    elif dropDown == "crscode":
        searchType = 3
    else:
        searchType = 4

    if dropDown is None:
        searchType = 0
    if query == '' or query is None:
        query = ''

    if sortBy is None:
        sortBy = "newest"

    images = []
    try:
        results = database.search(searchType, query, "1", sortBy)

        if results == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

        # Accessing images
        i = 0
        for dict in results:
            if dict["images"]:
                image = dict["images"]
                images.append(image[0].url)
                dict["images"] = i
                i += 1

            else:
                images.append(
                    "http://res.cloudinary.com/dijpr9qcs/image/upload/yah8siamtbmtg5wtnsdv.png")
                dict["images"] = i
                i += 1

    except Exception as e:
        print(argv[0] + ": " + str(e), file=stderr)
        html = render_template('errorPage.html')
        response = make_response(html)
        return response

    html = render_template('searchResults.html', results=results,
                           username=username, query=query, searchType=searchType,
                           images=images, sortBy=sortBy)

    response = make_response(html)
    if dropDown is not None:
        response.set_cookie('dropDown', dropDown)
    response.set_cookie('query', query)
    response.set_cookie('sortBy', sortBy)
    return response

# -----------------------------------------------------------------------


@app.route('/sellerPage', methods=['GET', 'POST'])
def sellerPageTemplate():
    username = CASClient().authenticate()
    uniqueId = request.args.get('bookid')

    if uniqueId is not None:
        book = None
        try:
            results = database.getDescription(uniqueId)
            msg = "**Please resubmit book images, if you had any**"

            for result in results:
                book = result
        except Exception as e:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    if uniqueId is None or uniqueId.strip == '':
        book = None
        msg = None

    # when sending to profile page have a "successful" message display
    html = render_template('sellerPage.html', username=username,
                           msg=msg, book=book)

    response = make_response(html)
    return response


# -----------------------------------------------------------------------


@app.route('/buyerPage', methods=['GET', 'POST'])
def buyerPageTemplate():

    uniqueId = request.args.get('bookid')
    print('uniqueID', uniqueId)

    # if check for if uniqueID is none
    # if (uniqueId == None):
    #     return errorMsg('Invalid book ID')

    try:
        results = database.getDescription(uniqueId)

        if results == -1 or not results:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    except Exception as e:
        print("Error: " + str(e), file=stderr)
        html = render_template('errorPage.html')
        response = make_response(html)
        return response

    # Accessing images
    images = []

    if len(results[0]["images"]) == 0:
        images.append(
            "http://res.cloudinary.com/dijpr9qcs/image/upload/yah8siamtbmtg5wtnsdv.png")
    else:
        for image in results[0]["images"]:
            images.append(image.url)

    html = render_template('buyerPage.html', results=results,
                           images=images, uniqueId=uniqueId)
    response = make_response(html)
    return response


# ----------------------------------------------------------------------

@app.route('/profilePage', methods=['GET', 'POST'])
def profilePageTemplate():
    username = CASClient().authenticate()
    username = username.strip()
    print("username: ", username)
    listingID = request.args.get('list')
    print("ListingID: ", listingID)
    sellerID = request.args.get('sellerId')
    print("sellerID: ", sellerID)
    bidder = request.args.get('bidder')
    title = request.args.get('title')
    highestBid = request.args.get('cost')

    try:
        # send to bidder
        if 'accept' in request.form:

            error1 = database.updateStatus(listingID, bidder, 'accepted')
            if error1 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            error2 = sendEmail(mail, [bidder], 'accept',
                               username, highestBid, title)
            if error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

        # send to bidder -> if it was the highest bidder send to everyone
        elif 'decline' in request.form:
            error1 = database.updateStatus(listingID, bidder, 'declined')
            if error1 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            # need to update highest bid
            error2 = database.removeMyBid(bidder, listingID)
            if error1 == -1 or error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            error3 = sendEmail(mail, [bidder], 'decline',
                                               username, highestBid, title)
            if error3 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

        # send email to all bidders and seller
        elif 'confirm' in request.form:
            return redirect(url_for('checkout'))

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

            allBidders.insert(0, username)
            error3 = sendEmail(mail, allBidders, 'deny',
                               sellerID, highestBid, title)
            if error3 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

        # book received now must: send seller the money and change book status
        elif 'received' in request.form:
            # send seller money
            print("inside received")
            # update status
            error1 = database.updateStatus(listingID, username, 'received')
            print('Error1: ', error1)
            if error1 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            # send email to seller
            error2 = sendEmail(mail, [], 'received',
                               sellerID, highestBid, title)
            print('Error2: ', error2)
            if error2 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

             # need automatic refresh
            error3 = checkTransactions(database, username, highestBid)
            print('Error3: ', error3)
            if error3 == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response
            elif error3 == False:
                print('buyer has not sent money')
                # want to add popup
            elif error3 == True:
                print('before send Money')
                error4 = sendMoney(database, sellerID, username, title, highestBid)
                print('after send Money')
                if error4 == -1:
                    print('in send money error')
                    html = render_template('errorPage.html')
                    response = make_response(html)
                    return response
                # else:
                    # pop up with congratulations money has been sent

        # if it's the highest bid need to notify everyone
        # user wants to delete their bid
        deleteBidBuyerID = request.args.get('deleteBidBuyerID')
        deleteBidListingID = request.args.get('deleteBidListingID')
        if deleteBidBuyerID is not None and deleteBidListingID is not None:
            database.removeMyBid(deleteBidBuyerID, deleteBidListingID)

        # user wants to delete their listing
        deleteListingID = request.args.get('deleteListingID')
        if deleteListingID is not None:
            allBidders = database.getAllBids(listingID)
            sendEmail(mail, allBidders, 'removed', username, None, title)
            database.removeListing(deleteListingID)

        # Listings
        listings = database.myListings(username)
        if listings == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

        # bids
        bids = database.myBids(username)
        if listings == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

        # purchases
        purchases = database.myPurchases(username)
        if purchases == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

        # books sold
        soldBooks = database.mySoldBooks(username)
        if soldBooks == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    except Exception as e:
        print("Error: " + str(e), file=stderr)
        html = render_template('errorPage.html')
        response = make_response(html)
        return response

    html = render_template('profilePage.html', username=username, listings=listings,
                           purchases=purchases, bids=bids, soldBooks=soldBooks)
    response = make_response(html)
    return response


# ----------------------------------------------------------------------


@app.route('/aboutUs', methods=['GET'])
def aboutUsTemplate():
    username = CASClient().authenticate()
    username = username.strip()
    #client_token = generate_client_token()

    html = render_template(
        'aboutUs.html', username=username)  # client_token=client_token,

    response = make_response(html)
    return response


# ----------------------------------------------------------------------
@app.route('/autoComplete', methods=['GET'])
def autoComplete():
    dropDown = request.args.get('searchType')
    query = request.args.get('query')

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

    try:
        results = database.search(searchType, query, 0, "newest")
        if results == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response
    except Exception as e:
        print("Error: " + str(e), file=stderr)
        html = render_template('errorPage.html')
        response = make_response(html)
        return response

    # make the list of possible autocomplete
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
    username = username.strip()
    title = request.args.get('title')
    cost = request.args.get('cost')
    listing = request.args.get('list')
    sellerId = request.args.get('sellerId')
    buyNow = request.args.get('buyNow')
    print('buyNow: ', buyNow)
    indicator = 0
    # buyer submits venmo -> make request
    # buyer presses recieved -> check of they sent money(venmouserName, amount, Book title,)
    # might be a problem if buy the same book title from same seller -> need listing ID
    # sens money

    # Make sure buyers only returns 1, if it doensnt send pop up with an error
    # connect recieved to send money to seller or throw popup
    # connect recieved button to trigger checking if buyer sent money, if didnt sent money, email buyer and seller?

    venmoUsername = request.form.get('username')
    if venmoUsername != None:
        # venmoUsername = venmoUsername.strip()
        indicator = 1
        print('about to send request')
        error = sendRequest(database, venmoUsername, username,
                            cost, title, sellerId, listing)
        print('sent request')
        if error == -1:
            print('in send request error')
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

        if buyNow == 'yes':
            print('about to buyNow')
            bidders = database.buyNow(username, listing, cost)
            print('after buyNow')
            if bidders == -1:
                print('in buyNow error')
                html = render_template('errorPage.html')
                response = make_response(html)
                return response
        else:
            print('before updateStatus')
            bidders = database.updateStatus(listing, username, 'confirmed')
            print('after updateStatus')
            if bidders == -1:
                print('in updateStatus error')
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

        bidders.insert(0, username)
        # later need to distinguish between confirm and purchase so can delete bids
        error2 = sendEmail(mail, bidders, 'confirm', sellerId, cost, title)
        if error2 == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    html = render_template('checkout.html', username=username, indicator=indicator,
                           title=title, cost=cost, sellerId=sellerId, list=listing, buyNow=buyNow)
    response = make_response(html)

    return response


# ----------------------------------------------------------------------
@app.route('/congratsPage', methods=['GET', 'POST'])
def congratsPage():
    username = CASClient().authenticate()
    username = username.strip()
    msg = ""
    msg1 = ""
    results = []

    # profile page: accepting a bid on your listing; confirming your bid to purchase book
    # Congrats you have accepted a bid, now we just need bidder to confirm
    # Congrats you and the seller have agreed on purchase, proceed to checkout

    # bid update
    if request.args.get('bookid'):
        buyerID = username
        buyNow = request.args.get('buyNow')
        uniqueId = request.args.get('bookid')
        try:
            # users are routed straight to checkout now, so this case does not happen
            if buyNow is not None:
                results = database.getDescription(uniqueId)
                if results == -1:
                    html = render_template('errorPage.html')
                    response = make_response(html)
                    return response
                for result in results:
                    book = result

                type1 = 0
                database.buyNow(buyerID, uniqueId, buyNow)
                if results == -1:
                    html = render_template('errorPage.html')
                    response = make_response(html)
                    return response
                msg += "You have successfully placed your bid, now we are just waiting on the sellers confirmation!  "
                msg1 += "Here is information regarding your purchase "
            else:
                type1 = 1
                bid = request.form.get('bid')
                venmoUsername = request.form.get('venmoUsername')
                database.addBid(buyerID, uniqueId, bid)
                if results == -1:
                    html = render_template('errorPage.html')
                    response = make_response(html)
                    return response
                msg += "You have successfully placed your bid, now we are just waiting on the sellers confirmation!  "
                msg1 += "Here is information regarding your bid: "

                results = database.getDescription(uniqueId)
                if results == -1:
                    html = render_template('errorPage.html')
                    response = make_response(html)
                    return response

                for result in results:
                    book = result

        except Exception as e:
            print("Error: " + str(e), file=stderr)
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    elif request.method == 'POST':
        type1 = 3
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        minprice = request.form.get('minPrice')
        buynow = request.form.get('buyNow')
        # need case were username is wrong
        venmoUsername = request.form.get('venmoUsername')
        print("venmoUsername: ", venmoUsername)
        transaction = database.getTransaction(username)
        print("Transaction: ", transaction)
        if transaction == None:
            error = database.addTransaction(venmoUsername, username)
            if error == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response
        elif transaction == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

        image1 = request.files.get('image1')
        image2 = request.files.get('image2')
        image3 = request.files.get('image3')
        # authors as a list; coursename vs coursenumber
        author = request.form.get('author')
        crscode = request.form.get('crscode')
        if crscode is None or crscode == '' or crscode.strip(' ') is None or crscode.strip(' ') == '':
            crscode = "N/A"
        crstitle = request.form.get('crstitle')
        if crstitle is None or crstitle == '' or crstitle.strip(' ') is None or crstitle.strip(' ') == '':
            crstitle = "N/A"
        condition = request.form.get('bookCondition')
        time = datetime.now()
        listTime = time.strftime("%m:%d:%Y:%H:%M:%S")

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
            if results == -1:
                html = render_template('errorPage.html')
                response = make_response(html)
                return response

            book = {
                "title": title,
                "authors": author,
                "minPrice": minprice,
                "sellerId": username,
                "buyNow": buynow,
                "condition": condition
            }

            msg += "You have successfully created a listing! It won't be long until the bids start rolling in!  "
            msg1 += "Here is the information regarding your listing:"
        except Exception as e:
            print("Error: " + str(e), file=stderr)
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    html = render_template('congratsPage.html', username=username, msg=msg, msg1=msg1,
                           book=book, type1=type1)
    response = make_response(html)

    return response

# ----------------------------------------------------------------------


@app.route('/helpBuyer', methods=['GET'])
def helpBuyerTemplate():
    username = CASClient().authenticate()
    username = username.strip()
    #client_token = generate_client_token()

    html = render_template(
        'helpBuyer.html', username=username)  # client_token=client_token,

    response = make_response(html)
    return response
# ----------------------------------------------------------------------


@app.route('/helpSeller', methods=['GET'])
def helpSellerTemplate():
    username = CASClient().authenticate()
    username = username.strip()
    #client_token = generate_client_token()

    html = render_template(
        'helpSeller.html', username=username)  # client_token=client_token,

    response = make_response(html)
    return response
# ----------------------------------------------------------------------


@app.route('/contactUs', methods=['GET'])
def contactUsTemplate():
    username = CASClient().authenticate()
    username = username.strip()

    html = render_template('contactUs.html', username=username)

    response = make_response(html)
    return response

# ----------------------------------------------------------------------


@app.route('/privacyPolicy', methods=['GET'])
def privacyPolicyTemplate():
    username = CASClient().authenticate()
    username = username.strip()

    html = render_template('privacyPolicy.html', username=username)

    response = make_response(html)
    return response

# -----------------------------------------------------------------------

@app.route('/sellerListings', methods=['GET'])
def sellerListingsTemplate():
    username = CASClient().authenticate()
    username = username.strip()

    sellerID = request.args.get('sellerID')
    sortBy = request.args.get('sortBy')

    if sellerID is None and sortBy is not None:
        sellerID = request.cookies.get('sellerID')

    if sortBy is None:
        sortBy = "newest"

    results = database.sellerListings(sellerID, sortBy)

    if results == -1:
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    images = []
    # Accessing images
    i = 0
    for dict in results:
        if dict["images"]:
            image = dict["images"]
            images.append(image[0].url)
            dict["images"] = i
            i += 1

        else:
            images.append(
                "http://res.cloudinary.com/dijpr9qcs/image/upload/yah8siamtbmtg5wtnsdv.png")
            dict["images"] = i
            i += 1

    html = render_template('sellerListings.html', username=username, sellerID=sellerID, results=results, sortBy=sortBy, images=images)

    response = make_response(html)
    if sellerID is not None:
        response.set_cookie('sellerID', sellerID)
    return response

#------------------------------------------------------------------------
# MAKE LOGOUT A DROP DOWN FROM THE TIGER ICON


@app.route('/logout', methods=['GET'])
def logout():
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
