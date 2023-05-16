from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

db_url = "postgresql://sqlalchemy_test:password@localhost/sqlalchemy_test"
engine = create_engine(db_url)

SessionFactory = sessionmaker(bind=engine)

session = SessionFactory()
# Do stuff with the session

with engine.connect() as connection:
    result = connection.execute(text("""
        SELECT o.first_name, o.last_name, p.name
        FROM owners o
        JOIN ponies p ON (o.id = p.owner_id)
    """))
    for row in result:
        print(row)
        print(row["first_name"], row["last_name"], "owns", row["name"])

engine.dispose()