#from sqlalchemy import create_engine

#use this if we are using a pre-populated table

#string vars for engine connection
#DB_NAME = "csc430"
#HOST_CONN = "localhost"
#USERNAME = "root"
#PASSW = "1234"

#ENGINE_STRING = f"mysql+mysqlconnector://{USERNAME}:{PASSW}@{HOST_CONN}/{DB_NAME}"

#this creates a link to the mysql local db, set vars in global above
#engine = create_engine(ENGINE_STRING)

#connection = engine.connect()

# From the default bind key
#class Product(db.Model):
#    __table__ = db.metadata.tables["Product"]

#class Product_Cart(db.Model):
#    __table__ = db.metadata.tables["Cart"]

# From an "auth" bind key
#class User(db.Model):
#    __table__ = db.metadatas["auth"].tables["User"]

#class Product_Cart(db.Model):
#    __table__ = db.metadatas["auth"].tables["Product_Cart"]

#class Sales_History(db.Model):
#    __table__ = db.metadatas["auth"].tables["Sales_History"]