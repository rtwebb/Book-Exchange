from queryDatabase import QueryDatabase

test = QueryDatabase()
# test.add('353431', 'CCC', ['CCC'], 'CCC101', 'CCC', 'tianaf\n', 'good', 10, 50, '11:14:2020:22:05:42', [])
# test.addBid('vdhopte\n', 'cd68ac82-2978-421f-ad21-6d57939193f6', 23)
# test.addBid('emmandrar\n', 'cd68ac82-2978-421f-ad21-6d57939193f6', 33)
# test.addBid('tianaf\n', 'cd68ac82-2978-421f-ad21-6d57939193f6', 40)
# test.updateStatus('cd68ac82-2978-421f-ad21-6d57939193f6', 'vdhopte\n', 'confirmed')
# test.removeAllBids('cd68ac82-2978-421f-ad21-6d57939193f6')
# test.removeListing('cd68ac82-2978-421f-ad21-6d57939193f6')
# test.removeMyBid('emmandrar\n', 'cd68ac82-2978-421f-ad21-6d57939193f6')



# from sys import argv, stderr, exit
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from database import Base, Books, Authors, Bids, Courses, Listings, Images
# from uuid import uuid4
#
# DATABASE_URI = 'postgres://vjlbayumjwpewg:19bf7b1ddf47645b85ddd2a53327548f856e138ec4104be' \
#                    '1b99df2f432df9f85@ec2-23-23-36-227.compute-1.amazonaws.com:5432/d1ud4l1r0mt58n'
#
# engine = create_engine(DATABASE_URI)
# Session = sessionmaker(bind=engine)
# session = Session()
#
# listing = Listings(uniqueID=uuid4(), sellerID='tianaf', isbn=11111, condition='good',
#                        minPrice=45.00, buyNow=60.00, listTime='16:45')
# bid1 = Bids(buyerID='vdhopte', listingID=listing.uniqueID, bid=55.00, status='pending')
# bid2 = Bids(buyerID='emmandra', listingID=listing.uniqueID, bid=58.00, status='pending')
# listing.bids = [bid1, bid2]
# session.add(listing)
# session.commit()
