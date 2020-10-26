# ---------------------------------------
# Querydatabse

# By: Emmandra, Tiana, Toussaint
# ----------------------------------------

from sys import stderr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Books, Authors, Bids, Courses, Listings, Images


class QueryDatabase:

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

    # def add(self):
    #
    #
    # def remove(self):

    def search(self, signal, query):
        # signal tells me what kind of query it is: book title, isbn, course, etc

        if signal == 1:  # if query is by isbn
            return self._connection.query(Listings).\
                filter(Listings.isbn == query).all()
        elif signal == 2:  # query is a book title
            return self._connection.query(Listings).\
                filter(Listings.isbn == Books.isbn).\
                filter(Books.title.like(query)).all()
        else:  # query is a course
            return self._connection.query(Listings).\
                filter(Listings.isbn == Courses.isbn).\
                filter(Courses.course.like(query)).all()

        # have to figure out all of the search options we will have
