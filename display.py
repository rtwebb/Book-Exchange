#!/usr/bin/env python

# ------------------------------------------------------------------------------------
# display.py : display the database
# Author: Tiana Fitzgerald
# ------------------------------------------------------------------------------------

from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Books, Authors, Bids, Listings, Courses, Images


def main():
    DATABASE_URI = 'postgres://vjlbayumjwpewg:19bf7b1ddf47645b85ddd2a53327548f856e138' \
                   'ec4104be1b99df2f432df9f85@ec2-23-23-36-227.compute-1.amazonaws.com:' \
                   '5432/d1ud4l1r0mt58n'

    if len(argv) != 1:
        print('Usage: python display.py', file=stderr)
        exit(1)

    engine = create_engine(DATABASE_URI)
    # DATABASE_NAME = 'postgres://wjtbbfidjdxfep:2bc4bbc50b88443cb242e1959973f11c65996319de0fabad2d480b7f51dc09af@ec2-54-84-98-18.compute-1.amazonaws.com:5432/db01ol8nkv7pc6'
    # engine = create_engine(DATABASE_NAME)
    Session = sessionmaker(bind=engine)
    session = Session()

    print('------------------------------------')
    print('books')
    print('------------------------------------')
    for book in session.query(Books).all():
        print(book.isbn, book.title)

    print('------------------------------------')
    print('authors')
    print('------------------------------------')
    for author in session.query(Authors).all():
        print(author.isbn, author.name)

    print('------------------------------------')
    print('courses')
    print('------------------------------------')
    for course in session.query(Courses).all():
        print(course.courseCode, course.courseTitle)

    print('------------------------------------')
    print('bids')
    print('------------------------------------')
    for bid in session.query(Bids).all():
        print(bid.buyerID, bid.listingID, bid.bid, bid.status)

    print('------------------------------------')
    print('listings')
    print('------------------------------------')
    for list in session.query(Listings).all():
        print(list.uniqueID, list.sellerID, list.condition, list.minPrice,
              list.buyNow, list.highestBid, list.listTime, list.status)

    print('------------------------------------')
    print('images')
    print('------------------------------------')
    for image in session.query(Images).all():
        print(image.listingID, image.url)


if __name__ == '__main__':
    main()
