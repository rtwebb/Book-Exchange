# --------------------------------------------------------------------------
# bookExchange.py
# book-exchange flask file, that works as web-framework
# Author: Toussaint, Tiana
# -----------------------------------------------------------------------
from sys import stderr, argv
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from queryDatabase import QueryDatabase
from datetime import datetime
from CASClient import CASClient

# -----------------------------------------------------------------------

app = Flask(__name__, template_folder='template')

# Do we need this/ how do we use this??????
# Generated by os.urandom(16)
app.secret_key = b'\xcdt\x8dn\xe1\xbdW\x9d[}yJ\xfc\xa3~/'


# -----------------------------------------------------------------------
@app.route('/', methods=['GET'])
@app.route('/homePage', methods=['GET'])
def homePageTemplate():
    username = CASClient().authenticate()

    # need to get recently listed books to show
    result = []
    try:
        database = QueryDatabase()
        database.connect()
        result = database.homeRecents()
        errorMsg = ''
        print(result)
    except Exception as e:
        print("Error: " + str(e), file=stderr)
        errorMsg = 'An error occurred please contact email at bottom of the screen'

    # set cookies on search query to follow through searchResults and buyerPage

    html = render_template('homePage.html', results=result, errorMsg=errorMsg, username=username)
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

    if dropDown == '':
        searchType = 0
    if query == '' or query is None:
        query = ''

    results = []

    # checking for null inputs and not interacting with drop-down
    if searchType == 0 or query == '':
        html = render_template('searchResults.html', results=results, searchType=searchType,
                               username=username)  # searchKind=searchKind)
        response = make_response(html)
        return response
    # proper input (drop-down filled in and query sent)
    else:
        try:
            database = QueryDatabase()
            database.connect()
            results = database.search(searchType, query)
            database.disconnect()

        except Exception as e:
            print(argv[0] + ": " + str(e), file=stderr)

        html = render_template('searchResults.html', results=results, searchType=searchType)  # searchKind=searchKind)
        response = make_response(html)
        return response


# -----------------------------------------------------------------------

@app.route('/sellerPage', methods=['GET'])
def sellerPageTemplate():
    username = CASClient().authenticate()

    isbn = request.args.get('isbn')
    title = request.args.get('title')
    minprice = request.args.get('minprice')
    buynow = request.args.get('buynow')
    # img = request.args.get('image')
    # in html we need to add condition drop down; authors as a list; coursename vs coursenumber
    author = request.args.get('author')
    crsnum = request.args.get('crsnum')
    crsname = request.args.get('crsname')
    dropDown = request.args.get('dropDown')
    time = datetime.now()
    listTime = time.strftime("%H:%M:%S")

    # confirmation JS stuff    

    # passing to database
    try:
        database = QueryDatabase()
        database.connect()
        database.add(isbn, title, [author], crsnum, crsname, username, dropDown,
                     minprice, buynow, listTime, None)
        database.disconnect()
    except Exception as e:
        print("Error: " + str(e), file=stderr)

    # when sending to profile page have a "successful" message display
    html = render_template('sellerPage.html', username=username)

    response = make_response(html)
    return response


# -----------------------------------------------------------------------

@app.route('/buyerPage', methods=['GET'])
def buyerPageTemplate():
    username = CASClient().authenticate()

    # buyerPage needs link back to home page 

    # If user makes a bid
    # check to make sure if they are sure about the amount
    # if it is correct show success page and have a link to go back to homePage
    # if no stay on buyer page

    html = render_template('buyerPage.html', username=username)

    response = make_response(html)
    return response


# ----------------------------------------------------------------------

@app.route('/profilePage', methods=['GET', 'POST'])
def profilePageTemplate():
    username = CASClient().authenticate()
    bid = request.args.get('list')
    bidder = request.args.get('bidder')

    try:
        database = QueryDatabase()
        database.connect()

        if 'accept' in request.form:
            database.updateStatus(bid, bidder, 'accepted')
        elif 'decline' in request.form:
            database.updateStatus(bid, bidder, 'declined')

        # query database for the given user
        listings = database.auctionBids(username)
        database.disconnect()
    except Exception as e:
        print("Error: " + str(e), file=stderr)
    # get books they are selling
    # if none set object to none, else pass along
    # get books that they have bid on
    # if none set object to none, else pass along

    # in html page I called the things: listings, purchases, bids
    html = render_template('profilePage.html', listings=listings, username=username)

    response = make_response(html)
    return response


# ----------------------------------------------------------------------

@app.route('/aboutUs', methods=['GET'])
def aboutUsTemplate():
    username = CASClient().authenticate()

    html = render_template('aboutUs.html', username=username)

    response = make_response(html)
    return response


# ----------------------------------------------------------------------
# MAKE LOGOUT A DROP DOWN FROM THE TIGER ICON
# NEED TO MAKE A LOGOUT BUTTON
@app.route('/logout', methods=['GET'])
def logout():
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
