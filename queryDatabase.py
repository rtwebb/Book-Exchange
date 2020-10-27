# ---------------------------------------
# QueryDatabase

# By: Emmandra, Tiana, Toussaint, Vedant
# ----------------------------------------

from sys import stderr
from sqlalchemy import create_engine, update
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
        book = self._connection.query(Books).filter(Books.isbn == isbn).one_or_none()
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
                
    def remove(self, isbn, sellerID):

        #Deleting from Listings Table
        listObj = Listings.query.filter(Listings.isbn==isbn) .\
            filter(Listings.sellerID == sellerID)
        #listObj = seld._connection.query(Listings).filter(Listings.isbn==isbn) .\
            #filter(Listings.sellerID == sellerID)
        self._connection.delete(listObj)

        #Deleting from Images Table
        imgObj = Images.query.filter(Images.isbn==isbn) .\
            filter(Images.sellerID == sellerID)
        #imgObj = self._connection.query(Images).filter(Images.isbn==isbn) .\
            #filter(Images.sellerID == sellerID)
        self._connecton.delete(imgObj)

        #Deleting from Bids Table
        bidObj = Bids.query.filter(Bids.isbn==isbn) .\
            filter(Bids.sellerID == sellerID)
        #bidObj = self._connection.query(Bids).filter(Bids.isbn==isbn) .\
            #filter(Bids.sellerID == sellerID)
        self._connecton.delete(bidObj)

        #Deleting from Books Table & Authors Table if necessary
        bookObj = Books.query.filter(Books.isbn==isbn)
        #bookObj = self._connection.query(Books).filter(Books.isbn==isbn)
        if bookObj.quantity > 1:
            num = Books.query.filter(Books.isbn==isbn).update({Books.quantity : Books.quantity - 1}) 
            #bookObj.quantity -= 1

        #the last book with this isbn was so delete the row
        else:

            authObj = Authors.query.filter(Authors.isbn==isbn)
            #authObj = self._connection.query(Authors).filter(Authors.isbn==isbn)
            courseObj = Courses.query.filter(Courses.isbn==isbn)
            #courseObj = self._connection.query(Courses).filter(Courses.isbn==isbn)
            self._connection.delete(authObj)

        self._connection.delete(bookObj)
            
        self._connection.commit()

    def search(self, signal, query):
        # signal tells me what kind of query it is: book title, isbn, course, etc
        result = []
        if signal == 1:  # if query is by isbn
            found = self._connection.query(Books, Courses, Listings).\
                filter(Listings.isbn == query).\
                filter(Courses.isbn == Listings.isbn).\
                filter(Books.isbn == Listings.isbn).\
                order_by(Listings.listTime).all()
        elif signal == 2:  # query is a book title
            found = self._connection.query(Books, Courses, Listings).\
                filter(Listings.isbn == Books.isbn).\
                filter(Books.title.like(query)).\
                filter(Courses.isbn == Books.isbn).\
                order_by(Listings.listTime).all()
        elif signal == 3:  # query is a coursenum
            found = self._connection.query(Books, Courses, Listings).\
                filter(Listings.isbn == Courses.isbn).\
                filter(Courses.number.like(query)).\
                filter(Books.isbn == Courses.isbn).\
                order_by(Listings.listTime).all()
        else:  # search by course title
            found = self._connection.query(Books, Courses, Listings).\
                filter(Listings.isbn == Books.isbn).\
                filter(Books.isbn == Courses.isbn).\
                filter(Courses.title.like(query)).\
                order_by(Listings.listTime).all()
        for book, course, listing in found:
            result.append((book.title, course.number, course.title, listing.minPrice))
        return result

        # have to figure out all of the search options we will have

    def homeRecents(self):
        result = []
        found = self._connection.query(Books, Courses, Listings).\
            filter(Listings.isbn == Books.isbn).\
            filter(Listings.isbn == Courses.isbn).\
            order_by(Listings.listTime).all()
        for book, course, listing in found:
            result.append((book.title, course.number, course.title, listing.minPrice))
        return result
