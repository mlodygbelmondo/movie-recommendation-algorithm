from extensions import db

class Users(db.Model):
    __tablename__ = 'Users'

    Id = db.Column(db.String(36), primary_key=True, nullable=False)  # String instead of UUID
    Login = db.Column(db.String(50), nullable=False)
    Password = db.Column(db.String(250), nullable=False)
    Email = db.Column(db.String(50), nullable=False)