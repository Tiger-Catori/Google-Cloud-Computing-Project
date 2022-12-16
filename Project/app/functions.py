from flask import Flask, render_template, request 
import json
import google.oauth2.id_token
from google.auth.transport import requests as googleRequests
from google.cloud import datastore
import requests

firebase_request_adapter = googleRequests.Request()

user_id = ""
name = ""
email = ""


"""This file is for Utility and Cloud Functions"""


def format_product_data(products):
    """Formats a list of products into rows of four products long"""
    newFormat = []
    currentRow = []
    for product in products:
        currentRow.append(product)
        if len(currentRow) == 4:
            newFormat.append(currentRow)
            currentRow = []
    if len(currentRow) != 0:
        newFormat.append(currentRow)
    return newFormat


def authenticate_user(token):
    """ Authenticates the user and returns the user's information"""

    # Verify Firebase auth.
    id_token = token
    error_message = None
    claims = None
    user_data = None
    if id_token:
        try:
            # Verify the token against the Firebase Auth API.
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            # Get the users' account (and make it if it doesn't exist)
            user_data = get_user_data(
                claims['user_id'], claims['email'], claims['name'])

        except ValueError as exc:
            # Expired tokens etc
            error_message = str(exc)
            user_data = None
    return {
        "user_data": user_data,
        "error_message": error_message
    }

def get_user_data(userId, email="", name=""):
    """Get's the specified user's account including basket and orders.
    If the userId is not in the database, an account will be created for it.
    """

    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/read_mongodb_user"
    data = {
        'userId': userId,
        'email': email,
        'name': name
    }
    response = requests.get(url, data)
    user_data = json.loads(response.content.decode("utf-8"))

    return user_data


def get_product(productId=None):
    """ Returns information on products
        If productId is supplied, just that product will be returned.
        If no productId is supplied, all products are returned.
    """

    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/read_mongodb_products"

    if productId:
        params = {'id': productId}
    else:
        params = {}

    response = requests.get(url, params)
    data = json.loads(response.content.decode("utf-8"))
    return data

def add_to_basket(userId, productId, qty):
    """Adds a number of products to a specified user's basket
    On success, returns 201
    """

    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/add_mongodb_user_basket"
    params = {
        "userId": userId,
        "productId": productId,
        "qty": qty
    }
    response = requests.post(
        url, params)

    return response.status_code


def remove_from_basket(userId, basketIndex):
    """Removes a product from a specified user's basket
    On success, returns 201
    """

    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/remove_mongodb_user_basket"
    params = {
        "userId": userId,
        "basketIndex": basketIndex
    }
    response = requests.post(
        url, params)

    return response.status_code


def create_order(orderDetails):
    """Creates and order and empties the basket in a user's account
    On success, returns 201
    """

    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/add_mongodb_user_order"
    response = requests.post(url, orderDetails)

    return response.status_code


def get_user_summaries():
    """Gets all user's id, email, name and admin status"""

    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/read_mongodb_user_summaries"
    response = requests.get(url)
    customer_data = json.loads(response.content.decode("utf-8"))

    return customer_data


def delete_user(userId):
    """Deletes a user's account from the database
    On success, returns 200
    """
    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/delete_mongodb_user"
    response = requests.post(url, {'userId': userId})

    return response.status_code


def update_user(params):
    """Updates a user's account
    On success, returns 200
    """
    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/update_mongodb_user"
    response = requests.post(url, params)

    return response.status_code


def create_product(params):
    """Creates a new product in Mongo (Text part)
    On success, returns 200
    """
    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/create_mongodb_product"
    response = requests.get(url, params)

    return response.status_code


def upload_image(imageId, base64Image):
    """Creates a new product image in Cloud Storage
    On success, returns 200
    """
    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/upload_cloud_storage_image"
    params = {
        "id": imageId,
        "image": base64Image
    }
    response = requests.post(url, params)

    return response.status_code


def delete_image(id):
    """Deletes a product image in Cloud Storage
    On success, returns 200
    """
    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/delete_cloud_storage_image"
    response = requests.post(url, {"id": id})

    return response.status_code


def update_product(params):
    """Updates a products text in Mongo
    On success, returns 200
    """
    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/update_mongodb_product"
    response = requests.get(url, params)

    return response.status_code


def delete_product(id):
    """Deletes a product in Mongo
    On success, returns 200
    """
    url = "https://europe-west2-cloudcomputingproject-367317.cloudfunctions.net/delete_mongodb_product"
    response = requests.get(url, {"id": id})

    return response.status_code