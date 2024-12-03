import mysql.connector
import bcrypt

from flask import jsonify

# =======================GLOBAL VARS=======================
ERROR_EMAIL_NOTFOUND = f"EMAIL %s NOT FOUND IN OUR SYSTEM. PLEASE REGISTER OR USE A DIFFERENT EMAIL"


# =======================SQL ACTIONS=======================
#connects to db and returns db obj as future callable
def conn_2_db():
    mydb = mysql.connector.connect(#could potentially make this configurable
        host = "localhost",
        user = "root",
        password = "1234",
        database = "csc430"
    )
    return mydb
#outter vars meant for future functions
mydb = conn_2_db()
cursor = mydb.cursor()

#call to close connection to db
def close_conn_2_db():
    cursor.close()
    mydb.close() 

def pull_product_list():
    QUERY = "select * from product"
    cursor.execute(QUERY)
    result = cursor.fetchall()
    
    for x in result:
        print(result) #debug , comment when finished
        
    return jsonify(result)


    
# ======================= Cart Functions ==========================
#assign user to cart table, try NOT to thread this with other existing carts
def assign_to_cart(users_id):
    
    QUERY = f"insert into cart ({users_id})"
    SEL_QUERY = f"select users_email from users where users_id = {users_id}" #match user email to passed id
    
    users_email = cursor.execute(SEL_QUERY)

    cursor.execute(QUERY)#insert user_id of passed u_id into cart table

    mydb.commit()

#updates the current cart to be the most recently created cart
def current_cart_db_update(users_email):
    
    MOST_RECENT_CART_QUERY = f"""update users
    set current_cart_id = (select max(cart_id) from cart where cart.users_id = users.users_id)
    where users_email = {users_email}
    """

    cursor.execute(MOST_RECENT_CART_QUERY)

# ======================= User & Account Functions ==========================

def hash_password(password):
    salt = bcrypt.gensalt()#generates a salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)# Hashs the password with the salt after converting it into binary
    return hashed_password #returns the now hased password

def create_user(input_name, input_email, input_password):
    # Hash the password
    input_password = hash_password(input_password)

    # SQL Queries
    insert_user_query = """
        INSERT INTO users (users_name, users_email, users_password)
        VALUES (%s, %s, %s);
    """
    
    select_user_id_query = """
        SELECT users_id FROM users WHERE users_email = %s;
    """
    
    create_cart_query = """
        INSERT INTO cart (users_id) VALUES (%s);
    """
    
    update_current_cart_query = """
        UPDATE users 
        SET current_cart_id = (SELECT MAX(cart_id) FROM cart WHERE cart.users_id = users.users_id)
        WHERE users_id = %s;
    """

    try:
        # Start transaction
        cursor.execute("START TRANSACTION;")
        
        # Insert new user and handle duplicate emails
        cursor.execute(insert_user_query, (input_name, input_email, input_password))
        
        # Retrieve the new user's ID
        cursor.execute(select_user_id_query, (input_email,))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError("Account creation failed: EMAIL IN USE. Please login.")
        
        current_users_id = result[0]
        
        # Create a cart for the new user
        cursor.execute(create_cart_query, (current_users_id,))
        
        # Update the user's current cart ID
        cursor.execute(update_current_cart_query, (current_users_id,))
        
        # Commit the transaction
        mydb.commit()

        return current_users_id  # Optionally use this for automatic login
        
    except Exception as e:
        #mydb.rollback()
        print(f"Error: {e}")
        return None


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)#turns the password into binary and then compares it with the hashed password

def u_login(email,password, hashed_password):
    EMAIL_QUERY = f"select users_email from users where users_email = {email} ;"

    try:
        cursor.execute(EMAIL_QUERY)
    except:
        return jsonify(ERROR_EMAIL_NOTFOUND)
    
# ======================= Admin Functionalities ==========================

#adds a x amount of stock to a product - allocated by its id
def add_x_to_product_stock(x,product_id):
    GET_CURR_STOCK_QUERY = f'select stock from product where product_id = {product_id};'
    try:
        cursor.execute(GET_CURR_STOCK_QUERY)
        curr_stock = cursor.fetchone()[0]
    except:
        print("Failed to update value, please double check passed product_id")
    
    updated_stock = curr_stock + x
    QUERY = f'''
select * from product where product_id = {product_id};
update product 
set stock = {updated_stock}
where product_id = {product_id}
'''
    try:
        cursor.execute(QUERY)
    except:
        print("Addition statement failed! Reference database if issue persists")

    return updated_stock
# ======================= Sale Functionalities ==========================

#removes a n amount of stock from a product
def remove_x_from_product_stock():
    return 0

