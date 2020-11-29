from __future__ import unicode_literals

from datetime import datetime

import sqlalchemy as sa
from sms_digi.models.meta import Base
from sqlalchemy.dialects.postgresql import JSONB


class User(Base):
    """
        User DB-Model class:
            Columns are created using sqlalchemy and colander is used for validations.
            Table Name: "user"
            Columns with their validations:
                id = Integer, autoincrement, primary_key
                email = Text
                password = Text
                created_date = Timestamp without time zone
                updated_date = Timestamp without time zone
    """

    __tablename__ = 'user'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    email = sa.Column(sa.Text, nullable=False)
    password = sa.Column(sa.Text, nullable=False)
    created_date = sa.Column(sa.DateTime, default=datetime.utcnow, server_default=sa.func.now(), nullable=False)
    updated_date = sa.Column(sa.DateTime, default=datetime.utcnow, server_default=sa.func.now(), nullable=False)


class Chemical(Base):
    """
    Chemical DB-Model class:
        Columns are created using sqlalchemy and colander is used for validations.
        Table Name: "chemical"
        Columns with their validations:
            id = Integer, autoincrement, primary_key
            name = Text
            created_date = Timestamp without time zone
            updated_date = Timestamp without time zone
    """

    __tablename__ = 'chemical'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    name = sa.Column(sa.Text, nullable=False)
    created_date = sa.Column(sa.DateTime, default=datetime.utcnow, server_default=sa.func.now(), nullable=False)
    updated_date = sa.Column(sa.DateTime, default=datetime.utcnow, server_default=sa.func.now(), nullable=False)


class Commodity(Base):
    """
    Commodity DB-Model class:
        Columns are created using sqlalchemy and colander is used for validations.
        Table Name: "commodity"
        Columns with their validations:
            id = Integer, autoincrement, primary_key
            name = Text
            inventory = BigInteger
            price = Float
            chemical_composition = JSONB
    """

    __tablename__ = 'commodity'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    name = sa.Column(sa.Text, nullable=False)
    inventory = sa.Column(sa.Float, nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    chemical_composition = sa.Column(JSONB, nullable=False)
    created_date = sa.Column(sa.DateTime, default=datetime.utcnow, server_default=sa.func.now(), nullable=False)
    updated_date = sa.Column(sa.DateTime, default=datetime.utcnow, server_default=sa.func.now(), nullable=False)
