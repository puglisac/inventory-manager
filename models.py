from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy_serializer.serializer import SerializerMixin

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

# rules to exclude password and backref from serialization
    serialize_rules = ('-pull_list.user','-password')

    id=db.Column(db.Integer, 
                      primary_key=True,
                      autoincrement=True)
    email = db.Column(db.Text,
                      nullable=False,
                      unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    pull_list = db.relationship('Item', backref='user')

    @classmethod
    # authenticate a user
    def authenticate(cls, email, password):
        u=User.query.filter_by(email=email).first_or_404()
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else: 
            return False
    
    @classmethod
    # signs up a new user
    def signup(cls, email, password, first_name, last_name, is_admin):
        hashed_password = bcrypt.generate_password_hash(password).decode("utf8")
        u=cls(email=email, password=hashed_password, first_name=first_name, last_name=last_name, is_admin=is_admin)
        return u
    
    def changePassword(self, newPassword):
        hashed_password = bcrypt.generate_password_hash(newPassword).decode("utf8")
        self.password=hashed_password
        return self

class Item(db.Model, SerializerMixin):
    """Item."""

    def __repr__(self):
        """Show info about item."""

        i = self
        return f"<Item {i.id} {i.name} {i.quantity} {i.location} {i.description} {i.image_path}>"

    __tablename__ = "items"

    # rules to excludebackref from serialization
    serialize_rules = ('-categories.items',)

    id = db.Column(db.Integer,
                      primary_key=True,
                      autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image_path=db.Column(db.Text)
    categories = db.relationship('Category', secondary='items_categories', backref='items')
    user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete="SET NULL") )

class Category(db.Model, SerializerMixin):
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
