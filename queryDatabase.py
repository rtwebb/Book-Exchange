# ---------------------------------------
# queryDatabase.py

# By: Emmandra, Tiana, Toussaint, Vedant
# ----------------------------------------

from sys import stderr, argv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Books, Authors, Bids, Courses, Listings, Images, Transactions
from uuid import uuid4
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

# test stuff
# DATABASE_NAME = "postgres://wjtbbfidjdxfep:2bc4bbc50b88443cb242e1959973f11c65996319de0fabad2d480b7f51dc09af@ec2-54-84-98-18.compute-1.amazonaws.com:5432/db01ol8nkv7pc6"
# engine = create_engine(DATABASE_NAME)

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
            sellerID, condition, minPrice, buyNow, listTime, urls, uniqueID):

        if uniqueID is not None:

            try:

                listing = self._connection.query(Listings). \
                          filter(Listings.uniqueID == uniqueID).one()

                listing.sellerID = sellerID
                self._connection.commit()
                listing.condition = condition.title()
                self._connection.commit()
                listing.minPrice = minPrice
                self._connection.commit()
                listing.buyNow = buyNow
                self._connection.commit()

                images = self._connection.query(Images). \
                        filter(Images.listingID == uniqueID).all()

                for image in images:
                    self._connection.delete(image)
                self._connection.commit()
                
                imagelist = []
                for url in urls:
                    imagelist.append(Images(listingID=listing.uniqueID, url=url))
                listing.images = imagelist
                self._connection.commit()

                book = self._connection.query(Books). \
                    filter(Books.listingID == uniqueID).one()

                book.isbn = isbn
                self._connection.commit()
                book.title = title.title()
                self._connection.commit()

                existingAuthors = self._connection.query(Authors). \
                                 filter(Authors.listingID == uniqueID).all()

                for author in existingAuthors:
                    self._connection.delete(author)
                self._connection.commit()

                authorlist = []
                for author in authors:
                    authorlist.append(Authors(listingID=listing.uniqueID, isbn=isbn, name=author.title()))
                book.authors = authorlist
                self._connection.commit()
                listing.book = [book]
                self._connection.commit()

                course = self._connection.query(Courses). \
                        filter(Courses.listingID == uniqueID).one()

                course.courseCode=courseCode.upper()
                self._connection.commit()
                course.courseTitle = courseTitle.title()
                self._connection.commit()

                listing.course = [course]
                self._connection.commit()

                return 0

            except Exception as e:
                print(argv[0] + ':', e, file=stderr)
                return -1
      
        else:
            try:
                listing = Listings(uniqueID=uuid4(), sellerID=sellerID,
                                   condition=condition.title(), minPrice=minPrice,
                                   buyNow=buyNow, listTime=listTime, highestBid=0, status='open')
                imagelist = []
                for url in urls:
                    imagelist.append(Images(listingID=listing.uniqueID, url=url))
                listing.images = imagelist

                book = Books(listingID=listing.uniqueID, isbn=isbn, title=title.title())
                authorlist = []
                for author in authors:
                    authorlist.append(Authors(listingID=listing.uniqueID, isbn=isbn, name=author.title()))
                book.authors = authorlist
                listing.book = [book]
    
                course = Courses(listingID=listing.uniqueID, courseCode=courseCode.upper(),
                                 courseTitle=courseTitle.title())
                listing.course = [course]
                self._connection.add(listing)
                self._connection.commit()

                return 0

            except Exception as e:
                print(argv[0] + ':', e, file=stderr)
                return -1

    # -----------------------------------------------------------------------------

    # add a bid to the database or update an existing one
    def addBid(self, buyerID, listingID, bid):
        try:
            # update highestBid for this listing
            listing = self._connection.query(Listings). \
                filter(Listings.uniqueID == listingID).one()

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
                # send email to prev highest bidder(s)
                prevHighest = self._connection.query(Bids).filter(Bids.listingID == listingID).\
                    filter(Bids.bid == listing.highestBid).all()
                results = []
                for bid in prevHighest:
                    results.append(bid.buyerID.rstrip())
                listing.highestBid = bid
                self._connection.commit()
                return 1, results
            elif float(bid) < listing.highestBid:
                # check to see if there are other bids on the listing
                found = self._connection.query(Bids). \
                    filter(Bids.listingID == listingID). \
                    order_by(Bids.bid.desc()).first()
                if found:
                    # set highest bid equal to new highest bid
                    listing.highestBid = found.bid
                    self._connection.commit()
            return 0, None
        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1, None

    # ----------------------------------------------------------------------------------
    def addTransaction(self, venmoUsername, username):
        
        try:
            transaction = self._connection.query(Transactions). \
                filter(Transactions.casUsername == username).one_or_none()

            if transaction is not None:
                transaction.venmoUsername = venmoUsername
                self._connection.commit()
                return 0
            else:
                newTrans = Transactions(venmoUsername=venmoUsername, casUsername=username)
                self._connection.add(newTrans)
                self._connection.commit()

                return 0

        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------
    def getTransaction(self, username):
        try:
            transaction = self._connection.query(Transactions). \
                filter(Transactions.casUsername == username).one_or_none()

            # this is wrong
            if transaction is None:
                return None
            else:
                return transaction.venmoUsername

        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # when a listing is bought, remove all bids other than the accepted/confirmed one
    def removeAllBids(self, uniqueID):
        try:
            bids = self._connection.query(Bids). \
                filter(Bids.listingID == uniqueID). \
                filter(Bids.status != 'accepted'). \
                filter(Bids.status != 'confirmed'). \
                filter(Bids.status != 'purchased'). \
                filter(Bids.status != 'received').all()
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
            bid, listing = self._connection.query(Bids, Listings). \
                filter(Bids.listingID == uniqueID). \
                filter(Bids.buyerID.contains(buyerID)). \
                filter(Listings.uniqueID == Bids.listingID).one()

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

                return 1  # indicate that highest bid was removed so email is sent
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
            listing = self._connection.query(Listings). \
                filter(Listings.uniqueID == uniqueID).one()

            self._connection.delete(listing)
            self._connection.commit()

            return 0

        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1

    # ----------------------------------------------------------------------------------

    # searches the database and returns data to show on searchResults
    def search(self, signal, query, requestType, sortBy):
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
                newQuery = newQuery.replace("-", "")
                found = self._connection.query(Listings, Books). \
                    filter(Books.isbn.ilike(newQuery, escape='\\')). \
                    filter(Listings.uniqueID == Books.listingID). \
                    filter(Listings.status != 'closed'). \
                    filter(Listings.status != 'purchased'). \
                    filter(Listings.status != 'received').order_by(Listings.listTime.desc()).all()

            elif signal == 2:  # query is a book title
                found = self._connection.query(Listings, Books). \
                    filter(Books.title.ilike(newQuery, escape='\\')). \
                    filter(Listings.uniqueID == Books.listingID). \
                    filter(Listings.status != 'closed'). \
                    filter(Listings.status != 'purchased'). \
                    filter(Listings.status != 'received').order_by(Listings.listTime.desc()).all()

            elif signal == 3:  # query is a courseCode
                found = self._connection.query(Listings, Courses). \
                    filter(Courses.courseCode.ilike(newQuery, escape='\\')). \
                    filter(Listings.uniqueID == Courses.listingID). \
                    filter(Listings.status != 'closed'). \
                    filter(Listings.status != 'purchased'). \
                    filter(Listings.status != 'received').order_by(Listings.listTime.desc()).all()

            else:  # search by course title
                found = self._connection.query(Listings, Courses). \
                    filter(Courses.courseTitle.ilike(newQuery, escape='\\')). \
                    filter(Listings.uniqueID == Courses.listingID). \
                    filter(Listings.status != 'closed'). \
                    filter(Listings.status != 'purchased'). \
                    filter(Listings.status != 'received').order_by(Listings.listTime.desc()).all()

            if requestType == "1":
                for listing, other in found:
                    result = {
                        "isbn": listing.book[0].isbn,
                        "title": listing.book[0].title,
                        "crscode": listing.course[0].courseCode,
                        "crstitle": listing.course[0].courseTitle,
                        "images": listing.images,
                        "uniqueId": listing.uniqueID,
                        "highestBid": listing.highestBid,
                        "buyNow": listing.buyNow
                    }
                    results.append(result)

                if sortBy == "alphabetical":
                    results = sorted(results, key=lambda d: d["title"])
                elif sortBy == "lotohi":
                    results = sorted(results, key=lambda d: d["highestBid"])
                elif sortBy == "hitolo":
                    results = sorted(results, key=lambda d: d["highestBid"])
                    results = results[::-1]
                elif sortBy == "BNPhitolo":
                    results = sorted(results, key=lambda d: d["buyNow"])
                    results = results[::-1]
                elif sortBy == "BNPlotohi":
                    results = sorted(results, key=lambda d: d["buyNow"])

                return results

            else:
                for listing, other in found:
                    result = {
                        "isbn": listing.book[0].isbn,
                        "title": listing.book[0].title,
                        "crscode": listing.course[0].courseCode,
                        "crstitle": listing.course[0].courseTitle
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
            found = self._connection.query(Listings). \
                filter(Listings.status != 'closed'). \
                filter(Listings.status != 'purchased'). \
                filter(Listings.status != 'received'). \
                order_by(Listings.listTime.desc()).all()
            for listing in found:
                result = {
                    "isbn": listing.book[0].isbn,
                    "title": listing.book[0].title,
                    "crscode": listing.course[0].courseCode,
                    "crstitle": listing.course[0].courseTitle,
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
                allBids = self.getAllBids(listingID)
                check = self.removeAllBids(listingID)
                if check == -1:
                    return -1
                return allBids
            if newStatus == 'received':
                listing = self._connection.query(Listings). \
                    filter(Listings.uniqueID == listingID).one()
                listing.status = 'received'
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

    # provides info for bids on a user's listings
    def myListings(self, query):
        try:
            results = []
            # find listing
            found = self._connection.query(Listings). \
                filter(Listings.sellerID.contains(query)). \
                filter(Listings.status != 'purchased'). \
                filter(Listings.status != 'received').order_by(Listings.listTime.desc()).all()
            for listing in found:
                if len(listing.bids) > 0:  # bids are connected to listing already, so check if there are some
                    for bid in listing.bids:
                        if bid.bid == listing.highestBid:  # only show highest bid(s)
                            result = {
                                "title": listing.book[0].title,
                                "crscode": listing.course[0].courseCode,
                                "buyerId": bid.buyerID,
                                "highestBid": listing.highestBid,
                                "buyNow": listing.buyNow,
                                "status": bid.status,
                                "uniqueId": listing.uniqueID
                            }
                            results.append(result)
                else:  # case of no bids on book
                    result = {
                        "title": listing.book[0].title,
                        "crscode": listing.course[0].courseCode,
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

    # get purchases that a user has made (for profile page)
    def myPurchases(self, query):
        try:
            results = []
            found = self._connection.query(Listings, Bids). \
                filter(Bids.buyerID.ilike(query)). \
                filter(Bids.status.in_(['confirmed', 'purchased', 'received'])). \
                filter(Listings.uniqueID == Bids.listingID).all()
            for listing, bid in found:
                result = {
                    "title": listing.book[0].title,
                    "crscode": listing.course[0].courseCode,
                    "crstitle": listing.course[0].courseTitle,
                    "minPrice": listing.minPrice,
                    "bid": bid.bid,
                    "status": bid.status,
                    "uniqueId": listing.uniqueID,
                    "sellerId": listing.sellerID
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
            found = self._connection.query(Bids, Listings). \
                filter(Bids.buyerID.contains(query)). \
                filter(Listings.uniqueID == Bids.listingID). \
                filter(Bids.status != 'confirmed'). \
                filter(Bids.status != 'purchased'). \
                filter(Bids.status != 'received').all()
            for bid, listing in found:
                result = {
                    "title": listing.book[0].title,
                    "crscode": listing.course[0].courseCode,
                    "crstitle": listing.course[0].courseTitle,
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

    def mySoldBooks(self, query):
        try:
            results = []
            # find listing
            found = self._connection.query(Listings). \
                filter(Listings.sellerID.contains(query)). \
                filter(Listings.status.in_(['purchased', 'received'])).\
                order_by(Listings.listTime.desc()).all()
            for listing in found:
                for bid in listing.bids:
                    result = {
                        "title": listing.book[0].title,
                        "crscode": listing.course[0].courseCode,
                        "buyerId": bid.buyerID,
                        "highestBid": listing.highestBid,
                        "buyNow": listing.buyNow,
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
            listing = self._connection.query(Listings). \
                filter(Listings.uniqueID == uniqueID). \
                filter(Listings.status != 'closed'). \
                filter(Listings.status != 'purchased'). \
                filter(Listings.status != 'received').one()

            transaction = self._connection.query(Transactions). \
                filter(Transactions.casUsername == listing.sellerID).one()

            venmoUsername = transaction.venmoUsername

            result = {
                "uniqueID": uniqueID,
                "title": listing.book[0].title,
                "crscode": listing.course[0].courseCode,
                "crstitle": listing.course[0].courseTitle,
                "sellerId": listing.sellerID,
                "uniqueId": listing.uniqueID,
                "isbn": listing.book[0].isbn,
                "condition": listing.condition,
                "minPrice": listing.minPrice,
                "highestBid": listing.highestBid,
                "buyNow": listing.buyNow,
                "listTime": listing.listTime,
                "images": listing.images,
                "authors": listing.book[0].authors[0].name,
                "listingStatus": listing.status,
                "venmoUsername": venmoUsername
            }
            results.append(result)

            return results
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

    # ------------------------------------------------------------------------------------

    def sellerListings(self, sellerID, sortBy):
        results = []

        try:
            found = self._connection.query(Listings). \
                filter(Listings.sellerID == sellerID). \
                filter(Listings.status != 'closed'). \
                filter(Listings.status != 'purchased'). \
                filter(Listings.status != 'received').order_by(Listings.listTime.desc()).all()

            for listing in found:
                result = {
                    "isbn": listing.book[0].isbn,
                    "title": listing.book[0].title,
                    "crscode": listing.course[0].courseCode,
                    "crstitle": listing.course[0].courseTitle,
                    "images": listing.images,
                    "uniqueId": listing.uniqueID,
                    "highestBid": listing.highestBid,
                    "buyNow": listing.buyNow
                }

                results.append(result)

            if sortBy == "alphabetical":
                results = sorted(results, key=lambda d: d["title"])
            elif sortBy == "lotohi":
                results = sorted(results, key=lambda d: d["highestBid"])
            elif sortBy == "hitolo":
                results = sorted(results, key=lambda d: d["highestBid"])
                results = results[::-1]
            elif sortBy == "BNPhitolo":
                results = sorted(results, key=lambda d: d["buyNow"])
                results = results[::-1]
            elif sortBy == "BNPlotohi":
                results = sorted(results, key=lambda d: d["buyNow"])

            return results

        except Exception as e:
            print(argv[0] + ':', e, file=stderr)
            return -1
