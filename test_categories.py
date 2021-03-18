from unittest import TestCase
from app import app
from models import db, connect_db, User, Category
from flask import jsonify
import os

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///inventory_manager_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = "some_secret_key"
app.config['TESTING'] = True

connect_db(app)

db.create_all()

class TestCategoriesRoutes(TestCase):
    
    @classmethod
    def setUpClass(cls):
        """ get_some_resource() is slow, to avoid calling it for eachtest  use setUpClass()
            and store the result as class variable
        """
        super(TestCategoriesRoutes, cls).setUpClass()
        User.query.delete()
        Category.query.delete()
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
        cls.test_category=Category(name="Category name",
                            description="this describes the item")

        db.session.add_all([cls.admin_test_user, cls.test_user, cls.test_category])
        db.session.commit()
        cls.test_category_id=cls.test_category.id
        cls.admin_token = None
        cls.token = None
        with app.test_client() as client:
            resp = client.post("/users/login", json=   {"email":"admin_test@email.com", "password": "password"})
            cls.admin_token = resp.json['access_token']

        with app.test_client() as client:
            resp = client.post("/users/login", json={"email":"test@email.com", "password": "anotherPassword"})
            cls.token = resp.json['access_token']

    def test_get_all_categories(self):
        with app.test_client() as client:
            resp = client.get("/categories/", headers={ 'Authorization': f'Bearer {TestCategoriesRoutes.admin_token}'})
            self.assertEqual(resp.status_code, 200)

    def test_invalid_get_all_categories(self):
        with app.test_client() as client:
            resp = client.get("/categories/", headers={ 'Authorization': f'Bearer {None}'})
            self.assertEqual(resp.status_code, 422)

    def test_get_one_category(self):
        with app.test_client() as client:
            resp = client.get(f"/categories/{TestCategoriesRoutes.test_category_id}", headers={ 'Authorization': f'Bearer {TestCategoriesRoutes.token}'})
            self.assertEqual(resp.status_code, 200)

    def test_unauth_get_one_users(self):
        with app.test_client() as client:
            resp = client.get(f"/categories/{TestCategoriesRoutes.test_category_id}", headers={ 'Authorization': f'Bearer {None}'})
            self.assertEqual(resp.status_code, 422)
    
    def test_unauth_edit_category(self):
        with app.test_client() as client:
            resp = client.patch(f"/users/{TestCategoriesRoutes.test_category_id}", headers={ 'Authorization': f'Bearer {TestCategoriesRoutes.token}'}, 
            json={'description': 'newDescription'})
            self.assertEqual(resp.status_code, 401)

    # def test_edit_user_as_admin(self):
    #     with app.test_client() as client:
    #         resp = client.patch("/users/test@email.com", headers={ 'Authorization': f'Bearer {TestUsersRoutes.admin_token}'}, 
    #         json={'first_name': 'newName'})
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual(resp.json['user']['first_name'], 'newName')
    
    # def test_self_edit_user(self):
    #     with app.test_client() as client:

    #         resp = client.patch("/users/test@email.com", headers={ 'Authorization': f'Bearer {TestUsersRoutes.token}'}, 
    #         json={'first_name': 'newerName'})
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual(resp.json['user']['first_name'], 'newerName')

    # def test_change_pwd(self):
    #     with app.test_client() as client:
    #         resp = client.patch("/users/test@email.com/change_password", headers={ 'Authorization': f'Bearer {TestUsersRoutes.token}'}, 
    #         json={'existing_password': 'anotherPassword', 'new_password':'newPassowrd'})
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual(resp.json['user']['email'], 'test@email.com')

    # def test_unauth_change_pwd(self):
    #     with app.test_client() as client:
    #         resp = client.patch("/users/test@email.com/change_password", headers={ 'Authorization': f'Bearer {TestUsersRoutes.admin_token}'}, 
    #         json={'existing_password': 'anotherPassword', 'new_password':'newPassowrd'})
    #         self.assertEqual(resp.status_code, 401)

    # def test_wrong_change_pwd(self):
    #     with app.test_client() as client:
    #         resp = client.patch("/users/test@email.com/change_password", headers={ 'Authorization': f'Bearer {TestUsersRoutes.token}'}, 
    #         json={'existing_password': 'Password', 'new_password':'newPassowrd'})
    #         self.assertEqual(resp.status_code, 400)
    #         self.assertEqual(resp.json['message'], "incorrect password")
    
    # def test_delete_user_as_admin(self):
    #     u=User.signup(  email="to_delete@email.com",
    #                     password="password",
    #                     first_name="First",
    #                     last_name="Last",
    #                     is_admin=False)
    #     db.session.add(u)
    #     db.session.commit()
    #     with app.test_client() as client:
    #         resp = client.delete("/users/to_delete@email.com", headers={ 'Authorization': f'Bearer {TestUsersRoutes.admin_token}'})
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual(resp.json['message'], "user successfully deleted")

    # def test_unauth_delete_user(self):
    #     u=User.signup(  email="to_delete@email.com",
    #                     password="password",
    #                     first_name="First",
    #                     last_name="Last",
    #                     is_admin=False)
    #     db.session.add(u)
    #     db.session.commit()
    #     with app.test_client() as client:
    #         resp = client.delete("/users/to_delete@email.com", headers={ 'Authorization': f'Bearer {TestUsersRoutes.token}'})
    #         self.assertEqual(resp.status_code, 401)
    #         self.assertEqual(resp.json['message'], "unauthorized")

    # def test_delete_user_as_self(self):
    #     u=User.signup(  email="to_delete@email.com",
    #                     password="password",
    #                     first_name="First",
    #                     last_name="Last",
    #                     is_admin=False)
    #     db.session.add(u)
    #     db.session.commit()
    #     with app.test_client() as client:
    #         token_resp=client.post("/users/login", json={"email":"to_delete@email.com", "password": "password"})
    #         token=token_resp.json['access_token']
    #         resp = client.delete("/users/to_delete@email.com", headers={ 'Authorization': f'Bearer {token}'})
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual(resp.json['message'], "user successfully deleted")

    # def test_add_item_to_user(self):
    #     with app.test_client() as client:
    #         resp = client.patch("/users/test@email.com/add_item", headers={ 'Authorization': f'Bearer {TestUsersRoutes.token}'},
    #         json={'item_id': TestUsersRoutes.test_item_id})
    #         self.assertEqual(resp.status_code, 200)

    # def test_remove_item_from_user(self):
    #     with app.test_client() as client:
    #         resp = client.patch("/users/test@email.com/remove_item", headers={ 'Authorization': f'Bearer {TestUsersRoutes.admin_token}'},
    #         json={'item_id': TestUsersRoutes.test_item_id})
    #         self.assertEqual(resp.status_code, 200)

    # def test_unauth_remove_item_from_user(self):
    #     with app.test_client() as client:
    #         resp = client.patch("/users/test@email.com/remove_item", headers={ 'Authorization': f'Bearer {TestUsersRoutes.token}'},
    #         json={'item_id': TestUsersRoutes.test_item_id})
    #         self.assertEqual(resp.status_code, 401)
