import sqlalchemy as db

from database.db_base import db_base


class User(db_base.Base):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    lives_in_b = db.Column(db.Boolean)
    room_number = db.Column(db.Integer)
