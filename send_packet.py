import sys
from itertools import chain
import socket
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from repository import get_neighbour_port

HOST = '127.0.0.1'

def main():
    if len(sys.argv) > 4:
        print("Too much arguments, need name only")
        sys.exit()
    elif len(sys.argv) < 4:
        print("Not enough arguments, need name only")
        sys.exit()
    name_from = sys.argv[1]
    name_to = sys.argv[2]
    message = sys.argv[3]
    engine = create_engine(
        'postgres://postgres:postgres@localhost:5432/pg_test'
    )
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    ports = get_neighbour_port(session, name_from)
    print(ports)
    session.close()
    engine.dispose()
    message = 'Packet' + '\n' + name_to + '\n' + message
    for port in chain.from_iterable(ports):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            addr = (HOST, int(port))
            s.sendto(message.encode('utf-8'), addr)
            print("Sent packet to {}".format(name_from))
            s.close()

if __name__ == "__main__":
    main()