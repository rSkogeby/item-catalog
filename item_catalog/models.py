#!/usr/bin/env python3
"""Python Database API."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Item(Base):
    __tablename__ = 'item'
    name = Column(
        String(80), nullable=False
    )
    id = Column(
        Integer, primary_key=True
    )

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
