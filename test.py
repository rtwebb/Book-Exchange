from queryDatabase import QueryDatabase

test = QueryDatabase()
test.connect()
result = test.search(5, '123')

for row in result:
    for author in row.authors:
        print(author.name)