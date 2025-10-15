"""
SQLAlchemy declarative base and database models.

Defines the base class for all database models using SQLAlchemy's
declarative_base pattern. All models should inherit from Base.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Provides common functionality for all database models including:
    - Declarative mapping support
    - Metadata management for migrations
    - Common column types and mixins (can be extended)

    Example usage:
        from mcp_server.models.base import Base
        from sqlalchemy import Column, Integer, String

        class User(Base):
            __tablename__ = "users"

            id = Column(Integer, primary_key=True)
            name = Column(String(255))
    """

    pass
