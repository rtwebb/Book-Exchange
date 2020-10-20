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

    
    html = render_template('homePage.html', result=result)
                          
    response = make_response(html)
    return response


#-----------------------------------------------------------------------
@app.route('/searchResults', methods=['GET'])
def searchResultsTemplate():

    isbn = request.get.args('query')
    result = []
    try: 
        database = querydatabse()
        database.connect()
        result = database.search(isbn)
        
    except Exception as e:
        print(argv[0] + ": " + str(e), file=stderr)   
    
    html = render_template('searchResults.html', result=result)
                          
    response = make_response(html)
    return response


#-----------------------------------------------------------------------

@app.route('/sellerPage', methods=['GET'])
def sellerPageTemplate():

    # include the information that needs to be filled in dependent on the template

    html = render_template('sellerPage.html')
                          
    response = make_response(html)
    return response


#-----------------------------------------------------------------------

@app.route('/buyerPage', methods=['GET'])
def buyerPageTemplate():


    # include the information that needs to be filled in dependent on the template

    html = render_template('buyerPage.html')
                          
    response = make_response(html)
    return response


#----------------------------------------------------------------------
    
@app.route('/aboutUs', methods=['GET'])
def aboutPageTemplate():

    # include the information that needs to be filled in dependent on the template

    html = render_template('aboutUs.html')
                          
    response = make_response(html)
    return response
