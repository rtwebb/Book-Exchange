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
@app.route('/', methods=['GET'])
@app.route('/homePage', methods=['GET'])
def homePageTemplate():
    username = CASClient().authenticate()

    # need to get recently listed books to show
    results = []
    try:
        results = database.homeRecents()
        errorMsg = ''
    except Exception as e:
        print("Error: " + str(e), file=stderr)
        errorMsg = 'An error occurred please contact email at bottom of the screen'

    # getting images corresponding to each book
    # if no image was uploaded - using a stock photo
    images = []
    for result in results:
        if result[5]:
            images.append(result[5][0].url)
        else:
            images.append(
                "http://res.cloudinary.com/dijpr9qcs/image/upload/bxtyvg9pnuwl11ahkvhg.png")

    uniqueIds = []
    for result in results:
        if result[6]:
            uniqueIds.append(result[6])

    html = render_template('homePage.html', results=results, image=images,
                           errorMsg=errorMsg, uniqueIds=uniqueIds, username=username)
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
    elif dropDown == "crsnum":
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
            uniqueIds = None
        html = render_template('searchResults.html', results=results, searchType=searchType,
                               username=username, query=query, image=images, uniqueIds=uniqueIds)
        response = make_response(html)
        return response
    # proper input (drop-down filled in and query sent)
    else:
        try:
            results = database.search(searchType, query)

            images = []
            for result in results:
                if result[5]:
                    images.append(result[5][0].url)
                else:
                    images.append(
                        "http://res.cloudinary.com/dijpr9qcs/image/upload/bxtyvg9pnuwl11ahkvhg.png")

            uniqueIds = []
            for result in results:
                if result[6]:
                    uniqueIds.append(result[6])

        except Exception as e:
            print(argv[0] + ": " + str(e), file=stderr)

        print('In else statement')
        html = render_template('searchResults.html', results=results,
                               username=username, uniqueIds=uniqueIds, query=query, searchType=searchType,
                               image=images)  # searchKind=searchKind)
        response = make_response(html)
        return response


# -----------------------------------------------------------------------

@app.route('/sellerPage', methods=['GET', 'POST'])
def sellerPageTemplate():
    username = CASClient().authenticate()

    if request.method == 'POST':
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        minprice = request.form.get('minprice')
        buynow = request.form.get('buynow')
        image1 = request.files.get('image1')
        image2 = request.files.get('image2')
        image3 = request.files.get('image3')
        # authors as a list; coursename vs coursenumber
        author = request.form.get('author')
        crsnum = request.form.get('crsnum')
        crsname = request.form.get('crsname')
        condition = request.form.get('bookCondition')
        time = datetime.now()
        listTime = time.strftime("%m:%d:%Y:%H:%M:%S")

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

            database.add(isbn, title, [author], crsnum, crsname, username, condition,
                         minprice, buynow, listTime, images)
        except Exception as e:
            print("Error: " + str(e), file=stderr)

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

    try:
        results = database.getDescription(uniqueId)  # whatever she called it and pass args
        errorMsg = ''
    except Exception as e:
        print("Error: " + str(e), file=stderr)
        errorMsg = 'An error occurred please contact email at bottom of the screen'
    images = []
    for result in results:
        if result[6]:
            images.append(result[6][0].url)
    print(results)

    if request.method == 'POST':
        buyerID = username
        bid = request.form.get('bid')
        print('bid', bid)

        database.addBid(buyerID, uniqueId, bid)  # whatever she called it and pass args
    # buyerPage needs link back to home page
    # If user makes a bid
    # check to make sure if they are sure about the amount
    # if it is correct show success page and have a link to go back to homePage
    # if no stay on buyer page

    html = render_template('buyerPage.html', results=results[0], images=images, listing=uniqueId)
    response = make_response(html)
    return response


# ----------------------------------------------------------------------

@app.route('/profilePage', methods=['GET', 'POST'])
def profilePageTemplate():
    username = CASClient().authenticate()
    bid = request.args.get('list')
    bidder = request.args.get('bidder')

    try:
        if 'accept' in request.form:
            bodyMsg = "Hello, " + bidder + "\n" + "\n" + \
                      "Your TigerBookExchange bid was accepted."
            msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                          recipients=[bidder + '@princeton.edu'], body=bodyMsg)
            mail.send(msg)

            database.updateStatus(bid, bidder, 'accepted')

        elif 'decline' in request.form:
            bodyMsg = "Hello, " + bidder + "\n" + "\n" + \
                      "Your TigerBookExchange bid was declined."
            msg = Message('TigerBookExchange Bid', sender='tigerbookexchange@gmail.com',
                          recipients=[bidder + '@princeton.edu'], body=bodyMsg)
            mail.send(msg)

            database.updateStatus(bid, bidder, 'declined')

        # query database for the given user
        listings = database.bidsOnMyListings(username)
        # use this to reset the forms in mylistings in the profilepage
        # for book in listings:
        # database.updateStatus(book[5], book[2], 'pending')
        purchases = database.myPurchases(username)
        bids = database.myBids(username)

    except Exception as e:
        print("Error: " + str(e), file=stderr)
    # get books they are selling
    # if none set object to none, else pass along
    # get books that they have bid on
    # if none set object to none, else pass along

    # in html page I called the things: listings, purchases, bids
    html = render_template('profilePage.html', user=username, listings=listings,
                           purchases=purchases, bids=bids, username=username)

    response = make_response(html)
    return response


# ----------------------------------------------------------------------

@app.route('/aboutUs', methods=['GET'])
def aboutUsTemplate():
    username = CASClient().authenticate()

    html = render_template('aboutUs2.html', username=username)

    response = make_response(html)
    return response


# ----------------------------------------------------------------------
@app.route('/autoComplete', methods=['GET'])
def autoComplete():
    username = CASClient().authenticate()

    dropDown = request.args.get('dropDown')
    query = request.args.get('query')

    # ask Tiana to return ISBN
    if dropDown == "isbn":
        listIndex = 3
    elif dropDown == "title":
        listIndex = 0
    elif dropDown == "crsnum":
        listIndex = 1
    else:
        listIndex = 2

    results = []
    try:
        results = database.search(searchType, query)
    except Exception as e:
        print("Error: " + str(e), file=stderr)
        errorMsg = 'An error occurred please contact email at bottom of the screen'

    # make the list of possible automcomplete
    if results is not None:
        autoComplete = []
        for result in results:
            autoComplete.append(result[listIndex])

    jsonStr = dumps(autoComplete)
    response = make_response(jsonStr)
    return response


# ----------------------------------------------------------------------
# MAKE LOGOUT A DROP DOWN FROM THE TIGER ICON
@app.route('/logout', methods=['GET'])
def logout():
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
