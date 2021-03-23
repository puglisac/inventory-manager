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

    def test_get_one_category_404(self):
        with app.test_client() as client:
            resp = client.get(f"/categories/0", headers={ 'Authorization': f'Bearer {TestCategoriesRoutes.token}'})
            self.assertEqual(resp.status_code, 404)

    def test_unauth_get_one_cagegory(self):
        with app.test_client() as client:
            resp = client.get(f"/categories/{TestCategoriesRoutes.test_category_id}", headers={ 'Authorization': f'Bearer {None}'})
            self.assertEqual(resp.status_code, 422)
    
    def test_unauth_edit_category(self):
        with app.test_client() as client:
            resp = client.patch(f"/users/{TestCategoriesRoutes.test_category_id}", headers={ 'Authorization': f'Bearer {TestCategoriesRoutes.token}'}, 
            json={'description': 'newDescription'})
            self.assertEqual(resp.status_code, 401)

    def test_edit_Category_as_admin(self):
        with app.test_client() as client:
            resp = client.patch(f"/categories/{TestCategoriesRoutes.test_category_id}", headers={ 'Authorization': f'Bearer {TestCategoriesRoutes.admin_token}'}, 
            json={'description': 'newDescription'})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json['category']['description'], 'newDescription')
    
    def test_delete_category(self):
        c=Category(  name="category_to_delete",
                        description="will be deleted")
        db.session.add(c)
        db.session.commit()
        with app.test_client() as client:
            resp = client.delete(f"/categories/{c.id}", headers={ 'Authorization': f'Bearer {TestCategoriesRoutes.admin_token}'})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json['message'], "category successfully deleted")

    def test_unauth_delete_category(self):
        c=Category(  name="category_to_delete",
                        description="will be deleted")
        db.session.add(c)
        db.session.commit()
        with app.test_client() as client:
            resp = client.delete(f"/categories/{c.id}", headers={ 'Authorization': f'Bearer {TestCategoriesRoutes.token}'})
            self.assertEqual(resp.status_code, 401)
            self.assertEqual(resp.json['message'], "unauthorized")