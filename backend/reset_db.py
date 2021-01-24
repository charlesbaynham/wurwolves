import sys

from alembic.autogenerate.api import compare_metadata
from alembic.migration import MigrationContext

from .database import engine
from .model import Base


def reset_database_if_needed():
    if len(sys.argv) > 1 and sys.argv[1] == "-f":
        print("Forcing database reset")
        reset_database()
        return

    # Check if the current database's tables match the expected ones
    target_metadata = Base.metadata
    mc = MigrationContext.configure(engine.connect())
    if compare_metadata(mc, target_metadata):
        # They differ: wipe and reset the database
        print("Table structure is altered: resetting the database...")
        reset_database()
    else:
        print("No changes required: not resetting database")


def reset_database():
    target_metadata = Base.metadata
    target_metadata.bind = engine
    target_metadata.drop_all()
    target_metadata.create_all()


if __name__ == "__main__":
    reset_database_if_needed()
