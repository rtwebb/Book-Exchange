#--------------------------------------------------------------------------
# bookExchange.py
# book-exchange flask file, that works as web-frameowkr
# Author: Toussaint
#-----------------------------------------------------------------------
from sys import stderr, argv
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from queryDatabase import querydatabse
#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='template')

#-----------------------------------------------------------------------
@app.route('/', methods=['GET'])
@app.route('/homePage', methods=['GET'])
def homePageTemplate():

    # need to get recently listed books to show
    # once get object send to homePage
    # each book needs to link to buyerPage with more information
    # set cookies on search query to follow through searchResults and buyerPage
    
    html = render_template('homePage.html')
                          
    response = make_response(html)
    return response


#-----------------------------------------------------------------------
@app.route('/searchResults', methods=['GET'])
def searchResultsTemplate():

    # need to get results based on search query
    # once get object send to searchResults
    # each book needs to link to buyerPage with more information
    # set cookies on search query to follow through searchResults and buyerPage

    isbn = request.args.get('query')
    results = []
    try: 
        database = querydatabse()
        database.connect()
        results = database.search(isbn)
        
    except Exception as e:
        print(argv[0] + ": " + str(e), file=stderr)   
    
    html = render_template('searchResults.html', results=results)
                          
    response = make_response(html)
    return response


#-----------------------------------------------------------------------

@app.route('/sellerPage', methods=['GET'])
def sellerPageTemplate():

    # pulls down information and adds to database if user says yes everything is correct
      # to check if correct use confirmationPage (is this information right?)
         # if yes generates sucess page
         # if no stay go back to sellerPage (with saved information) and they can fix 

    html = render_template('sellerPage.html')
                          
    response = make_response(html)
    return response


#-----------------------------------------------------------------------

@app.route('/buyerPage', methods=['GET'])
def buyerPageTemplate():
    # buyerPage needs link back to home page 
    
    # If user makes a bid
       # check to make sure if they are sure about the amount
          # if it is correct show success page and have a link to go back to homePage
          # if no stay on buyer page 

    html = render_template('buyerPage.html')
                          
    response = make_response(html)
    return response


#----------------------------------------------------------------------
    
@app.route('/profilePage', methods=['GET'])
def profilePageTemplate():

    # query database for the given user
      # get books they are selling
         # if none set object to none, else pass along
      # get books that they have bid on 
         # if none set object to none, else pass along 
    html = render_template('profilePage.html')
                          
    response = make_response(html)
    return response

#----------------------------------------------------------------------
    
@app.route('/aboutUs', methods=['GET'])
def aboutUsTemplate():


    html = render_template('aboutUs.html')
                          
    response = make_response(html)
    return response