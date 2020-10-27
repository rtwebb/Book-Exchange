from queryDatabase import QueryDatabase

test = QueryDatabase()
test.connect()
test.add('321', 'This is a Test Title', ['Test McTest Author'], 'TST101', 'Test Course',
         'tianaf', 'good', 30.00, 45.00, '16:15', '')
result = test.homeRecents()

for row in result:
    print(row)