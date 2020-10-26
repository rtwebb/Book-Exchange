# ---------------------------------------
# Querydatabse

# By: Emmandra, Tiana, Toussaint, Vedant
# ----------------------------------------

from sys import stderr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Books, Authors, Bids, Courses, Listings, Images

class querydatabase:

    def __init__(self):
        self._connection = None

    def connect(self):
        DATABASE_URI = 'postgres://vjlbayumjwpewg:19bf7b1ddf47645b85ddd2a53327548' \
                       'f856e138ec4104be1b99df2f432df9f85@ec2-23-23-36-227.compute-' \
                       '1.amazonaws.com:5432/d1ud4l1r0mt58n'
        engine = create_engine(DATABASE_URI)
        Session = sessionmaker(bind=engine)
        self._connection = Session()

    def disconnect(self):
        self._connection = None

    def add(self, isbn, sellerID, condition, minPrice, buyNow, listTime):
        try:
            book = session.query(Books).filter(Books.isbn == isbn).one()
            book.quantity += 1

        except:
            session.rollback()
            print("Listing rolled back")
    
    # def remove(self):

    def search(self, isbn):
        result = []
        for item in self._connection.query(Listings). \
                filter(Listings.isbn == isbn).all():
            result.append(item.sellerID)
        return result
