#!/usr/bin/env python

# ------------------------------------------------------------------------------------
# create.py : create the database
# Author: Tiana Fitzgerald
# ------------------------------------------------------------------------------------

from os import path, remove
from sys import argv, stderr, exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Books, Authors, Bids, Courses, Listings, Images


def main():
    # Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"
    DATABASE_URI = 'postgres+psycopg2://xjcnysxibbvxqk:02a1f9be7858af4c' \
                   '7ca4e22e32ca713c6c1fc8bd2f1d18085946d5e353c32a4a' \
                   '@ec2-18-210-90-1.compute-1.amazonaws.com:5432/dcnlsds3mjdbl4'

    if len(argv) != 1:
        print('Usage: python create.py', file=stderr)
        exit(1)

    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.drop_all(engine)
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

    # ------------------------------------------------------------------------------------

    image = Images(sellerID='vedant', isbn=123,
                   url='http://res.cloudinary.com/dijpr9qcs/image/upload/z3vnl0jbvb41kkhw8vpl.jpg')
    session.add(image)
    session.commit()


if __name__ == '__main__':
    main()
