import sys
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from repository import insert_neighbour


def main():
    if len(sys.argv) > 3:
        print("Too much arguments, need name only")
        sys.exit()
    elif len(sys.argv) < 3:
        print("Not enough arguments, need name only")
        sys.exit()
    name1 = sys.argv[1]
    name2 = sys.argv[2]
    engine = create_engine(
        'postgres://postgres:postgres@localhost:5432/pg_test'
    )
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    insert_neighbour(session, name1, name2)
    insert_neighbour(session, name2, name1)
    print("{} link to {} added".format(name1, name2))
    session.close()
    engine.dispose()

if __name__ == "__main__":
    main()