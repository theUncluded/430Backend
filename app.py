from flask import Flask, render_template, request, jsonify, redirect
from modules import functions
import pytest

app = Flask(__name__)  
#Configuration of application, errors with config file lead to hard coding config in app
#Fix soon
#e_string = model.ENGINE_STRING
#print(e_string)
#app.config["SQLALCHEMY_DATABASE_URI"] = e_string

# =======================LOGIN MANAGER INIT=======================
#lm = LoginManager()
#lm.init_app(app)
#lm.login_view = 'login'

# ===Main & Admin Pages===
@app.route('/') 
def index():
	return render_template('index.html')

#pull product list uses functions library found in app dir to return a json of the product list in full - enacted on index load
def index2():
    return functions.pull_product_list()

@app.route('/admin/')
def admin_panel():
    return render_template('admin_panel.html')

# ===User Login Pages & Methods===

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/logout/')
def logout():
    return redirect('index.html')

# ======================= DEBUG ==========================



if __name__ == '__main__':
    app.run(host='0.0.0.0' , port=8080 , debug=True)