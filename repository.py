from models import Number, Router, Routers, Neighbours
from typing import List

def get_max_count(session):
    number = (
        session.query(Number)
        .order_by(Number.count.desc())
        .all()
    )
    return number[0].count


def insert_count(session, count):
    insert = Number(
        count=count
    )
    session.add(insert)
    session.commit()


def insert_router_info(session, name, port, pc_id):
    insert = Routers(
        router_name=name,
        router_port=port,
        pc_id=pc_id
    )
    session.add(insert)
    session.commit()


def insert_router_table(session, name, pc_id, hop_cost, neighbour):
    insert = Router(
        owned_by=name,
        destination_pc_id=pc_id,
        hop_cost=hop_cost,
        neighbour=neighbour
    )
    session.add(insert)
    session.commit()

def get_routing_table(session, name) -> List[Router]:
    return (
        session.query(Router)
            .filter(Router.owned_by == name)
            .all()
    )

def get_router_names(session) -> List[Routers]:
    return (
        session.query(Routers.router_name)
            .all()
    )


def get_routing_table_pc_names(session, name) -> List[Router]:
    return (
        session.query(Router.destination_pc_id)
            .filter(Router.owned_by == name)
            .all()
    )


def get_hop_cout(session, name, pc_name):
    get = (
        session.query(Router)
            .filter(Router.owned_by == name)
            .filter (Router.destination_pc_id == pc_name)
            .one()
    )
    return get.hop_cost, get.id

def delete_routing_table_row(session, id):
    session.query(Router).filter(Router.id == id).delete()
    session.commit()

def get_neighbours(session, name):
    return (
        session.query(Neighbours.neighbour)
            .filter(Neighbours.router_name == name)
            .all()
    )
def get_neighbour_port(session, neighbour_name):
    return (
        session.query(Routers.router_port)
            .filter(Routers.router_name == neighbour_name)
            .all()
    )

def get_neighbour_in_routing_table(session, name, neighbour):
    return (
        session.query(Router.neighbour)
            .filter(Router.owned_by == name)
            .filter(Router.neighbour == neighbour)
            .all()
    )

def delete_routing_table_neighbour(session, name, neighbour):
    session.query(Router).\
        filter(Router.owned_by == name).\
        filter(Router.neighbour == neighbour).\
        delete()
    session.commit()

def delete_neighbour(session, name, neighbour):
    session.query(Neighbours).\
        filter(Neighbours.router_name == name).\
        filter(Neighbours.neighbour == neighbour).\
        delete()
    session.commit()

def insert_neighbour(session, name, neighbour):
    insert = Neighbours(
        router_name= name,
        neighbour = neighbour
    )
    session.add(insert)
    session.commit()

def find_next_router(session, name, destination):
    get = session.query(Router).\
            filter(Router.owned_by == name).\
            filter(Router.destination_pc_id == destination).\
            one()
    return get.neighbour
