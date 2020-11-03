# ---------------------------------------
# QueryDatabase

# By: Emmandra, Tiana, Toussaint, Vedant
# ----------------------------------------

from sys import stderr
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from database import Base, Books, Authors, Bids, Courses, Listings, Images
from uuid import uuid4
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url


class QueryDatabase:

    def __init__(self):
        self._connection = None

    # ----------------------------------------------------------------------------------

    def connect(self):
        DATABASE_URI = 'postgres://vjlbayumjwpewg:19bf7b1ddf47645b85ddd2a53327548' \
                       'f856e138ec4104be1b99df2f432df9f85@ec2-23-23-36-227.compute-' \
                       '1.amazonaws.com:5432/d1ud4l1r0mt58n'
        engine = create_engine(DATABASE_URI)
        Session = sessionmaker(bind=engine)
        self._connection = Session()

    # ----------------------------------------------------------------------------------

    def disconnect(self):
        self._connection = None

    # ----------------------------------------------------------------------------------

    # Function currently takes a URL but flask is passing through a file
    def add(self, isbn, title, authors, coursenum, coursename,
            sellerID, condition, minPrice, buyNow, listTime, urls):
        
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

            course = Courses(isbn=isbn, coursenum=coursenum, coursename=coursename)
            self._connection.add(course)
            self._connection.commit()

        listing = Listings(uniqueID=uuid4(), sellerID=sellerID, isbn=isbn,
                           condition=condition, minPrice=minPrice,
                           buyNow=buyNow, listTime=listTime)
        imagelist = []
        for url in urls:
            print('add url', url)
            imagelist.append(Images(listingID=listing.uniqueID, url=url))
        listing.images = imagelist

        self._connection.add(listing)
        self._connection.commit()

    # -----------------------------------------------------------------------------

    def remove(self, isbn, uniqueID):

        # Deleting from Listings Table
        listObj = Listings.query.filter(Listings.uniqueID == uniqueID)
        # listObj = seld._connection.query(Listings).filter(Listings.isbn==isbn) .\
        # filter(Listings.sellerID == sellerID)
        self._connection.delete(listObj)

        # Deleting from Images Table
        imgObj = Images.query.filter(Images.listingID == uniqueID)
        # imgObj = self._connection.query(Images).filter(Images.isbn==isbn) .\
        # filter(Images.sellerID == sellerID)
        self._connecton.delete(imgObj)

        # Deleting from Bids Table
        bidObj = Bids.query.filter(Bids.listingID == uniqueID)
        # bidObj = self._connection.query(Bids).filter(Bids.isbn==isbn) .\
        # filter(Bids.sellerID == sellerID)
        self._connecton.delete(bidObj)

        # Deleting from Books Table & Authors Table if necessary
        bookObj = Books.query.filter(Books.isbn == isbn)
        # bookObj = self._connection.query(Books).filter(Books.isbn==isbn)
        if bookObj.quantity > 1:
            num = Books.query.filter(Books.isbn == isbn).update({Books.quantity: Books.quantity - 1})
            # bookObj.quantity -= 1

        # the last book with this isbn was so delete the row
        else:

            authObj = Authors.query.filter(Authors.isbn == isbn)
            # authObj = self._connection.query(Authors).filter(Authors.isbn==isbn)
            courseObj = Courses.query.filter(Courses.isbn == isbn)
            # courseObj = self._connection.query(Courses).filter(Courses.isbn==isbn)
            self._connection.delete(authObj)
            self._connection.delete(courseObj)
            self._connection.delete(bookObj)

        

        self._connection.commit()

    # ----------------------------------------------------------------------------------

    def search(self, signal, query):
        # signal tells me what kind of query it is: book title, isbn, course, etc
        result = []
        newQuery = query.replace("%", "\\%")
        newQuery = newQuery.replace("_", "\\_")
        newQuery = '%' + newQuery.lower() + '%'
        print(newQuery)
        if signal == 1:  # if query is by isbn
            found = self._connection.query(Books, Courses, Listings).\
                filter(Courses.isbn == Listings.isbn). \
                filter(Books.isbn == Listings.isbn). \
                filter(Listings.isbn.ilike(newQuery, escape='\\')). \
                order_by(Listings.listTime).all()
        elif signal == 2:  # query is a book title
            found = self._connection.query(Books, Courses, Listings). \
                filter(Listings.isbn == Books.isbn). \
                filter(Books.title.ilike(newQuery, escape='\\')). \
                filter(Courses.isbn == Books.isbn). \
                order_by(Listings.listTime).all()
        elif signal == 3:  # query is a coursenum
            found = self._connection.query(Books, Courses, Listings). \
                filter(Listings.isbn == Courses.isbn). \
                filter(Courses.coursenum.ilike(newQuery, escape='\\')). \
                filter(Books.isbn == Courses.isbn). \
                order_by(Listings.listTime).all()
        else:  # search by course title
            found = self._connection.query(Books, Courses, Listings). \
                filter(Listings.isbn == Books.isbn). \
                filter(Books.isbn == Courses.isbn). \
                filter(Courses.coursename.ilike(newQuery, escape='\\')). \
                order_by(Listings.listTime).all()
        for book, course, listing in found:
            result.append((book.title, course.coursenum, course.coursename, listing.minPrice, listing.images))
        return result

    # ----------------------------------------------------------------------------------

    def homeRecents(self):
        result = []
        found = self._connection.query(Books, Courses, Listings). \
            filter(Listings.isbn == Books.isbn). \
            filter(Listings.isbn == Courses.isbn). \
            order_by(Listings.listTime).all()
        for book, course, listing in found:
            result.append((book.title, course.coursenum, course.coursename, listing.minPrice, listing.images))
        return result

    # ----------------------------------------------------------------------------------

    def bidsOnMyListings(self, query):
        result = []
        found = self._connection.query(Books, Courses, Bids). \
            filter(Listings.sellerID.ilike(query)). \
            filter(Listings.uniqueID == Bids.listingID). \
            filter(Books.isbn == Listings.isbn). \
            filter(Listings.isbn == Courses.isbn).all()
        for book, course, bid in found:
            result.append((book.title, course.coursenum, bid.buyerID,
                           bid.bid, bid.status, bid.listingID))
        return result

    # ----------------------------------------------------------------------------------

    def updateStatus(self, listingID, buyerID, newStatus):
        print('DONE')
        found = self._connection.query(Bids).\
            filter(Bids.buyerID == buyerID). \
            filter(Bids.listingID == listingID).\
            one()
        found.status = newStatus
        self._connection.commit()

    # ----------------------------------------------------------------------------------

    def myPurchases(self, query):
        result = []
        found = self._connection.query(Books, Courses, Listings, Bids). \
            filter(Bids.buyerID.ilike(query)). \
            filter(Bids.status == 'accepted'). \
            filter(Listings.uniqueID == Bids.listingID). \
            filter(Books.isbn == Listings.isbn). \
            filter(Listings.isbn == Courses.isbn).all()
        for book, course, listing, bid in found:
            result.append((book.title, course.coursenum, course.coursename, listing.minPrice,
                           bid.bid))
        return result

    # ----------------------------------------------------------------------------------

    def myBids(self, query):
        result = []
        found = self._connection.query(Books, Courses, Bids). \
            filter(Bids.buyerID.ilike(query)). \
            filter(Listings.uniqueID == Bids.listingID). \
            filter(Books.isbn == Listings.isbn). \
            filter(Listings.isbn == Courses.isbn).all()
        for book, course, bid in found:
            result.append((book.title, course.coursenum, course.coursename, bid.bid,
                           bid.status))
        return result

    # ----------------------------------------------------------------------------------

    def imageToURL(self, image):
        cloudinary.config(
            cloud_name="dijpr9qcs",
            api_key="867126563973785",
            api_secret="tvtXgGn_OL2RzA1YxScf3nwxpPE"
        )

        DEFAULT_TAG = "python_sample_basic"

        print("--- Upload a local file")
        response = upload(image, tags=DEFAULT_TAG)
        url, options = cloudinary_url(
            response['public_id'],
            format=response['format'],
        )
        print('imagetourl', url)
        return url
