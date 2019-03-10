#!/usr/bin/env python3
"""Python Database API."""

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, func, DateTime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

class Mixin(object):
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

   #pid =  Column(Integer, nullable=True)
    creation_date = Column(DateTime, default=func.now())
    last_modified = Column(DateTime, onupdate=func.now())

Base = declarative_base(cls=Mixin)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), index=True)
    picture = Column(String(160), nullable=True)
    password_hash = Column(String(64), nullable=True)
    
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('user.id')
    )
    user = relationship(User)
    @property
    def serialize(self):
        # Return object data in easily serialisable format
        return {
            'name': self.name,
            'id': self.id
        }



class Item(Base):
    __tablename__ = 'item'
    name = Column(String(80), nullable=False)
    description = Column(String(800), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('user.id')
    )
    user = relationship(User)
    @property
    def serialize(self):
        # Return object data in easily serialisable format
        return {
            'name': self.name,
            'description':self.description,
            'category_id': self.category_id,
            'id': self.id
        }

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
