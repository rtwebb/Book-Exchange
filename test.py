from queryDatabase import QueryDatabase

test = QueryDatabase()
test.connect()
result = test.search(1, '123')

for row in result:
    print(row.minPrice)