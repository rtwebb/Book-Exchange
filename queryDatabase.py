# ---------------------------------------
# queryDatabase.py

# By: Emmandra, Tiana, Toussaint, Vedant
# ----------------------------------------

from sys import stderr, argv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Books, Authors, Bids, Courses, Listings, Images
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

    # -----------------------------------------------------------------------------

    # add a listing to the database (pending)
    def add(self, isbn, title, authors, courseCode, courseTitle,
            sellerID, condition, minPrice, buyNow, listTime, urls):

        try:
            book = self._connection.query(Books).filter(Books.isbn == isbn).one_or_none()
            if book is not None:
                book.quantity += 1
                self._connection.commit()
                course = self._connection.query(Courses). \
                    filter(Courses.isbn == isbn). \
                    filter(Courses.courseCode.contains(courseCode)). \
                    one_or_none()
                if course is None:
                    course = Courses(isbn=isbn, courseCode=courseCode.upper(), courseTitle=courseTitle.title())
                    self._connection.add(course)
                    self._connection.commit()

            else:
                book = Books(isbn=isbn, title=title.title(), quantity=1)
                authorlist = []
                for author in authors:
                    authorlist.append(Authors(isbn=isbn, name=author.title()))
                book.authors = authorlist
                self._connection.add(book)
                self._connection.commit()

                course = Courses(isbn=isbn, courseCode=courseCode.upper(), courseTitle=courseTitle.title())
                self._connection.add(course)
                self._connection.commit()

            listing = Listings(uniqueID=uuid4(), sellerID=sellerID, isbn=isbn,
                               condition=condition.title(), minPrice=minPrice,
                               buyNow=buyNow, listTime=listTime, highestBid=0, status='open')
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

    # when a listing is bought, remove all bids other than the accepted/confirmed one
    def removeAllBids(self, uniqueID):
        try:
            bids = self._connection.query(Bids). \
                filter(Bids.listingID == uniqueID). \
                filter(Bids.status != 'accepted').\
                filter(Bids.status != 'confirmed').all()
            for bid in bids:
                self._connection.delete(bid)
                self._connection.commit()

            return 0

        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # -----------------------------------------------------------------------------

    # if a user wants to remove a bid, use this method
    def removeMyBid(self, buyerID, uniqueID):
        try:
            results = self._connection.query(Bids, Listings). \
                filter(Bids.listingID == uniqueID). \
                filter(Bids.buyerID.contains(buyerID)). \
                filter(Listings.uniqueID == Bids.listingID).all()
            for bid, listing in results:
                # handle case where you are deleting highest bid
                if bid.bid == listing.highestBid:
                    self._connection.delete(bid)
                    self._connection.commit()

                    # check to see if there are other bids on the listing
                    found = self._connection.query(Bids). \
                        filter(Bids.listingID == uniqueID). \
                        order_by(Bids.bid.desc()).first()
                    if found:
                        # set highest bid equal to new highest bid
                        listing.highestBid = found.bid
                        self._connection.commit()
                    else:  # if there no other bids, set highest equal to 0
                        listing.highestBid = 0
                        self._connection.commit()
                else:
                    self._connection.delete(bid)
                    self._connection.commit()
            return 0

        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # if a seller wants to remove a listing, use this method
    def removeListing(self, uniqueID):
        try:
            results = self._connection.query(Listings, Books, Courses). \
                filter(Listings.uniqueID == uniqueID). \
                filter(Books.isbn == Listings.isbn). \
                filter(Courses.isbn == Books.isbn).all()
            for listing, book, course in results:
                self._connection.delete(listing)
                self._connection.commit()
                if book.quantity - 1 == 0:
                    self._connection.delete(book)
                    self._connection.commit()
                    self._connection.delete(course)
                    self._connection.commit()
                else:
                    book.quantity -= 1
                    self._connection.commit()

            return 0
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # searches the database and returns data to show on searchResults
    def search(self, signal, query, requestType):
        try:
            # signal tells me what kind of query it is: book title, isbn, course, etc
            newQuery = query.replace("%", "\\%")
            newQuery = newQuery.replace("_", "\\_")
            if requestType == "1":
                newQuery = '%' + newQuery.lower() + '%'
            else:
                newQuery = newQuery.lower() + '%'
            results = []
            if signal == 1:  # if query is by isbn
                found = self._connection.query(Books, Courses, Listings). \
                    filter(Courses.isbn == Listings.isbn). \
                    filter(Books.isbn == Listings.isbn). \
                    filter(Listings.isbn.ilike(newQuery, escape='\\')). \
                    filter(Listings.status != 'closed'). \
                    filter(Listings.status != 'purchased'). \
                    order_by(Listings.listTime.desc()).all()
            elif signal == 2:  # query is a book title
                found = self._connection.query(Books, Courses, Listings). \
                    filter(Listings.isbn == Books.isbn). \
                    filter(Books.title.ilike(newQuery, escape='\\')). \
                    filter(Courses.isbn == Books.isbn). \
                    filter(Listings.status != 'closed'). \
                    filter(Listings.status != 'purchased'). \
                    order_by(Listings.listTime.desc()).all()
            elif signal == 3:  # query is a courseCode
                found = self._connection.query(Books, Courses, Listings). \
                    filter(Listings.isbn == Courses.isbn). \
                    filter(Courses.courseCode.ilike(newQuery, escape='\\')). \
                    filter(Books.isbn == Courses.isbn). \
                    filter(Listings.status != 'closed'). \
                    filter(Listings.status != 'purchased'). \
                    order_by(Listings.listTime.desc()).all()
            else:  # search by course title
                found = self._connection.query(Books, Courses, Listings). \
                    filter(Listings.isbn == Books.isbn). \
                    filter(Books.isbn == Courses.isbn). \
                    filter(Courses.courseTitle.ilike(newQuery, escape='\\')). \
                    filter(Listings.status != 'closed'). \
                    filter(Listings.status != 'purchased'). \
                    order_by(Listings.listTime.desc()).all()
            if requestType == "1":
                for book, course, listing in found:
                    result = {
                        "isbn": book.isbn,
                        "title": book.title,
                        "crscode": course.courseCode,
                        "crstitle": course.courseTitle,
                        "images": listing.images,
                        "uniqueId": listing.uniqueID,
                        "highestBid": listing.highestBid,
                        "buyNow": listing.buyNow
                    }

                    results.append(result)
                return results
            else:
                for book, course, listing in found:
                    result = {
                        "isbn": book.isbn,
                        "title": book.title,
                        "crscode": course.courseCode,
                        "crstitle": course.courseTitle
                    }
                    results.append(result)
                return results

        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # provides information for recent listings in order of listed time
    def homeRecents(self):
        try:
            results = []
            found = self._connection.query(Books, Courses, Listings). \
                filter(Listings.isbn == Books.isbn). \
                filter(Listings.isbn == Courses.isbn). \
                filter(Listings.status != 'closed'). \
                filter(Listings.status != 'purchased'). \
                order_by(Listings.listTime.desc()).all()
            for book, course, listing in found:
                result = {
                    "isbn": book.isbn,
                    "title": book.title,
                    "crscode": course.courseCode,
                    "crstitle": course.courseTitle,
                    "images": listing.images,
                    "uniqueId": listing.uniqueID,
                    "highestBid": listing.highestBid,
                    "buyNow": listing.buyNow
                }
                results.append(result)

            return results
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # provides info for bids on a user's listings
    def myListings(self, query):
        try:
            results = []
            # find listing
            found = self._connection.query(Listings, Books, Courses). \
                filter(Listings.sellerID.contains(query)). \
                filter(Books.isbn == Listings.isbn). \
                filter(Courses.isbn == Listings.isbn).all()
            for listing, book, course in found:
                if len(listing.bids) > 0:  # bids are connected to listing already, so check if there are some
                    for bid in listing.bids:
                        if bid.bid == listing.highestBid:  # only show highest bid(s)
                            result = {
                                "title": book.title,
                                "crscode": course.courseCode,
                                "buyerId": bid.buyerID,
                                "highestBid": listing.highestBid,
                                "buyNow": listing.buyNow,
                                "status": bid.status,
                                "uniqueId": listing.uniqueID
                            }
                            results.append(result)
                else:  # case of no bids on book
                    result = {
                        "title": book.title,
                        "crscode": course.courseCode,
                        "buyerId": "There are currently no bidders for this listing",
                        "highestBid": 0.0,
                        "buyNow": listing.buyNow,
                        "status": "N/A",
                        "uniqueId": listing.uniqueID
                    }
                    results.append(result)
            return results
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # update bid status [pending, accepted, declined, confirmed]
    def updateStatus(self, listingID, buyerID, newStatus):
        try:
            bid = self._connection.query(Bids). \
                filter(Bids.buyerID.contains(buyerID)). \
                filter(Bids.listingID == listingID).one()
            bid.status = newStatus
            self._connection.commit()
            if newStatus == 'confirmed':
                listing = self._connection.query(Listings). \
                    filter(Listings.uniqueID == listingID).one()
                listing.status = 'purchased'
                self._connection.commit()
            if newStatus == 'accepted':
                listing = self._connection.query(Listings). \
                    filter(Listings.uniqueID == listingID).one()
                listing.status = 'closed'
                self._connection.commit()
            if newStatus == 'declined':
                listing = self._connection.query(Listings). \
                    filter(Listings.uniqueID == listingID).one()
                listing.status = 'open'
                self._connection.commit()

            return 0
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # get purchases that a user has made (for profile page)
    def myPurchases(self, query):
        try:
            results = []
            found = self._connection.query(Books, Courses, Listings, Bids). \
                filter(Bids.buyerID.ilike(query)). \
                filter(Bids.status == 'confirmed'). \
                filter(Listings.uniqueID == Bids.listingID). \
                filter(Books.isbn == Listings.isbn). \
                filter(Listings.isbn == Courses.isbn).all()
            for book, course, listing, bid in found:
                result = {
                    "title": book.title,
                    "crscode": course.courseCode,
                    "crstitle": course.courseTitle,
                    "minPrice": listing.minPrice,
                    "bid": bid.bid
                }
                results.append(result)

            return results
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # get bids that a user has made (for profile page)
    def myBids(self, query):
        try:
            results = []
            found = self._connection.query(Bids, Books, Courses, Listings). \
                filter(Bids.buyerID.contains(query)). \
                filter(Listings.uniqueID == Bids.listingID). \
                filter(Books.isbn == Listings.isbn). \
                filter(Courses.isbn == Books.isbn). \
                filter(Bids.status != 'confirmed').all()
            for bid, book, course, listing in found:
                result = {
                    "title": book.title,
                    "crscode": course.courseCode,
                    "crstitle": course.courseTitle,
                    "sellerId": listing.sellerID,
                    "bid": bid.bid,
                    "status": bid.status,
                    "uniqueId": listing.uniqueID
                }
                results.append(result)

            return results
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # upload given image to cloudinary and return URL
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

    # provide listing details to show on buyerPage
    def getDescription(self, uniqueID):
        try:
            results = []
            found = self._connection.query(Listings, Books, Courses). \
                filter(Listings.uniqueID == uniqueID). \
                filter(Books.isbn == Listings.isbn). \
                filter(Listings.status != 'closed'). \
                filter(Listings.status != 'purchased'). \
                filter(Courses.isbn == Listings.isbn).all()
            for listing, book, course in found:
                result = {
                    "title": book.title,
                    "crscode": course.courseCode,
                    "crstitle": course.courseTitle,
                    "sellerId": listing.sellerID,
                    "uniqueId": listing.uniqueID,
                    "isbn": listing.isbn,
                    "condition": listing.condition,
                    "minPrice": listing.minPrice,
                    "highestBid": listing.highestBid,
                    "buyNow": listing.buyNow,
                    "listTime": listing.listTime,
                    "images": listing.images,
                    "authors": book.authors[0].name
                }
                results.append(result)

            return results
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # add a bid to the database or update an existing one
    def addBid(self, buyerID, listingID, bid):
        try:
            # update highestBid for this listing
            listing = self._connection.query(Listings). \
                filter(Listings.uniqueID == listingID).one_or_none()
            # if buyer already has a bid on that book, update the bid
            foundBid = self._connection.query(Bids). \
                filter(Bids.buyerID.contains(buyerID)). \
                filter(Bids.listingID == listingID).one_or_none()

            if foundBid:
                foundBid.bid = bid
                self._connection.commit()
                foundBid.status = 'pending'
                self._connection.commit()

            # otherwise, create a new bid
            else:
                newBid = Bids(buyerID=buyerID, listingID=listingID, bid=bid, status='pending')
                self._connection.add(newBid)
                self._connection.commit()

            if float(bid) > listing.highestBid:
                listing.highestBid = bid
                self._connection.commit()
            elif float(bid) < listing.highestBid:
                # check to see if there are other bids on the listing
                found = self._connection.query(Bids). \
                    filter(Bids.listingID == listingID). \
                    order_by(Bids.bid.desc()).first()
                if found:
                    # set highest bid equal to new highest bid
                    listing.highestBid = found.bid
                    self._connection.commit()
            return 0
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------
    def buyNow(self, buyerID, listingID, bid):
        try:
            listing = self._connection.query(Listings). \
                filter(Listings.uniqueID == listingID).one()

            listing.status = "purchased"
            self._connection.commit()
            listing.highestBid = bid
            self._connection.commit()
            buyNowPrice = listing.buyNow

            foundBid = self._connection.query(Bids). \
                filter(Bids.buyerID == buyerID). \
                filter(Bids.listingID == listingID).one_or_none()

            if foundBid:
                foundBid.bid = buyNowPrice
                self._connection.commit()
                foundBid.status = 'confirmed'
                self._connection.commit()
            else:
                newBid = Bids(buyerID=buyerID, listingID=listingID, bid=buyNowPrice, status='confirmed')
                self._connection.add(newBid)
                self._connection.commit()

            allBids = self.getAllBids(listingID)
            check = self.removeAllBids(listingID)
            if check == -1:
                return -1

            return allBids

        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------
    def getAllBids(self, listingID):
        try:
            results = []
            found = self._connection.query(Bids).filter(Bids.listingID == listingID).all()
            for bid in found:
                results.append(bid.buyerID.rstrip())
            return results
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1
