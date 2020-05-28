# -*- coding: utf-8 -*-
"""User models."""
import datetime

from flask_login import UserMixin

from wurwolves.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)
from wurwolves.extensions import bcrypt


class Post(SurrogatePK, Model):
    __tablename__ = "post"

    title = Column(db.Text, unique=False, nullable=False)
    body = Column(db.Text, unique=False, nullable=False)
    author_id = reference_col("user", nullable=True)
    created = Column(db.DateTime, default=datetime.datetime.utcnow)


class User(SurrogatePK, Model):
    __tablename__ = "user"

    username = Column(db.String(50), unique=False, nullable=False)
    password = Column(db.LargeBinary(128), nullable=True)
    email = Column(db.String(160), unique=False, nullable=False)
