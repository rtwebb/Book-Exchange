# ---------------------------------------
# queryDatabase.py

# By: Emmandra, Tiana, Toussaint, Vedant
# ----------------------------------------

from sys import stderr, argv
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from database import Base, Books, Authors, Bids, Courses, Listings, Images
from uuid import uuid4
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

DATABASE_URI = 'postgres://vjlbayumjwpewg:19bf7b1ddf47645b85ddd2a53327548' \
               'f856e138ec4104be1b99df2f432df9f85@ec2-23-23-36-227.compute-' \
               '1.amazonaws.com:5432/d1ud4l1r0mt58n'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()


class QueryDatabase:

    def __init__(self):
        self._engine = engine
        self._connection = session

    # ----------------------------------------------------------------------------------

    # def connect(self):
    #
    #     self._connection = Session()
    #
    # # ----------------------------------------------------------------------------------
    #
    # def disconnect(self):
    #     self._connection.close()

    # ----------------------------------------------------------------------------------

    # Function currently takes a URL but flask is passing through a file
    def add(self, isbn, title, authors, coursenum, coursename,
            sellerID, condition, minPrice, buyNow, listTime, urls):

        try:
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
                imagelist.append(Images(listingID=listing.uniqueID, url=url))
            listing.images = imagelist
            self._connection.add(listing)
            self._connection.commit()

            return 0

        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # -----------------------------------------------------------------------------

    def removeBids(self, uniqueID):
        try:
            bids = self._connection.query(Bids).\
                filter(Bids.listingID == uniqueID).\
                filter(Bids.status != 'accepted').all()
            for bid in bids:
                self._connecton.delete(bid)

            self._connection.commit()
            return 0

        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    def removeListing(self, uniqueID):
        try:
            results = self._connection.query(Listings, Books, Courses).\
                filter(Listings.uniqueID == uniqueID).\
                filter(Listings.isbn == Books.isbn).\
                filter(Books.isbn == Courses.isbn).all()
            for listing, book, course in results:
                self._connection.delete(listing)
                if book.quantity - 1 == 0:
                    self._connection.delete(book)
                    self._connection.delete(course)

            self._connection.commit()
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    def search(self, signal, query):
        try:
            # signal tells me what kind of query it is: book title, isbn, course, etc
            result = []
            newQuery = query.replace("%", "\\%")
            newQuery = newQuery.replace("_", "\\_")
            newQuery = '%' + newQuery.lower() + '%'
            print(newQuery)
            if signal == 1:  # if query is by isbn
                found = self._connection.query(Books, Courses, Listings). \
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
                result.append((book.isbn, book.title, course.coursenum, course.coursename, listing.minPrice, listing.images,
                               listing.uniqueID))
            return result
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    def homeRecents(self):
        try:
            result = []
            found = self._connection.query(Books, Courses, Listings). \
                filter(Listings.isbn == Books.isbn). \
                filter(Listings.isbn == Courses.isbn). \
                order_by(Listings.listTime).all()
            for book, course, listing in found:
                result.append((book.isbn, book.title, course.coursenum, course.coursename, listing.minPrice, listing.images,
                               listing.uniqueID))
            return result
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    def bidsOnMyListings(self, query):
        try:
            result = []
            found = self._connection.query(Books, Courses, Bids). \
                filter(Listings.sellerID.ilike(query)). \
                filter(Listings.uniqueID == Bids.listingID). \
                filter(Books.isbn == Listings.isbn). \
                filter(Listings.isbn == Courses.isbn).\
                filter(Bids.bid == Listings.highestBid).all()
            for book, course, bid in found:
                result.append((book.title, course.coursenum, bid.buyerID,
                               bid.bid, bid.status, bid.listingID))
            return result
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    def updateStatus(self, listingID, buyerID, newStatus):
        try:
            found = self._connection.query(Bids). \
                filter(Bids.buyerID == buyerID). \
                filter(Bids.listingID == listingID). \
                one()
            found.status = newStatus
            self._connection.commit()
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    def myPurchases(self, query):
        try:
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
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    def myBids(self, query):
        try:
            result = []
            found = self._connection.query(Bids, Books, Courses, Listings). \
                filter(Bids.buyerID.contains(query)). \
                filter(Listings.uniqueID == Bids.listingID). \
                filter(Books.isbn == Listings.isbn). \
                filter(Courses.isbn == Books.isbn). \
                all()
            for bid, book, course, listing in found:
                result.append((book.title, course.coursenum, course.coursename, listing.sellerID, bid.bid,
                               bid.status))
            return result
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    def imageToURL(self, image):
        try:
            cloudinary.config(
                cloud_name="dijpr9qcs",
                api_key="867126563973785",
                api_secret="tvtXgGn_OL2RzA1YxScf3nwxpPE"
            )
            DEFAULT_TAG = "python_sample_basic"

            print("--- Uploading image file")
            response = upload(image, tags=DEFAULT_TAG)
            url, options = cloudinary_url(
                response['public_id'],
                format=response['format'],
            )
            return url
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    def getDescription(self, uniqueID):
        try:
            result = []
            found = self._connection.query(Listings, Books, Courses). \
                filter(Listings.uniqueID == uniqueID). \
                filter(Books.isbn == Listings.isbn). \
                filter(Courses.isbn == Listings.isbn).all()
            for listing, book, course in found:
                result.append((listing.sellerID, listing.isbn, listing.condition, listing.minPrice,
                               listing.buyNow, listing.listTime, listing.images, book.title,
                               book.authors[0].name, course.coursenum, course.coursename, listing.uniqueID,
                               listing.highestBid))
            return result
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    def addBid(self, buyerID, listingID, bid):
        try:
            found = self._connection.query(Listings).\
                filter(Listings.uniqueID == listingID).one()
            if bid > found.highestBid:
                found.highestBid = bid
                self._connection.commit()
            newBid = Bids(buyerID=buyerID, listingID=listingID, bid=bid, status='pending')
            self._connection.add(newBid)
            self._connection.commit()
            return 0
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1