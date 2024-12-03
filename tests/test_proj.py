from modules import functions
def test_home():
    new_stock = functions.add_x_to_product_stock(2,1)
    print(new_stock)
#def test_lemme_see_the_listofdicts():
#    query = f'select users_id from users;'
#    results = functions.cursor.execute(query)
#    while results is not None:
#        print(results)
#    return results

def test_create_user():
    return functions.create_user("reechard","test123@email.com","99999999")

def pull_user_list():
    results = functions.cursor.execute("select * from users")
    while results is not None:
         print(results)
    assert results
   