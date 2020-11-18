#!/usr/bin/env python

# ------------------------------------------------------------------------------------
# database.py : the database schema
# Author: Tiana Fitzgerald
# ------------------------------------------------------------------------------------

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Books(Base):
    __tablename__ = 'books'
    isbn = Column(String, primary_key=True)
    title = Column(String)
    quantity = Column(Integer)
    authors = relationship('Authors', back_populates='books', cascade='all, delete-orphan')


class Authors(Base):
    __tablename__ = 'authors'
    isbn = Column(String, ForeignKey('books.isbn'), primary_key=True)
    name = Column(String, primary_key=True)
    books = relationship('Books', back_populates='authors')


class Courses(Base):
    __tablename__ = 'courses'
    isbn = Column(String, primary_key=True)
    courseCode = Column(String, primary_key=True)
    courseTitle = Column(String)


class Bids(Base):
    __tablename__ = 'bids'
    buyerID = Column(String, primary_key=True)
    listingID = Column(String, ForeignKey('listings.uniqueID'), primary_key=True)
    bid = Column(Float)  # pending, accepted, declined, confirmed, denied, received
    status = Column(String)


class Listings(Base):
    __tablename__ = 'listings'
    uniqueID = Column(String, primary_key=True)
    sellerID = Column(String)
    isbn = Column(String)
    condition = Column(String)
    minPrice = Column(Float)
    buyNow = Column(Float)
    listTime = Column(String)
    highestBid = Column(Float)
    status = Column(String)  # open, closed, purchased, received
    images = relationship('Images', cascade='all, delete-orphan')
    bids = relationship('Bids', cascade='all, delete-orphan')


class Images(Base):
    __tablename__ = 'images'
    listingID = Column(String, ForeignKey('listings.uniqueID'), primary_key=True)
    url = Column(String, primary_key=True)
