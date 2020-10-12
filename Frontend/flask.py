#--------------------------------------------------------------------------
# flask.py
# book-exchange flask file, that works as web-frameowkr
# Author: Toussaint
#-----------------------------------------------------------------------

from database import Database
from time import strftime, localtime, asctime
from flask import Flask, request, make_response, redirect, url_for
from templates import headerTemplate, footerTemplate, homePageTemplate
from templates import searchResultsTemplate, sellerPageTemplate,
from templates import buyerPageTemplate, aboutPageTemplate

#-----------------------------------------------------------------------

app = Flask(__name__)

#-----------------------------------------------------------------------

@app.route('/homePage', methods=['Get'])
def homePageTemplate():





#-----------------------------------------------------------------------
@app.route('/searchResults', methods=['Get'])
def searchResultsTemplate():







#-----------------------------------------------------------------------

@app.route('/sellersPage', methods=['Get'])
def sellerPageTemplate():







#-----------------------------------------------------------------------

@app.route('/buyersPage', methods=['Get'])
def buyerPageTemplate():





#----------------------------------------------------------------------
    
@app.route('/aboutUs', methods=['Get'])
def aboutPageTemplate():
