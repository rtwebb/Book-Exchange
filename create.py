#!/usr/bin/env python

# ------------------------------------------------------------------------------------
# create.py : create the database
# Author: Tiana Fitzgerald
# ------------------------------------------------------------------------------------

from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Books, Authors, Bids, Courses, Listings, Images


def main():
    DATABASE_URI = 'postgres://vjlbayumjwpewg:19bf7b1ddf47645b85ddd2a53327548f856e138ec4104be' \
                   '1b99df2f432df9f85@ec2-23-23-36-227.compute-1.amazonaws.com:5432/d1ud4l1r0mt58n'

    if len(argv) != 1:
        print('Usage: python create.py', file=stderr)
        exit(1)

    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # ------------------------------------------------------------------------------------

    book = Books(isbn=123, title='The Practice of Programming', quantity=1)
    author1 = Authors(isbn=123, name='Kernighan')
    author2 = Authors(isbn=123, name='Pike')
    book.authors = [author1, author2]
    session.add(book)
    book = Books(isbn=234, title='the C Programming Language', quantity=1)
    author1 = Authors(isbn=234, name='Kernighan')
    author2 = Authors(isbn=234, name='Ritchie')
    book.authors = [author1, author2]
    session.add(book)
    session.commit()

    # ------------------------------------------------------------------------------------

    course = Courses(isbn=123, number='COS333', title='Advanced Programming Techniques')
    session.add(course)
    course = Courses(isbn=234, number='COS217', title='Introduction to Programming Systems')
    session.add(course)
    session.commit()

    # ------------------------------------------------------------------------------------

    bid = Bids(buyerID='tianaf', sellerID='vedant', isbn=123, bid=19.99)
    session.add(bid)
    bid = Bids(buyerID='emmandra', sellerID='vedant', isbn=123, bid=25.00)
    session.add(bid)
    bid = Bids(buyerID='raph', sellerID='toussaint', isbn=234, bid=25.00)
    session.add(bid)
    session.commit()

    # ------------------------------------------------------------------------------------

    listing = Listings(sellerID='vedant', isbn=123, condition='good', minPrice=15.00,
                       buyNow=30.00, listTime='16:45')
    session.add(listing)
    listing = Listings(sellerID='toussaint', isbn=234, condition='okay', minPrice=20.00,
                       buyNow=50.00, listTime='18:45')
    session.add(listing)
    session.commit()

    # ------------------------------------------------------------------------------------

    image = Images(sellerID='vedant', isbn=123,
                   url='http://res.cloudinary.com/dijpr9qcs/image/upload/z3vnl0jbvb41kkhw8vpl.jpg')
    session.add(image)
    session.commit()


if __name__ == '__main__':
    main()
