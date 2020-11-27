# --------------------------------------------------------------------------
# bookExchange.py
# book-exchange flask file, that works as web-framework
# Author: Toussaint, Tiana, Emmandra
# -----------------------------------------------------------------------

from sys import stderr, argv
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from flask_mail import Mail
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
        errorCheck(results)

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
        errorCheck(results)

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
            errorCheck(results)
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

    # if check for if uniqueID is none
    # if (uniqueId == None):
    #     return errorMsg('Invalid book ID')

    try:
        results = database.getDescription(uniqueId)
        errorCheck(results)

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
    listingID = request.args.get('list')
    sellerID = request.args.get('sellerId')
    bidder = request.args.get('bidder')
    title = request.args.get('title')
    highestBid = request.args.get('cost')

    try:
        # send to bidder
        if 'accept' in request.form:
            error1 = database.updateStatus(listingID, bidder, 'accepted')
            errorCheck(error1)

            error2 = sendEmail(mail, [bidder], 'accept',
                               username, highestBid, title)
            errorCheck(error2)

        # send to bidder -> if it was the highest bidder send to everyone
        elif 'decline' in request.form:
            error1 = database.updateStatus(listingID, bidder, 'declined')
            errorCheck(error1)

            # need to update highest bid
            error2 = database.removeMyBid(bidder, listingID)
            errorCheck(error2)
            if error2 == 1:
                allBidders = database.getAllBids(listingID)
                errorCheck(allBidders)
                allBidders.insert(0, bidder)
                errorCheck(sendEmail(mail, allBidders, 'removeHighest', username, highestBid, title))

            error3 = sendEmail(mail, [bidder], 'decline',
                               username, highestBid, title)
            errorCheck(error3)

        # send email to all bidders and seller
        elif 'confirm' in request.form:
            return redirect(url_for('checkout'))

        elif 'deny' in request.form:
            error1 = database.updateStatus(listingID, username, 'declined')
            errorCheck(error1)

            error2 = database.removeMyBid(username, listingID)
            errorCheck(error2)

            allBidders = database.getAllBids(listingID)
            errorCheck(allBidders)
            if len(allBidders) < 1:
                error3 = sendEmail(mail, [username], 'deny',
                                   sellerID, highestBid, title)
            else:
                allBidders.insert(0, username)
                error3 = sendEmail(mail, allBidders, 'deny',
                                   sellerID, highestBid, title)

            errorCheck(error3)

        # book received now must: send seller the money and change book status
        elif 'received' in request.form:  # send seller money
            # update status
            error1 = database.updateStatus(listingID, username, 'received')
            errorCheck(error1)

            # send email to seller
            error2 = sendEmail(mail, [], 'received',
                               sellerID, highestBid, title)
            errorCheck(error2)

            # need automatic refresh
            error3 = checkTransactions(database, username, highestBid)
            errorCheck(error3)
            if not error3:
                print('buyer has not sent money')
                # want to add popup
            elif error3:
                error4 = sendMoney(database, sellerID, username, title, highestBid)
                errorCheck(error4)
                # else:
                # pop up with congratulations money has been sent

        # if it's the highest bid need to notify everyone
        # user wants to delete their bid
        deleteBidBuyerID = request.args.get('deleteBidBuyerID')
        deleteBidListingID = request.args.get('deleteBidListingID')
        if deleteBidBuyerID is not None and deleteBidListingID is not None:
            result = database.removeMyBid(deleteBidBuyerID, deleteBidListingID)
            errorCheck(result)
            if result == 1:
                allBidders = database.getAllBids(listingID)
                errorCheck(allBidders)
                allBidders.insert(0, deleteBidBuyerID)
                errorCheck(sendEmail(mail, allBidders, 'removeHighest', sellerID, highestBid, title))

        # user wants to delete their listing
        deleteListingID = request.args.get('deleteListingID')
        if deleteListingID is not None:
            allBidders = database.getAllBids(deleteListingID)
            errorCheck(allBidders)
            if len(allBidders) >= 1:
                result = sendEmail(mail, allBidders, 'removeListing', username, None, title)
                errorCheck(result)

            result = database.removeListing(deleteListingID)
            errorCheck(result)

        # Listings
        listings = database.myListings(username)
        errorCheck(listings)

        # bids
        bids = database.myBids(username)
        errorCheck(bids)

        # purchases
        purchases = database.myPurchases(username)
        errorCheck(purchases)

        # books sold
        soldBooks = database.mySoldBooks(username)
        errorCheck(soldBooks)

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
    # client_token = generate_client_token()

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
        errorCheck(results)
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

    # if query.strip() == '' or query is None:
    # result = []
    # autocomplete = result

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
        errorCheck(error)

        if buyNow == 'yes':
            print('about to buyNow')
            bidders = database.buyNow(username, listing, cost)
            print('after buyNow')
            errorCheck(bidders)
        else:
            print('before updateStatus')
            bidders = database.updateStatus(listing, username, 'confirmed')
            print('after updateStatus')
            errorCheck(bidders)

        bidders.insert(0, username)
        # later need to distinguish between confirm and purchase so can delete bids
        error2 = sendEmail(mail, bidders, 'confirm', sellerId, cost, title)
        errorCheck(error2)

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
    bid = 0

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
                errorCheck(results)

                for result in results:
                    book = result

                type1 = 0
                error = database.buyNow(buyerID, uniqueId, buyNow)
                errorCheck(error)

                msg += "You have successfully placed your bid, now we are just waiting on the sellers confirmation!  "
                msg1 += "Here is information regarding your purchase "
            else:
                type1 = 1
                bid1 = request.form.get('bid')
                bid = ''
                if "." not in bid1:
                    bid += bid1 + ".00"
                elif ".0" in bid1:
                    if ".00" not in bid1:
                        bid = bid1 + "0"
                    else:
                        bid = bid1

                venmoUsername = request.form.get('venmoUsername')
                indicator, results = database.addBid(buyerID, uniqueId, bid)
                errorCheck(indicator)

                msg += "You have successfully placed your bid, now we are just waiting on the sellers confirmation!  "
                msg1 += "Here is information regarding your bid: "

                results1 = database.getDescription(uniqueId)
                errorCheck(results1)

                for result in results1:
                    book = result

                if indicator == 1:  # case where new bid is greater than previous...send email
                    results.insert(0, username)
                    errorCheck(sendEmail(mail, results, 'beatBid', book['sellerId'], book['highestBid'],
                                         book['title']))

        except Exception as e:
            print(argv[0] + str(e), file=stderr)
            html = render_template('errorPage.html')
            response = make_response(html)
            return response

    elif request.method == 'POST':
        type1 = 3
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        minprice1 = request.form.get('minPrice')
        buynow1 = request.form.get('buyNow')
        minprice = ''
        buynow = ''
        if "." not in minprice1:
            minprice += minprice1 + ".00"
        elif ".0" in minprice1:
            if ".00" not in minprice1:
                minprice = minprice1 + "0"
            else:
                minprice = minprice1

        if "." not in buynow1:
            buynow += buynow1 + ".00"
        elif ".0" in buynow1:
            if ".00" not in buynow1:
                buynow = buynow1 + "0"
            else:
                buynow = buynow1

        # need case were username is wrong
        venmoUsername = request.form.get('venmoUsername')
        print("venmoUsername: ", venmoUsername)
        transaction = database.getTransaction(username)
        print("Transaction: ", transaction)
        if transaction == None:
            error = database.addTransaction(venmoUsername, username)
            errorCheck(error)

        errorCheck(transaction)

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

            results = database.add(isbn, title, [author], crscode, crstitle, username, condition,
                         minprice, buynow, listTime, images)
            errorCheck(results)

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
                           book=book, type1=type1, bid=bid)
    response = make_response(html)

    return response


# ----------------------------------------------------------------------


@app.route('/helpBuyer', methods=['GET'])
def helpBuyerTemplate():
    username = CASClient().authenticate()
    username = username.strip()
    # client_token = generate_client_token()

    html = render_template(
        'helpBuyer.html', username=username)  # client_token=client_token,

    response = make_response(html)
    return response


# ----------------------------------------------------------------------


@app.route('/helpSeller', methods=['GET'])
def helpSellerTemplate():
    username = CASClient().authenticate()
    username = username.strip()
    # client_token = generate_client_token()

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
    errorCheck(results)

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

    html = render_template('sellerListings.html', username=username, sellerID=sellerID, results=results, sortBy=sortBy,
                           images=images)

    response = make_response(html)
    if sellerID is not None:
        response.set_cookie('sellerID', sellerID)
    return response


# ------------------------------------------------------------------------
def errorCheck(error):
    if error == -1:
        html = render_template('errorPage.html')
        response = make_response(html)
        return response
    else:
        return


# ------------------------------------------------------------------------
# MAKE LOGOUT A DROP DOWN FROM THE TIGER ICON


@app.route('/logout', methods=['GET'])
def logout():
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
