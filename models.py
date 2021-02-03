from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

# models go below
class User(db.Model, SerializerMixin):
    """User."""

    def __repr__(self):
        """Show info about user."""

        u = self
        return f"<User {u.email} {u.first_name} {u.last_name}>"

    __tablename__ = "users"

    email = db.Column(db.Text,
                      primary_key=True,
                      nullable=False,
                      unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    pull_list = db.relationship('Item', secondary='pull_list', backref='user')

    @classmethod
    # authenticate a user
    def authenticate(cls, email, password):
        u=User.query.get_or_404(email)
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else: 
            return False
    
    @classmethod
    # signs up a new user
    def signup(cls, email, password, first_name, last_name):
        hashed_password = bcrypt.generate_password_hash(password).decode("utf8")
        u=cls(email=email, password=hashed_password, first_name=first_name, last_name=last_name)
        db.session.add(u)
        try:
            db.session.commit()
            return u
        except:
            raise RuntimeError('something went wrong')

class Item(db.Model, SerializerMixin):
    """Item."""

    def __repr__(self):
        """Show info about item."""

        i = self
        return f"<Item {i.id} {i.name} {i.quantity} {i.location} {i.description} {i.image_path}>"

    __tablename__ = "items"

    id = db.Column(db.Integer,
                      primary_key=True,
                      autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image_path=db.Column(db.Text)
    categories = db.relationship('Category', secondary='items_categories', backref='items')

class Category(db.Model):
    """Category."""

    def __repr__(self):
        """Show info about category."""

        c = self
        return f"<Item {c.id} {c.name} {c.description}>"

    __tablename__ = "categories"

    id = db.Column(db.Integer,
                      primary_key=True,
                      autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)

class Item_Category(db.Model):

    __tablename__="items_categories"

    id = db.Column(db.Integer, 
                        primary_key=True,
                        autoincrement=True)
    item_id = db.Column(db.Integer,
                        db.ForeignKey('items.id'), 
                        nullable=False)
    category_id = db.Column(db.Integer,
                        db.ForeignKey('categories.id'), 
                        nullable=False)

class Pull_List(db.Model):

    __tablename__='pull_list'

    id=db.Column(db.Integer, 
                    primary_key=True,
                    autoincrement=True)
    item_id = db.Column(db.Integer,
                        db.ForeignKey('items.id'), 
                        nullable=False)
    user_id = db.Column(db.Text,
                        db.ForeignKey('users.email'), 
                        nullable=False)