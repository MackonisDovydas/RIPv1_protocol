import sys
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine


from repository import get_routing_table

NAME = 'default_name'

def main():
    if len(sys.argv) > 2:
        print("Too much arguments, need name only")
        sys.exit()
    elif len(sys.argv) < 2:
        print("Not enough arguments, need name only")
        sys.exit()
    global NAME
    NAME = sys.argv[1]
    engine = create_engine(
        'postgres://postgres:postgres@localhost:5432/pg_test'
    )
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    table = get_routing_table(session, NAME)
    for row in table:
        print(row.destination_pc_id, "|", row.hop_cost, "|", row.neighbour)
    session.close()
    engine.dispose()



if __name__ == "__main__":
    main()