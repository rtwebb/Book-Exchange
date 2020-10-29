from queryDatabase import QueryDatabase

test = QueryDatabase()
test.connect()
result = test.homeRecents()

for row in result:
    print(row)