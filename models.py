from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

# models go below
class User(db.Model):
    """User."""

    def __repr__(self):
        """Show info about user."""

        u = self
        return f"<User {u.id} {u.email} {u.first_name} {u.last_name}>"

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    email = db.Column(db.Text,
                      nullable=False,
                      unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    home_location = db.Column(db.Text, nullable=False)

    @classmethod
    def authenticate(cls, email, password):
        u=User.query.get_or_404(email)
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else: 
            return False
