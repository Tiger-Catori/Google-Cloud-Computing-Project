import base64
from datetime import datetime, timedelta
import logging
import json
from flask import Flask, render_template, request, url_for, redirect
import functions
import uuid

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/')
@app.route('/home')  # HOME (HERO) PAGE
def home():
    """
        Main Landing page of the site.
        Contains a hero page spanning with whole or most of the viewport.
    """
    return render_template('home.html')


@app.route('/shop', methods=["GET"])  # SHOP (PRODUCTS) PAGE
def shop():
    """
    The Shop Page
    It contains a list of all the products available, each with an 'Add to basket' button.
    If you're an Admin, you also have a 'edit' button to edit the product.
    Account: Not required
    Admin: Not required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    product_info = functions.format_product_data(
        functions.get_product())


    return render_template('shop.html',
                           product_info=product_info,
                           user_data=auth_content['user_data'])


@app.route('/login', methods=['GET'])
def login():
    """The login page for the site.
    It uses firebase to authenticate the user (Google accounts only)
    On the first login, a document in the database will be created for the user
    Account: Not required
    Admin: Not required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    return render_template(
        'login.html',
        user_data=auth_content['user_data'],
        error_message=auth_content['error_message'])

@app.route('/about')
def about():
    """
        About page showing what the site is about.
    """
    return render_template('about.html')


@app.route('/basket', methods=['GET'])
def basket():
    """This shows the items currently in the user's basket
    Products can be removed from the basket
    Account: Required
    Admin: Not required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    else:
        # Add some details to the products
        runningTotal = 0
        for item in auth_content['user_data']['basket']:
            product = functions.get_product(item['productId'])
            item['title'] = product['title']
            item['imageID'] = product['imageID']
            item['pricePerUnit'] = float(product['pricePerUnit'])
            item['qty'] = int(item['qty'])
            runningTotal += item['pricePerUnit']*item['qty']

        return render_template('basket.html',
                               user_data=auth_content['user_data'],
                               totalPrice=runningTotal)


@app.route('/add_to_basket', methods=['POST'])
def add_to_basket():
    """A background post call to add a product to the user's basket.
    Account: Required
    Admin: Not required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    else:
        userId = auth_content['user_data']['userId']
        productId = request.form['id']
        qty = request.form['qty']

        response = functions.add_to_basket(userId, productId, qty)

        if response == 201:
            return "Success", 201
        else:
            return "Something went wrong", 500


@app.route('/remove_from_basket', methods=['POST'])
def remove_from_basket():
    """This removes a product from the basket and redirects the user back to their basket
    Account: Required
    Admin: Not required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    else:
        userId = auth_content['user_data']['userId']
        basketIndex = request.form['basketIndex']

        response = functions.remove_from_basket(userId, basketIndex)

        if response == 201:
            return redirect(url_for('basket'))
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're not sure what went wrong, but we're looking into it. Try again in a few mins",
                                   user_data=auth_content['user_data']), 500


@app.route('/orders', methods=['GET'])
def viewOrders():
    """This shows all orders an account has made
    Account: Required
    Admin: Not required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    else:
        return render_template('orders.html',
                               user_data=auth_content['user_data'])


@app.route('/create_order', methods=['GET'])
def create_order():
    """This page is where the user fills in their address for the order
    Account: Required
    Admin: Not required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    else:
        return render_template('create_order.html',
                               user_data=auth_content['user_data'])


@app.route('/create_order', methods=['POST'])
def submitOrder():
    """This creates an order from the user's basket then redirects them to their order
    Account: Required
    Admin: Not required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    else:
        runningTotal = 0
        for item in auth_content['user_data']['basket']:
            product = functions.get_product(item['productId'])
            runningTotal += float(product['pricePerUnit'])*int(item['qty'])

        orderDetails = {
            'userId': auth_content['user_data']['userId'],
            'timestamp': str(datetime.now()),
            'name': request.form['name'],
            'address': request.form['address'],
            'paymentType': request.form['paymentType'],
            'content': json.dumps(auth_content['user_data']['basket']),
            'expectedDeliveryDate': str(datetime.now() + timedelta(days=7)),
            'totalCost': runningTotal,
            'status': 'Preparing'
        }

        # Send to google function to create order and empty basket
        response = functions.create_order(orderDetails)

        if response == 201:
            return redirect(url_for('viewOrders'))
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're not sure what went wrong, but we're looking into it. Try again in a few mins",
                                   user_data=auth_content['user_data']), 500


@app.route('/update_product', methods=['GET'])
def update_product():
    """A page to edit details about an existing product. Only accessible by admins
    Account: Required
    Admin: Required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    elif auth_content['user_data']['admin'] == 'False':
        return unauthorised(auth_content)
    else:
        product_id = request.args.get('id')

        product_info = functions.get_product(product_id)

        # Change the tag list into a string for formatting
        formattedTags = ""
        for tag in product_info['tags']:
            formattedTags += tag + ","
        formattedTags = formattedTags[0:-1]
        product_info['tags'] = formattedTags.lower()

        return render_template('update_product.html',
                               product_info=product_info,
                               user_data=auth_content['user_data'])


@app.route('/admin', methods=['GET'])
def admin():
    """The main admin page.
    Has functionality to create and delete products and view, edit and delete users (and their order status)
    Account: Required
    Admin: Required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    elif auth_content['user_data']['admin'] == 'False':
        return unauthorised(auth_content)
    else:
        product_info = functions.get_product()
        customer_data = functions.get_user_summaries()

        return render_template('admin.html',
                               product_info=product_info,
                               customer_data=customer_data,
                               user_data=auth_content['user_data'])


@app.route('/edit_user', methods=['GET'])
def edit_user():
    """A page to edit details in a user account (and their orders)
    Account: Required
    Admin: Required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    elif auth_content['user_data']['admin'] == 'False':
        return unauthorised(auth_content)
    else:
        customer_id = request.args.get('id')
        customer_data = functions.get_user_data(customer_id)
        return render_template('edit_user_details.html',
                               customer_data=customer_data,
                               user_data=auth_content['user_data'])


@app.route('/delete_user', methods=['GET'])
def delete_user():
    """This deletes a user and redirects the admin to a confirmation page
    Account: Required
    Admin: Required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    elif auth_content['user_data']['admin'] == 'False':
        return unauthorised(auth_content)
    else:
        response = functions.delete_user(request.args.get('id'))

        if response == 200:
            return render_template('message.html',
                                   message_title='User Deleted',
                                   message_body='The user account has been deleted',
                                   user_data=auth_content['user_data'])
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=auth_content['user_data'])


@app.route('/update_user_submitted', methods=['POST'])
def update_user():
    """This updates a user's details then redirects the admin to a confirmation page
    Account: Required
    Admin: Required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    elif auth_content['user_data']['admin'] == 'False':
        return unauthorised(auth_content)
    else:
        if request.form['admin'] == 'on':
            admin = True
        else:
            admin = False

        orderStatuses = []
        for key in request.form.keys():
            if "orderStatusIndex" in key:
                orderStatuses.append(request.form[key])

        params = {
            'userId': request.form['userId'],
            'name': request.form['name'],
            'admin': admin,
            'orderStatuses': json.dumps(orderStatuses)
        }

        response = functions.update_user(params)

        if response == 200:
            return render_template('message.html',
                                   message_title='User Updated',
                                   message_body='The user account has been updated',
                                   user_data=auth_content['user_data'])
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=auth_content['user_data'])


@app.route('/update_personal_details', methods=['GET'])
def view_personal_details():
    """This shows a user their details and allows them to edit some parts
    Account: Required
    Admin: Not required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    else:
        return render_template('edit_personal_details.html',
                               user_data=auth_content['user_data'])


@app.route('/update_personal_details_submitted', methods=['POST'])
def update_personal_details():
    """This updates a user's own details
    Account: Required
    Admin: Not required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    else:
        admin = auth_content['user_data']['admin']

        orderStatuses = []
        for key in request.form.keys():
            if "orderStatusIndex" in key:
                orderStatuses.append(request.form[key])

        params = {
            'userId': request.form['userId'],
            'name': request.form['name'],
            'admin': admin,
            'orderStatuses': json.dumps(orderStatuses)
        }

        response = functions.update_user(params)

        if response == 200:
            return render_template('message.html',
                                   message_title='Details Updated',
                                   message_body='Your account has been updated',
                                   user_data=auth_content['user_data'])
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=auth_content['user_data'])


@app.route('/create_product_submitted', methods=['POST'])
def create_product_submitted_form():
    """This creates a new product then redirects the admin to a confirmation page
    Account: Required
    Admin: Required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    elif auth_content['user_data']['admin'] == 'False':
        return unauthorised(auth_content)
    else:

        imageID = str(uuid.uuid4())

        # Create the product text in MongoDB
        params = {
            "title": str(request.form['title']),
            "ageRating": str(request.form['ageRating']),
            "pricePerUnit": str(request.form['pricePerUnit']),
            "qty": int(request.form['qty']),
            "imageID": imageID,
            "tags": request.form['tags']
        }
        mongoResponse = functions.create_product(params)

        # Upload the image to Google Cloud Storage
        base64Image = base64.b64encode(request.files['image'].read())
        googleResponse = functions.upload_image(imageID, base64Image)

        if mongoResponse == 200 and googleResponse == 200:
            return render_template(
                'submitted_form.html',
                title=params['title'],
                ageRating=params['ageRating'],
                pricePerUnit=params['pricePerUnit'],
                qty=params['qty'],
                imageID=params['imageID'],
                tags=params['tags'],
                user_data=auth_content['user_data'],
                error_message=auth_content['error_message'],
                response="Successfully added to databases!"
            )
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=auth_content['user_data'])


@app.route('/update_product_submitted', methods=['POST'])
def update_product_submitted():
    """This updates details about an existing product. Only accessible by admins
    Account: Required
    Admin: Required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    elif auth_content['user_data']['admin'] == 'False':
        return unauthorised(auth_content)
    else:
        # Get product imageID data
        oldImageID = functions.get_product(request.form['id'])['imageID']
        newImageID = str(uuid.uuid4())

        googleUploadResponse = None
        googleRemoveResponse = None

        # Update MongoDB
        params = {
            "id": str(request.form['id']),
            "title": str(request.form['title']),
            "ageRating": str(request.form['ageRating']),
            "pricePerUnit": str(request.form['pricePerUnit']),
            "qty": int(request.form['qty']),
            "imageID": newImageID,
            "tags": request.form['tags']
        }
        mongoResponse = functions.update_product(params)

        # Update image in cloud storage if one was uploaded
        if request.files['image'].filename != '':

            # Upload new image
            base64Image = base64.b64encode(request.files['image'].read())
            googleUploadResponse = functions.upload_image(newImageID, base64Image)

            # Remove old image
            googleRemoveResponse = functions.delete_image(oldImageID)

        if (mongoResponse == 200 and
                (googleUploadResponse == 200 or googleUploadResponse == None) and
                (googleRemoveResponse == 200 or googleRemoveResponse == None)):
            return render_template('message.html',
                                   message_title='Product updated',
                                   message_body='The product details have been updated',
                                   user_data=auth_content['user_data'])
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=auth_content['user_data'])


@app.route('/delete_product_submitted', methods=['POST'])
def delete_product_submitted_form():
    """This deletes an existing product. Only accessible by admins
    Account: Required
    Admin: Required
    """
    auth_content = functions.authenticate_user(request.cookies.get("token"))

    # If not authenticated
    if auth_content['user_data'] == None:
        return redirect(url_for('login'))
    elif auth_content['user_data']['admin'] == 'False':
        return unauthorised(auth_content)
    else:
        # Get product imageID data
        imageID = functions.get_product(request.form['id'])['imageID']

        # Remove Mongo object
        mongoResponse = functions.delete_product(request.form['id'])

        # Remove image
        googleResponse = functions.delete_image(imageID)

        if mongoResponse == 200 and googleResponse == 200:
            return render_template('message.html',
                                   message_title='Product Deleted',
                                   message_body='The product has been deleted',
                                   user_data=auth_content['user_data'])
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=auth_content['user_data'])

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

def unauthorised(auth_content):
    return render_template('message.html',
                           message_title='Unauthorised',
                           message_body='Your account does not have permission to enter this page',
                           user_data=auth_content['user_data']), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    # Only run for local development.
    # app.run(host='127.0.0.1', port=8080, debug=True)
    app.run(debug=True)