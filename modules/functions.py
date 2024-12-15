import mysql.connector
import bcrypt
import json
import decimal
import os

from flask import jsonify
from MySQLdb.cursors import DictCursor
from modules import api_request
from dotenv import load_dotenv
from flask import jsonify

# =======================GLOBAL VARS & FXs=======================
load_dotenv() #load env vars

ERROR_EMAIL_NOTFOUND = f"EMAIL %s NOT FOUND IN OUR SYSTEM. PLEASE REGISTER OR USE A DIFFERENT EMAIL"

#serialize instance for decimals as they cannot be serialized in/with JSON
def dec_serializer(o):
    if isinstance(o, decimal.Decimal):
        return float(o)
    
# --------- ENV VARS ---------
#mysql host conn
host = os.environ.get('DB_HOST')
user = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')
database_name = os.environ.get('DB_NAME')
#rapidapi key conn
rapidapi_key = os.getenv("x-rapidapi-key")
rapidapi_host = os.getenv("x-rapidapi-host")
print(f"Database Host: {host}, User: {user}, DB Name: {database_name}")

#-----------DB CONN----------
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def pull_products(mysql):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)  # Use dictionary=True for row dicts
        cursor.execute("SELECT * FROM product;")
        result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in pull_products: {e}")
        return jsonify({"error": "Failed to fetch products"}), 500
    finally:
        cursor.close()
        connection.close()

# ======================= Cart Functions ==========================
#assign user to cart table, try NOT to thread this with other existing carts
def assign_to_cart(users_id):
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)

            # Check if user has a cart
            select_query = "SELECT cart_id FROM cart WHERE users_id = %s LIMIT 1"
            cursor.execute(select_query, (users_id,))
            cart_id = cursor.fetchone()
            
            # If a cart exists, return the cart id
            if cart_id:
                return cart_id['cart_id']
            
            # If no cart exists, create a new one for the user
            insert_query = "INSERT INTO cart (users_id) VALUES (%s)"
            cursor.execute(insert_query, (users_id,))
            connection.commit()
            return cursor.lastrowid  # Return the newly created cart ID

    except mysql.connector.Error as e:
        print(f"Database error in assign_to_cart: {e}")
        return None
    except Exception as e:
        print(f"General error in assign_to_cart: {e}")
        return None


#updates the current cart to be the most recently created cart
def current_cart_db_update(users_email):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = connection.cursor(dictionary=True)
    
    MOST_RECENT_CART_QUERY = f"""update users
    set current_cart_id = (select max(cart_id) from cart where cart.users_id = users.users_id)
    where users_email = {users_email}
    """

    cursor.execute(MOST_RECENT_CART_QUERY)

def save_cart(user_id, cart_items):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        print(f"Received user_id: {user_id}, cart_items: {cart_items}")
        
        # Get or create the user's cart ID
        cart_id = assign_to_cart(user_id)
        if not cart_id:
            print("Failed to assign or retrieve cart ID.")
            return jsonify({"success": False, "message": "Failed to assign cart"}), 500

        # Delete old items
        delete_query = "DELETE FROM product_pair WHERE cart_id = %s"
        cursor.execute(delete_query, (cart_id,))
        print(f"Cleared existing items in product_pair for cart_id: {cart_id}")

        # Insert updated items into product_pair
        insert_query = "INSERT INTO product_pair (cart_id, product_id, product_amount) VALUES (%s, %s, %s)"
        for item in cart_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")
            if not product_id or not quantity:
                print("Invalid item data detected:", item)
                continue
            cursor.execute(insert_query, (cart_id, product_id, quantity))
        
        connection.commit()
        print("Cart saved successfully.")
        return jsonify({"success": True, "message": "Cart saved successfully"}), 200

    except Exception as e:
        print(f"Error in save_cart function: {e}")
        return jsonify({"success": False, "message": "Failed to save cart"}), 500
    finally:
        cursor.close()
        connection.close()

def get_cart(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cart_id = assign_to_cart(user_id)
        print(f"Retrieved cart_id for user_id {user_id}: {cart_id}")

        if not cart_id:
            return jsonify([]), 200  # If no cart, return an empty list

        select_query = """
            SELECT 
                product_pair.product_id, 
                product_pair.product_amount, 
                product.price,
                product.product_name AS title
            FROM 
                product_pair 
            JOIN 
                product 
            ON 
                product_pair.product_id = product.product_id 
            WHERE 
                cart_id = %s
        """
        cursor.execute(select_query, (cart_id,))
        result = cursor.fetchall()
        print("Cart items retrieved:", result)

        cart_items = [
            {
                "product_id": row["product_id"],
                "quantity": row["product_amount"],
                "price": row["price"],
                "title": row["title"],
            }
            for row in result
        ]
        return jsonify(cart_items), 200

    except Exception as e:
        print(f"Error retrieving cart: {e}")
        return jsonify({"success": False, "message": "Failed to retrieve cart"}), 500
    finally:
        cursor.close()
        connection.close()

def checkout(user_id, cart_items):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("START TRANSACTION;")        

        for item in cart_items:
            product_id = item.get('product_id')
            quantity = item.get('quantity')

            if not product_id or not quantity:
                print(f"Invalid cart item: {item}")
                raise ValueError("Invalid cart item data.")

            cursor.execute("SELECT stock FROM product WHERE product_id = %s;", (product_id,))
            stock_row = cursor.fetchone()

            if not stock_row:
                print(f"Product ID {product_id} not found in the database.")
                raise ValueError(f"Product ID {product_id} not found.")

            stock = stock_row['stock']
            print(f"Stock for product {product_id}: {stock}")

            if stock >= quantity:
                new_stock = stock - quantity
                cursor.execute("UPDATE product SET stock = %s WHERE product_id = %s;", (new_stock, product_id))
                print(f"Updated stock for product {product_id}: {new_stock}")
            else:
                print(f"Insufficient stock for product {product_id}. Needed: {quantity}, Available: {stock}")
                cursor.execute("ROLLBACK;")
                return jsonify({"success": False, "message": f"Insufficient stock for product ID {product_id}."})

        cursor.execute("COMMIT;")
        print("Checkout transaction committed successfully.")
        return jsonify({"success": True, "message": "Checkout successful!"})

    except Exception as e:
        print(f"Checkout error: {e}")
        cursor.execute("ROLLBACK;")  
        return jsonify({"success": False, "message": "Checkout failed due to an error."})
# ======================= User & Account Functions ==========================

def hash_password(password):
    salt = bcrypt.gensalt()#generates a salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)# Hashs the password with the salt after converting it into binary
    return hashed_password #returns the now hased password

# Function to create a cart and update current cart given a users id.
def create_cart_for_user(users_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)    
    q3 = "INSERT INTO cart (users_id) VALUES (%s);"
    q4 = """
        UPDATE users 
        SET current_cart_id = (SELECT MAX(cart_id) FROM cart WHERE cart.users_id = users.users_id)
        WHERE users_id = %s;
    """
    cursor.execute(q3,(users_id,))
    cursor.execute(q4,(users_id,))
    # DO NOT PUT A COMIT IN FUNCTION. We only create a new cart for a user, when a new user is created, or if the users previous cart has been used for a sale.
    # The comit will occur within those functions!

def create_user(input_name, input_email, input_password):
    # Hash the password
    input_password = hash_password(input_password).decode('utf-8')  # Decode to store as string

    # SQL Queries
    insert_user_query = """
        INSERT INTO users (users_name, users_email, users_password)
        VALUES (%s, %s, %s);
    """
    
    select_user_id_query = """
        SELECT users_id FROM users WHERE users_email = %s;
    """
    
    check_email_query = """
        SELECT COUNT(*) FROM users WHERE users_email = %s;
    """

    try:
        # Create a new connection for this request
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            # Check if the email already exists
            cursor.execute(check_email_query, (input_email,))
            result = cursor.fetchone()
            if result and result['COUNT(*)'] > 0:
                print(f"Error: Email {input_email} already exists.")
                return None  # Email already exists, return None

            print("Starting transaction...")
            cursor.execute("START TRANSACTION;")
            
            # Insert new user
            print(f"Inserting user: {input_name}, {input_email}")
            cursor.execute(insert_user_query, (input_name, input_email, input_password))
            
            # Retrieve the new user's ID
            cursor.execute(select_user_id_query, (input_email,))
            result = cursor.fetchone()
            
            if not result:
                print("Error: Account creation failed, user ID not found.")
                raise ValueError("Account creation failed.")
            
            current_users_id = result['users_id']
            
            # Commit the transaction
            connection.commit()
            print(f"User created successfully with ID: {current_users_id}")

            return current_users_id  # Return the new user ID

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        if 'connection' in locals():
            connection.rollback()  # Rollback if there is an error
        return None
    except Exception as e:
        print(f"General error: {e}")
        return None



def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)#turns the password into binary and then compares it with the hashed password

def u_login(email, password, cursor):
    EMAIL_QUERY = "SELECT users_id, users_name, users_password FROM users WHERE users_email = %s;"

    try:
        cursor.execute(EMAIL_QUERY, (email,))
        result = cursor.fetchone()
        
        if result:
            print("User found:", result)  # Debugging the result from DB
            users_id = result['users_id']
            users_name = result['users_name']
            stored_hashed_password = result['users_password']
            print(f'{users_id}, {users_name}, {stored_hashed_password}' )
            print(f"Stored hashed password: {stored_hashed_password}")  # Debugging the stored password from DB
            print(f"Password (input): {password.encode('utf-8')}")
            print(f"Stored password (encoded): {stored_hashed_password.encode('utf-8')}")
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                return jsonify({
                    "success": True,
                    "message": "Login successful!",
                    "user_id": users_id,
                    "user_name": users_name  
                })
            else:
                return jsonify({"success": False, "message": "Invalid password."})
        else:
            return jsonify({"success": False, "message": f"EMAIL {email} NOT FOUND IN OUR SYSTEM. PLEASE REGISTER OR USE A DIFFERENT EMAIL"})

    except Exception as e:
        print(f"Error in u_login: {e}")
        return jsonify({"success": False, "message": "An error occurred during login."})

#login and register

def authenticate_user(data):
    email = data.get('email')
    password = data.get('password')
    is_registering = data.get('isRegistering', False)  # register flag

    # Get DB connection
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    # Create cursor
    cursor = connection.cursor(dictionary=True)

    if is_registering:
        # Register new user
        name = data.get('name', 'New User')
        print(data)
        user_id = create_user(name, email, password)
        if user_id:
            return jsonify({"success": True, "message": "Registration successful!", "user_id": user_id})
        else:
            return jsonify({"success": False, "message": "Registration failed, email might be in use."})
    else:
        # Log in existing user
        return u_login(email, password, cursor)  # Pass cursor to u_login()


    
# ======================= Admin Functionalities ==========================

#adds a x amount of stock to a product - allocated by its id
def add_x_to_product_stock(x,product_id):
    GET_CURR_STOCK_QUERY = f'select stock from product where product_id = {product_id};'
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True) 
        cursor.execute(GET_CURR_STOCK_QUERY)
        curr_stock = cursor.fetchone()[0]
    except:
        print("Failed to update value, please double check passed product_id")
    
    updated_stock = curr_stock + x
    QUERY = f'''
    update product 
    set stock = {updated_stock}
    where product_id = {product_id}
    '''
    try:
        cursor.execute(QUERY)
    except:
        print("Addition statement failed! Reference database if issue persists")

    return updated_stock

#removes a n amount of stock from a product
def remove_x_from_product_stock(x , product_id):
    GET_CURR_STOCK_QUERY = f'select stock from product where product_id = {product_id};'
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True) 
        cursor.execute(GET_CURR_STOCK_QUERY)
        curr_stock = cursor.fetchone()[0]
    except:
        print("Failed to update value, please double check passed product_id")

    new_stock = curr_stock - x
    QUERY = f'''
    update product 
    set stock = {new_stock}
    where product_id = {product_id}
    '''
    try:
        cursor.execute(QUERY)
    except Exception as e:
        print(e)

#utilizes an api call to get req the passed product name's rating and total amount of reviews
def find_rating(p_name):
    result = api_request.request_product_rating(p_name)
    rating = result["data"]["products"][0]["product_star_rating"]
    no_of_ratings = result["data"]["products"][0]["product_num_ratings"]
    rating_dict = {"rating" : rating , "num_of_ratings" : no_of_ratings}
    return rating_dict

#add a new product to database via passed product parameters. Make sure to use exact amazon name (<=100 char) when creating new product for most optimal ratings
def add_new_product(p_name , p_price , p_stock, category):
    ratings = find_rating(p_name)

    score = ratings["rating"]
    no_of_ratings = ratings["num_of_ratings"]

    INS_INTO_QUERY = f'''
    INSERT INTO product (product_name , price , stock , rating, num_rating, category)
    VALUES (%s , %s , %s , %s , %s , %s)
    '''

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(INS_INTO_QUERY, (p_name, p_price, p_stock, score, no_of_ratings, category))
        connection.commit()
        print("Product insertion successful")
        return True, "Product insertion successful"  # Success case
    except Exception as e:
        print(f"Error inserting product: {e}")
        return False, str(e)  # Error case with the error message
    
def update_product(p_id, new_name, new_price, new_stock):
    UPDATE_QUERY = """
        UPDATE product
        SET product_name = %s, price = %s, stock = %s
        WHERE product_id = %s;
    """
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(UPDATE_QUERY, (new_name, new_price, new_stock, p_id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"success": True, "message": "Product updated"})
    except Exception as e:
        print(f"Error while updating product: {e}")
        return jsonify({"success": False, "message": "Failed to update product"})


# change product price with product id and new price arguments
def price_manip(p_id , new_price):
    QUERY = """
    UPDATE product
    SET price = %d
    WHERE product_id = %i};
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True) 
        cursor.execute(QUERY, (new_price,p_id))
        print("Price update successful!")
    except Exception as e:
        print(e)

# change the name of a product in the database via a reference to its id
def product_name_change(p_id , new_name):
    QUERY ="""
    UPDATE product
    SET product_name = %s
    WHERE product_id = %i;
    """

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)         
        cursor.execute(QUERY, (new_name,p_id))
        print("Name update successful!")
    except Exception as e:
        print(e)