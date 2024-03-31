import sqlalchemy as db
from database.db_base import db_base


class Debtor(db_base.Base):
    __tablename__ = 'debtors'
    full_name = db.Column(db.String, primary_key=True)
    debt_amount = db.Column(db.Float)

