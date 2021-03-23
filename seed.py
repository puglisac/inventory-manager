
from models import db, User
from app import app

db.create_all()

adminUser = User.signup("admin@email.com", "AdminPassword", "Admin", "User", True)

db.session.add(adminUser)
db.session.commit()