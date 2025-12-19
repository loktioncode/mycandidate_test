import datetime
from typing import Any
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.ext.declarative import as_declarative,declarative_base, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str


    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


# Base = declarative_base(cls=CustomBase)