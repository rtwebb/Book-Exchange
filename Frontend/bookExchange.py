#--------------------------------------------------------------------------
# bookExchange.py
# book-exchange flask file, that works as web-frameowkr
# Author: Toussaint
#-----------------------------------------------------------------------

from flask import Flask, request, make_response, redirect, url_for
from flask import render_template

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')

#-----------------------------------------------------------------------
@app.route('/', methods=['GET'])
@app.route('/homePage', methods=['GET'])
def homePageTemplate():

    # include the information that needs to be filled in dependent on the template

    html = render_template('homePage.html')
                          
    response = make_response(html)
    return response


#-----------------------------------------------------------------------
@app.route('/searchResults', methods=['GET'])
def searchResultsTemplate():

    # include the information that needs to be filled in dependent on the template

    html = render_template('searchResults.html')
                          
    response = make_response(html)
    return response


#-----------------------------------------------------------------------

@app.route('/sellersPage', methods=['GET'])
def sellerPageTemplate():

    # include the information that needs to be filled in dependent on the template

    html = render_template('sellerPage.html')
                          
    response = make_response(html)
    return response


#-----------------------------------------------------------------------

@app.route('/buyersPage', methods=['GET'])
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
