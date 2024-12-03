from app import app
from modules import functions
# config.py
# Configure MySQL connection
app.config["MYSQL_HOST"] = functions.host  # Replace with your MySQL host
app.config["MYSQL_USER"] = functions.user       # Replace with your MySQL username
app.config["MYSQL_PASSWORD"] = functions.password  # Replace with your MySQL password
app.config["MYSQL_DB"] = functions.database_name  # Replace with your database name
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
class Config:
    DEBUG = True
