import ast
import re
import parse
import socket
import sys
from itertools import chain
import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, desc
import time as time
import signal

from repository import insert_router_info, insert_count, insert_router_table,\
    get_max_count, get_routing_table, get_router_names, \
    get_routing_table_pc_names, get_hop_cout, delete_routing_table_row, \
    get_neighbours, get_neighbour_port, get_neighbour_in_routing_table, \
    delete_routing_table_neighbour, delete_neighbour, find_next_router

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5200        # Port to listen on (non-privileged ports are > 1023)
NAME = 'default_name'

LOG = logging.getLogger(__name__)

def handler(signum, frame):
    raise Exception('30 seconds passed')

def main():
    print(PORT)
    neighbours = tuple()
    signal.signal(signal.SIGALRM, handler)
    while True:
        signal.alarm(10)  #How much time to wait for requesting routing tables
        try:
            message = get_message()

        except Exception:
            signal.alarm(10)
            print("Request tables from neighbours") #Kas 30 sekundziu
            last_neighbours = neighbours
            #inactive_neighbours(last_neighbours)
            neighbours = request_routing_tables()

        except KeyboardInterrupt:
            sys.exit()

        else:
            signal.alarm(10)
            print('Got message, working on it')
            message = message.decode("utf-8")
            """Packet, table or request?"""
            if 'Send table to' in message:
                print("Got request")
                neighbour_port = parse.parse('Send table to {}', message)
                send_routing_table_to(neighbour_port[0])
            elif 'Table' in message:
                print("Got table")
                message = message.split('\n')
                message.pop(0)
                neighbour_name = message.pop(0)
                if neighbour_name in chain.from_iterable(neighbours):
                    """neighbours = ''.join(map(str, neighbours))
                    neighbours = neighbours.replace(
                        "('" + neighbour_name + "',)", ''
                    )"""
                    message = '\n'.join(message)
                    save_routing_table(message, neighbour_name)
                    print("Table updated")
            elif 'Packet' in message:
                send_packet_to(message)
            else:
                print("Got something I should not had to got")
            #If table got, delete neighbour
            #  'Send table to {}'.format(PORT)
            # NAME + select_routing_table()
            # parsed = parse.parse('Send table to {}', port_to)
            # new func send_routing_table()


def init():
    engine = create_engine(
        'postgres://postgres:postgres@localhost:5432/pg_test'
    )
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    router_names = get_router_names(session)
    if len(sys.argv) > 2:
        print("Too much arguments, need name only")
        sys.exit()
    elif len(sys.argv) < 2:
        print("Not enough arguments, need name only")
        sys.exit()
    elif sys.argv[1] in chain.from_iterable(router_names):
        print("There already is router with this name")
        sys.exit()
    global NAME
    NAME = sys.argv[1]
    router_count = get_max_count(session)
    global PORT
    PORT = PORT + router_count
    insert_count(session, router_count+1)
    pc_id = "{}_pc".format(NAME)
    insert_router_info(session, NAME, PORT, pc_id)
    insert_router_table(session, NAME, pc_id, 0, 'self')
    session.close()
    engine.dispose()


def get_message():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            message, address = s.recvfrom(1024)
            return message


def select_routing_table():
    engine = create_engine(
        'postgres://postgres:postgres@localhost:5432/pg_test'
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    table = get_routing_table(session, NAME)
    routing_table = ''
    for row in table:
        routing_table += "{}|{}|{}\n".format(row.destination_pc_id,
                                             row.hop_cost,
                                             row.neighbour)
    session.close()
    engine.dispose()
    return routing_table


def save_routing_table(routing_table, router):
    routing_table = routing_table.splitlines()
    routing_table_template = "{}|{}|{}"
    engine = create_engine(
        'postgres://postgres:postgres@localhost:5432/pg_test'
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    routing_table_pc_names = get_routing_table_pc_names(session, NAME)
    for row in routing_table:
        parsed = parse.parse(routing_table_template, row)
        """ parsed[0] - pc_name , 
        parsed[1] - hop count , 
        parsed[2] - router name """
        if parsed[0] in chain.from_iterable(routing_table_pc_names):
            current_hop_count, current_id = get_hop_cout(
                session, NAME, parsed[0]
            )
            if current_hop_count > int(parsed[1]):
                delete_routing_table_row(session, current_id)
                insert_router_table(
                    session, NAME, parsed[0], int(parsed[1]) + 1, router
                )
        elif parsed[0] not in chain.from_iterable(routing_table_pc_names):
            insert_router_table(
                session, NAME, parsed[0], int(parsed[1]) + 1, router
            )
    session.close()
    engine.dispose()


def request_routing_tables():
    engine = create_engine(
        'postgres://postgres:postgres@localhost:5432/pg_test'
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    neighbours = get_neighbours(session, NAME)
    for neighbour in chain.from_iterable(neighbours):
        neighbour_port = get_neighbour_port(session, neighbour)
        for port in chain.from_iterable(neighbour_port):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                addr = (HOST, port)
                message = 'Send table to {}'.format(PORT)
                s.sendto(message.encode('utf-8'), addr)
                print("Sent request to {}".format(port))

    session.close()
    engine.dispose()
    return neighbours


def inactive_neighbours(last_neighbours):
    if last_neighbours:
        engine = create_engine(
            'postgres://postgres:postgres@localhost:5432/pg_test'
        )
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
        for last in chain.from_iterable(last_neighbours):
            list = get_neighbour_in_routing_table(session, NAME, last)
            if list:
                delete_routing_table_neighbour(session, NAME, last)
                print("{} in routing table was made "
                      "unreachable".format(last))
            else:
                delete_neighbour(session, NAME, last)
                print("{} connection as neighbour was deleted".format(last))

        session.close()
        engine.dispose()


def send_routing_table_to(neighbour_port):
    final_routing_table = "Table" + "\n" + NAME + '\n' + select_routing_table()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        addr = (HOST, int(neighbour_port))
        s.sendto(final_routing_table.encode('utf-8'), addr)
        print("Sent routing table to {}".format(neighbour_port))
        s.close()


def send_packet_to(packet):
    packet = packet.split('\n')
    to_neighbour = packet[1]
    if NAME == to_neighbour:
        print("Packet came safely to {}_pc".format(NAME))
        packet.pop(0)
        packet.pop(0)
        print("Message is: {}".format(packet))
    else:
        engine = create_engine(
            'postgres://postgres:postgres@localhost:5432/pg_test'
        )
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
        try:
            next_hop = find_next_router(session, NAME, to_neighbour + "_pc")
        except:
            print("No neighbour in table")
        else:
            neighbour_port = get_neighbour_port(session, next_hop)
            packet = '\n'.join(packet)
            for port in chain.from_iterable(neighbour_port):
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    addr = (HOST, int(port))
                    s.sendto(packet.encode('utf-8'), addr)
                    print("Redirected packet to {}".format(next_hop))
        session.close()
        engine.dispose()


if __name__ == "__main__":
    init()
    request_routing_tables()
    main()

