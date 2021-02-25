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
    def setUp(self):
        User.query.delete()
        self.admin_test_user=User.signup(
                            email="admin_test@email.com",
                            password="password",
                            first_name="First",
                            last_name="Last",
                            is_admin=True
        )
        self.test_user=User.signup(
                            email="test@email.com",
                            password="anotherPassword",
                            first_name="First",
                            last_name="Last",
                            is_admin=False
        )
        db.session.add_all([self.admin_test_user, self.test_user])
        db.session.commit()

    
    def test_login(self):
        with app.test_client() as client:
            resp = client.post("/users/login", json={"email":"admin_test@email.com", "password": "password"})
            self.assertEqual(resp.status_code, 200)

    def test_invalid_login(self):
        with app.test_client() as client:
            resp = client.post("/users/login", json={"email":"test@email.com", "password": "password"})
            self.assertEqual(resp.status_code, 401)