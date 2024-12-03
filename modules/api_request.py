import requests
import os


def request_product_rating(p_name):
    url = "https://real-time-amazon-data.p.rapidapi.com/search"

    querystring = {"query":f"{p_name}","page":"1","country":"US","sort_by":"RELEVANCE","product_condition":"ALL","is_prime":"false","deals_and_discounts":"NONE"}

    headers = {
	    "x-rapidapi-key": os.getenv('x-rapidapi-key'),
	    "x-rapidapi-host": os.getenv('x-rapidapi-host')
    }

    response = requests.get(url, headers=headers, params=querystring)

    print(response.json())

    return response.json()