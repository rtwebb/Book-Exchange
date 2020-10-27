# ---------------------------------------
# QueryDatabase

# By: Emmandra, Tiana, Toussaint, Vedant
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

    def add(self, isbn, title, authors, coursenumber, coursetitle,
            sellerID, condition, minPrice, buyNow, listTime, url):
        book = self._connection.query(Books).filter(Books.isbn == isbn).one()
        if book is not None:
            book.quantity += 1
            self._connection.commit()
        
        else:
            book = Books(isbn=isbn, title=title, quantity=1)
            authorlist = []
            for author in authors:
                authorlist.append(Authors(isbn=isbn, name=author))

            book.authors = authorlist
            self._connection.add(book)
            self._connection.commit()

            course = Courses(isbn=isbn, number=coursenumber, title=coursetitle)
            self._connection.add(course)
            self._connection.commit()
            
        listing = Listings(sellerID=sellerID, isbn=isbn, 
                           condition=condition, minPrice=minPrice, 
                           buyNow=buyNow, listTime=listTime)
        self._connection.add(listing)
        self._connection.commit()

        image = Images(sellerID=sellerID, isbn=isbn, url=url)
        self._connection.add(image)
        self._connection.commit()
                
    # def remove(self):

    def search(self, signal, query):
        # signal tells me what kind of query it is: book title, isbn, course, etc
        result = []
        if signal == 1:  # if query is by isbn
            found = self._connection.query(Books, Courses, Listings).\
                filter(Listings.isbn == query).\
                filter(Courses.isbn == Listings.isbn).\
                filter(Books.isbn == Listings.isbn).all()
        elif signal == 2:  # query is a book title
            found = self._connection.query(Books, Courses, Listings).\
                filter(Listings.isbn == Books.isbn).\
                filter(Books.title.like(query)).\
                filter(Courses.isbn == Books.isbn).all()
        elif signal == 3:  # query is a coursenum
            found = self._connection.query(Books, Courses, Listings).\
                filter(Listings.isbn == Courses.isbn).\
                filter(Courses.number.like(query)).\
                filter(Books.isbn == Courses.isbn).all()
        else:  # search by course title
            found = self._connection.query(Books, Courses, Listings).\
                filter(Listings.isbn == Books.isbn).\
                filter(Books.isbn == Courses.isbn).\
                filter(Courses.title.like(query)).all()
        for book, course, listing in found:
            result.append((book.title, course.number, course.title, listing.minPrice))
        return result

        # have to figure out all of the search options we will have
