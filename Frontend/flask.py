#--------------------------------------------------------------------------
# flask.py
# book-exchange flask file, that works as web-frameowkr
# Author: Toussaint
#-----------------------------------------------------------------------

from database import Database
from time import strftime, localtime, asctime
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')

#-----------------------------------------------------------------------
@app.route('/', methods=['Get'])
@app.route('/homePage', methods=['Get'])
def homePageTemplate():

    # include the information that needs to be filled in dependent on the template

    # html = render_template('homePage.html', ) 
                          
    # respone = make_response(html)
    # return response


#-----------------------------------------------------------------------
@app.route('/searchResults', methods=['Get'])
def searchResultsTemplate():

    # include the information that needs to be filled in dependent on the template

    # html = render_template('searchResults.html', ) 
                          
    # respone = make_response(html)
    # return response






#-----------------------------------------------------------------------

@app.route('/sellersPage', methods=['Get'])
def sellerPageTemplate():

    # include the information that needs to be filled in dependent on the template

    # html = render_template('sellerPage.html', ) 
                          
    # respone = make_response(html)
    # return response






#-----------------------------------------------------------------------

@app.route('/buyersPage', methods=['Get'])
def buyerPageTemplate():


    # include the information that needs to be filled in dependent on the template

    # html = render_template('buyerPage.html', ) 
                          
    # respone = make_response(html)
    # return response




#----------------------------------------------------------------------
    
@app.route('/aboutUs', methods=['Get'])
def aboutPageTemplate():

    # include the information that needs to be filled in dependent on the template

    # html = render_template('aboutUs.html', ) 
                          
    # respone = make_response(html)
    # return response
