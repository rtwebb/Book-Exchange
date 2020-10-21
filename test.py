from queryDatabase import Querydatabase

test = Querydatabase()
test.connect()
result = test.search('234')
print(result)