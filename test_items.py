from unittest import TestCase
from app import app
from models import Category, db, connect_db, User, Item
from flask import jsonify
import os

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///inventory_manager_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = "some_secret_key"
app.config['TESTING'] = True

connect_db(app)

db.create_all()

class TestItemsRoutes(TestCase):
    
    @classmethod
    def setUpClass(cls):
        """ get_some_resource() is slow, to avoid calling it for eachtest  use setUpClass()
            and store the result as class variable
        """
        super(TestItemsRoutes, cls).setUpClass()
        User.query.delete()
        Item.query.delete()
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
        cls.test_item=Item(name="Item name",
                            location="a place", 
                            description="this describes the item", 
                            quantity=2) 
        cls.test_category=Category(name="test",
                                    description="testing")
    

        db.session.add_all([cls.admin_test_user, cls.test_user, cls.test_item, cls.test_category])
        db.session.commit()
        cls.test_item_id=cls.test_item.id
        cls.test_category_id=cls.test_category.id
        cls.admin_token = None
        cls.token = None
        with app.test_client() as client:
            resp = client.post("/users/login", json=   {"email":"admin_test@email.com", "password": "password"})
            cls.admin_token = resp.json['access_token']

        with app.test_client() as client:
            resp = client.post("/users/login", json={"email":"test@email.com", "password": "anotherPassword"})
            cls.token = resp.json['access_token']

    def test_get_all_items(self):
        with app.test_client() as client:
            resp = client.get("/items/", headers={ 'Authorization': f'Bearer {TestItemsRoutes.token}'})
            self.assertEqual(resp.status_code, 200)

    def test_invalid_get_all_items(self):
        with app.test_client() as client:
            resp = client.get("/items/", headers={ 'Authorization': f'Bearer {None}'})
            self.assertEqual(resp.status_code, 422)

    def test_get_one_item(self):
        with app.test_client() as client:
            resp = client.get(f"/items/{TestItemsRoutes.test_item_id}", headers={ 'Authorization': f'Bearer {TestItemsRoutes.token}'})
            self.assertEqual(resp.status_code, 200)

    def test_get_one_item_404(self):
        with app.test_client() as client:
            resp = client.get(f"/items/0", headers={ 'Authorization': f'Bearer {TestItemsRoutes.token}'})
            self.assertEqual(resp.status_code, 404)

    def test_add_item(self):
        with app.test_client() as client:
            resp = client.post(f"/items/", headers={ 'Authorization': f'Bearer {TestItemsRoutes.admin_token}'},
            json={"name":"new item",
                    "location":"a place", 
                    "description":"this describes the item", 
                    "quantity":2,
                    "categories":[]})
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(resp.json['item']['name'], "new item")

    def test_unauth_add_item(self):
        with app.test_client() as client:
            resp = client.post(f"/items/", headers={ 'Authorization': f'Bearer {TestItemsRoutes.token}'}, 
            json={"name":"newer item",
                    "location":"a place", 
                    "description":"this describes the item", 
                    "quantity":2,
                    "categories":[]})
            self.assertEqual(resp.status_code, 401)
            self.assertEqual(resp.json['message'], "unauthorized")

    def test_unauth_edit_item(self):
        with app.test_client() as client:
            resp = client.patch(f"/items/{TestItemsRoutes.test_item_id}", headers={ 'Authorization': f'Bearer {TestItemsRoutes.token}'}, 
            json={'description': 'newDescription'})
            self.assertEqual(resp.status_code, 401)

    def test_edit_item(self):
        with app.test_client() as client:
            resp = client.patch(f"/items/{TestItemsRoutes.test_item_id}", headers={ 'Authorization': f'Bearer {TestItemsRoutes.admin_token}'}, 
            json={'description': 'newDescription'})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json['item']['description'], "newDescription")
 
    def test_delete_item(self):
        i=Item(name="item to delete",
                location="a place", 
                description="will be deleted", 
                quantity=2)
        db.session.add(i)
        db.session.commit()
        with app.test_client() as client:
            resp = client.delete(f"/items/{i.id}", headers={ 'Authorization': f'Bearer {TestItemsRoutes.admin_token}'})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json['message'], "item successfully deleted")

    def test_unauth_delete_item(self):
        i=Item(name="item to delete",
                location="a place", 
                description="will be deleted", 
                quantity=2)
        db.session.add(i)
        db.session.commit()
        with app.test_client() as client:
            resp = client.delete(f"/items/{i.id}", headers={ 'Authorization': f'Bearer {TestItemsRoutes.token}'})
            self.assertEqual(resp.status_code, 401)
            self.assertEqual(resp.json['message'], "unauthorized")

    def test_add_category_to_item(self):
        with app.test_client() as client:
            resp = client.patch(f"/items/{TestItemsRoutes.test_item_id}/add_category", headers={ 'Authorization': f'Bearer {TestItemsRoutes.admin_token}'}, 
            json={'category_id': TestItemsRoutes.test_category_id})
            self.assertEqual(resp.status_code, 200)
            self.assertIsNotNone(resp.json['item']['categories'][0])

    def test_add_category_to_item_404(self):
        with app.test_client() as client:
            resp = client.patch(f"/items/{TestItemsRoutes.test_item_id}/add_category", headers={ 'Authorization': f'Bearer {TestItemsRoutes.admin_token}'}, 
            json={'category_id': 0})
            self.assertEqual(resp.status_code, 404)

    def test_remove_category_from_item(self):
        with app.test_client() as client:
            resp = client.delete(f"/items/{TestItemsRoutes.test_item_id}/remove_category", headers={ 'Authorization': f'Bearer {TestItemsRoutes.admin_token}'}, 
            json={'category_id': TestItemsRoutes.test_category_id})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json['item']['categories']), 0)