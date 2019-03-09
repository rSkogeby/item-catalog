#!/usr/bin/env python3
"""Python Database API."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    name = Column(
        String(80), nullable=False
    )
    id = Column(
        Integer, primary_key=True
    )
    @property
    def serialize(self):
        # Return object data in easily serialisable format
        return {
            'name': self.name,
            'id': self.id
        }


class Item(Base):
    __tablename__ = 'item'
    name = Column(
        String(80), nullable=False
    )
    description = Column(
        String(800), nullable=False
    )
    category_id = Column(
        Integer, ForeignKey('category.id')
    )
    category = relationship(Category)
    id = Column(
        Integer, primary_key=True
    )
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
