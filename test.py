from queryDatabase import QueryDatabase

test = QueryDatabase()
test.connect()
result = test.search(3, 'cos')
test.disconnect()

for row in result:
    print(row)