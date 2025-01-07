from extensions import db
from sqlalchemy.dialects.postgresql import ENUM
from enums import Status

class UserFriends(db.Model):
    __tablename__ = 'UserFriends'

    Id = db.Column(db.String(36), primary_key=True, nullable=False)
    UserId = db.Column(db.String(36), db.ForeignKey('Users.Id'), nullable=False)
    FriendId = db.Column(db.String(36), db.ForeignKey('Users.Id'), nullable=False)
    Status = db.Column(ENUM(Status, name="status_enum", create_type=False), nullable=False)

    user = db.relationship('Users', foreign_keys=[UserId], backref='friends')
    friend = db.relationship('Users', foreign_keys=[FriendId])
