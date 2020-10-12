#!/usr/bin/env python

# ------------------------------------------------------------------------------------
# display.py : display the database
# Author: Tiana Fitzgerald
# ------------------------------------------------------------------------------------

from os import path
from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Books, Authors, Bids, Listings, Courses


def main():
    DATABASE_NAME = 'bookexchange.sqlite'

    if len(argv) != 1:
        print('Usage: python display.py', file=stderr)
        exit(1)
    if not path.isfile(DATABASE_NAME):
        print('Database connection failed', file=stderr)
        exit(1)

    engine = create_engine('sqlite:///' + DATABASE_NAME)
    Session = sessionmaker(bind=engine)
    session = Session()

    print('------------------------------------')
    print('books')
    print('------------------------------------')
    for book in session.query(Books).all():
        print(book.isbn, book.title, book.quantity)

    print('------------------------------------')
    print('authors')
    print('------------------------------------')
    for author in session.query(Authors).all():
        print(author.isbn, author.author)

    print('------------------------------------')
    print('courses')
    print('------------------------------------')
    for course in session.query(Courses).all():
        print(course.isbn, course.course)

    print('------------------------------------')
    print('bids')
    print('------------------------------------')
    for bid in session.query(Bids).all():
        print(bid.buyerID, bid.sellerID, bid.isbn, bid.bid)

    print('------------------------------------')
    print('listings')
    print('------------------------------------')
    for list in session.query(Listings).all():
        print(list.sellerID, list.isbn, list.condition, list.minPrice,
              list.buyNow, list.listTime)


if __name__ == '__main__':
    main()
