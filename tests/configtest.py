import pytest

from modules import functions
from flask import Flask, request

@pytest.fixture()
def app():
    app = Flask(__name__)

    with app.app_context():
        functions.pull_product_list()
    
    yield(app)

@pytest.fixture()
def client(app):
    return app.test_client()