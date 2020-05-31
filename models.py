from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Routers(Base):
    __tablename__ = "routers"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    router_name = Column(VARCHAR(80))
    router_port = Column(Integer)
    pc_id = Column(VARCHAR(80))


class Neighbours(Base):
    __tablename__ = "neighbours"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    router_name = Column(VARCHAR(80))
    neighbour = Column(VARCHAR(80))


class Number(Base):
    __tablename__ = "number"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    count = Column(Integer)


class Router(Base):
    __tablename__ = "router_table"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    owned_by = Column(VARCHAR(80))
    destination_pc_id = Column(VARCHAR(80))
    hop_cost = Column(Integer)
    neighbour = Column(VARCHAR(80))
