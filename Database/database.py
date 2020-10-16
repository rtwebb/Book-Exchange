#!/usr/bin/env python

# ------------------------------------------------------------------------------------
# database.py : the database schema
# Author: Tiana Fitzgerald
# ------------------------------------------------------------------------------------

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()


class Books(Base):
    __tablename__ = 'books'
    isbn = Column(String, primary_key=True)
    title = Column(String)
    quantity = Column(Integer)


class Authors(Base):
    __tablename__ = 'authors'
    isbn = Column(String, primary_key=True)
    author = Column(String, primary_key=True)


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
    image = Column(String)
