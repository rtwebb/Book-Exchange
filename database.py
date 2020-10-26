#!/usr/bin/env python

# ------------------------------------------------------------------------------------
# database.py : the database schema
# Author: Tiana Fitzgerald
# ------------------------------------------------------------------------------------

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()
# figure out where to put edition of book


class Books(Base):
    __tablename__ = 'books'
    isbn = Column(String, primary_key=True)
    title = Column(String)
    quantity = Column(Integer)
    authors = relationship('Authors')


class Authors(Base):
    __tablename__ = 'authors'
    isbn = Column(String, ForeignKey('books.isbn'), primary_key=True)
    name = Column(String, primary_key=True)


class Courses(Base):
    __tablename__ = 'courses'
    isbn = Column(String, primary_key=True)
    course = Column(String, primary_key=True)


class Bids(Base):
    __tablename__ = 'bids'
    buyerID = Column(String, primary_key=True)
    sellerID = Column(String, primary_key=True)
    isbn = Column(String, primary_key=True)
    bid = Column(Float)


class Listings(Base):
    __tablename__ = 'listings'
    sellerID = Column(String, primary_key=True)
    isbn = Column(String, primary_key=True)
    condition = Column(String)
    minPrice = Column(Float)
    buyNow = Column(Float)
    listTime = Column(String)


class Images(Base):
    __tablename__ = 'images'
    sellerID = Column(String, primary_key=True)
    isbn = Column(String, primary_key=True)
    url = Column(String)
