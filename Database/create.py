#!/usr/bin/env python

# ------------------------------------------------------------------------------------
# create.py : create the database
# Author: Tiana Fitzgerald
# ------------------------------------------------------------------------------------

from os import path, remove
from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Books, Authors, Bids, Courses, Listings


def main():
    DATABASE_NAME = 'bookexchange.sqlite'

    if len(argv) != 1:
        print('Usage: python create.py', file=stderr)
        exit(1)
    if path.isfile(DATABASE_NAME):
        remove(DATABASE_NAME)

    engine = create_engine('sqlite:///' + DATABASE_NAME)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

    # ------------------------------------------------------------------------------------

    book = Books(isbn=123, title='The Practice of Programming', quantity=500)
    session.add(book)
    book = Books(isbn=234, title='the C Programming Language', quantity=800)
    session.add(book)
    book = Books(isbn=345, title='Algorithm in C', quantity=650)
    session.add(book)
    session.commit()

    # ------------------------------------------------------------------------------------

    author = Authors(isbn=123, author='Kernighan')
    session.add(author)
    author = Authors(isbn=123, author='Pike')
    session.add(author)
    author = Authors(isbn=234, author='Kernighan')
    session.add(author)
    author = Authors(isbn=234, author='Ritchie')
    session.add(author)
    author = Authors(isbn=345, author='Sedgewick')
    session.add(author)
    session.commit()

    # ------------------------------------------------------------------------------------

    course = Courses(isbn=123, course='COS333')
    session.add(course)
    course = Courses(isbn=234, course='COS217')
    session.add(course)
    course = Courses(isbn=345, course='COS217')
    session.add(course)
    session.commit()

    # ------------------------------------------------------------------------------------

    bid = Bids(buyerID='tianaf', sellerID='vedant', isbn=123, bid=19.99)
    session.add(bid)
    bid = Bids(buyerID='emmandra', sellerID='vedant', isbn=123, bid=25.00)
    session.add(bid)
    session.commit()

    # ------------------------------------------------------------------------------------

    listing = Listings(sellerID='vedant', isbn=123, condition='good', minPrice=15.00,
                       buyNow=30.00, listTime='16:45')
    session.add(listing)
    session.commit()


if __name__ == '__main__':
    main()
