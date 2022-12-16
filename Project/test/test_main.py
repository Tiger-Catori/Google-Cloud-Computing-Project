import unittest
import io
from unittest import mock
from app import main


class TestMethods(unittest.TestCase):

    # Create a test local Flask client
    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()

    def unauthenticatedUserHelper(self, token):
        return {
            'user_data': None,
            'error_message': 'An authentication error message'
        }

    def authenticatedUserHelper(self, token):
        return {
            'user_data': {
                'userId': '3FCEQ8ZzLjXsmQwv9Yc8Q4oYOfp1',
                'email': 'michael@gmail.com',
                'name': 'Mr Michael',
                'admin': 'False',
                'orders': [{
                    'timestamp': '2021-12-13 15:07:02.188034',
                    'name': 'Mr Michael',
                    'address': 'Bond Street',
                    'paymentType': 'card',
                    'content': [{
                        'productId': '619bb55c11dd33ac12d5aa0f',
                        'qty': '2'
                    }],
                    'expectedDeliveryDate': '2021-12-20 15:07:02.191293',
                    'totalCost': '400.5',
                    'status': 'Cancelled'
                }],
                'basket': [{
                    'productId': '619bb55c11dd33ac12d5aa12',
                    'qty': '8'
                }]
            },
            'error_message': 'An authentication error message'
        }

    def adminUserHelper(self, token):
        user = TestMethods.authenticatedUserHelper(token)
        user['user_data']['admin'] = 'True'
        return user

    def add_to_basketHelper(self, userId, productId, qty):
        return 201

    def remove_from_basketHelper(self, userId, basketIndex):
        return 201

    def get_productHelper(self, productId=None):
        if productId == None:  # Call for all products
            return [TestMethods.get_productHelper(1),
                    TestMethods.get_productHelper(1),
                    TestMethods.get_productHelper(1)
                    ]
        else:  # Call for specific product
            return {
                '_id': {
                    '$oid': 'id'
                },
                'title': 'Shooter',
                'ageRating': '15',
                'pricePerUnit': '20.00',
                'qty': '10',
                'imageID': '555',
                'tags': ['Action', 'Shooter']
            }

    def create_orderHelper(self, orderDetails):
        return 201

    def delete_userHelper(self, id):
        return 200

    def update_userHelper(self, data):
        return 200

    def get_user_summariesHelper(self):
        return [{
            'userId': '3FCEQ8ZzLjXsmQwv9Yc8Q4oYOfp1',
            'email': '123@gmail.com',
            'name': 'Mr 123',
            'admin': 'False'
        }]

    def upload_imageHelper(self, imageId, base64Image):
        return 200

    def update_productHelper(self, params):
        return 200

    def delete_imageHelper(self, imageId):
        return 200

    def delete_productHelper(self, productId):
        return 200


    def test_root(self):
        response = self.app.get('/')
        self.assertIn("<h1>Welcome to the Game Store </h1>",
                      str(response.data))
        self.assertEqual(response.status_code, 200)


    def test_home(self):
        response = self.app.get('/home')
        self.assertIn("<h1>Welcome to the Game Store </h1>",
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    def test_shop(self):
        response = self.app.get('/shop')
        self.assertIn('<h1> Welcome to the shop page</h1>',
                      str(response.data))
        self.assertEqual(response.status_code, 200)


    def test_about(self):
        response = self.app.get('/about')
        self.assertIn("gamestore@gmail.com",
                      str(response.data))
        self.assertEqual(response.status_code, 200)



    def test_404(self):
        response = self.app.get('/notavalidroute')
        self.assertIn('The requested URL was not found on the server',
                      str(response.data))
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
