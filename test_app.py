from unittest import TestCase
from models import db, connect_db, User
import os

from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TEST_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = "some_secret_key"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserTest(TestCase):

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()

        self.testuser = User.register(
            email="test@test.com",
            pwd="testuser",
            first="test",
            last="user")
        db.session.add(self.testuser)
        db.session.commit()
        self.user_id = self.testuser.id

    def test_login_user(self):
        with app.test_client() as client:
            resp = client.post('/users/login', {"email": "test@test.com", "password": "testuser"})
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)