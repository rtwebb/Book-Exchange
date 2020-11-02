from queryDatabase import QueryDatabase

test = QueryDatabase()
test.connect()
result = test.auctionBids('vdhopte')
test.disconnect()

for row in result:
    print(row)