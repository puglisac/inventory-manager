from unittest import TestCase
from app import app
from models import db, connect_db, User
from flask import jsonify
import os

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///inventory_manager_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = "some_secret_key"
app.config['TESTING'] = True

connect_db(app)

db.create_all()

class TestUsersRoutes(TestCase):
    # def setUp(self):
        # User.query.delete()
        # self.admin_test_user=User.signup(
        #                     email="admin_test@email.com",
        #                     password="password",
        #                     first_name="First",
        #                     last_name="Last",
        #                     is_admin=True
        # )
        # self.test_user=User.signup(
        #                     email="test@email.com",
        #                     password="anotherPassword",
        #                     first_name="First",
        #                     last_name="Last",
        #                     is_admin=False
        # )
    @classmethod
    def setUpClass(cls):
        """ get_some_resource() is slow, to avoid calling it for eachtest  use setUpClass()
            and store the result as class variable
        """
        super(TestUsersRoutes, cls).setUpClass()
        User.query.delete()
        cls.admin_test_user=User.signup(
                            email="admin_test@email.com",
                            password="password",
                            first_name="First",
                            last_name="Last",
                            is_admin=True
        )
        cls.test_user=User.signup(
                            email="test@email.com",
                            password="anotherPassword",
                            first_name="First",
                            last_name="Last",
                            is_admin=False
        )
        db.session.add_all([cls.admin_test_user, cls.test_user])
        db.session.commit()
        cls.admin_token = None
        cls.token = None
        with app.test_client() as client:
            resp = client.post("/users/login", json=   {"email":"admin_test@email.com", "password": "password"})
            print("******", resp.json['access_token'])
            cls.admin_token = resp.json['access_token']

        # with app.test_client() as client:
        #     resp = client.post("/users/login", json={"email":"test@email.   com", "password": "anotherPassword"})
        #     cls.token = resp.json['access_token']

    def test_login(self):
        with app.test_client() as client:
            resp = client.post("/users/login", json={"email":"admin_test@email.com", "password": "password"})
            
            self.assertEqual(resp.status_code, 200)

    def test_invalid_login(self):
        with app.test_client() as client:
            resp = client.post("/users/login", json={"email":"test@email.com", "password": "password"})
            self.assertEqual(resp.status_code, 401)
    
    def test_signup(self):
        with app.test_client() as client:
            resp = client.post("/users/signup", json={
                                                "first_name":"New",
                                                "last_name":"User",
                                                "password":"password", 
                                                "email": "new@email.com", 
                                                "is_admin": False
                                                }, headers={ 'Authorization': f'Bearer {TestUsersRoutes.admin_token}'})
            self.assertEqual(resp.status_code, 201)