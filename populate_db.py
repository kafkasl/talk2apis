import os
import glob
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from dotenv import load_dotenv

from openapi.service import Service
from database.services import (
    Services,
    ServiceCategories,
    ServiceAPIs,
    APIEndpoint,
    APIParameters,
    DeleteService,
)

from ai.embeddings import to_binary

load_dotenv()


def main(files, recreate=False):
    # Connect to the SQLitef database
    db_uri = "sqlite:///instance/apis.db"
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()

    for file in files:
        # Get the service name from the filename
        service_name = os.path.basename(file).split(".")[0]

        try:
            service = (
                session.query(Services).filter(Services.name == service_name).one()
            )
            if not recreate:
                print(f"Service {service_name} already exists in the database. Skipping...")
                continue

            print(
                f"Service {service_name} already exists in the database. Recreating..."
            )

            # Delete the service
            DeleteService(session, service_name)

        except NoResultFound:
            print(f"Adding new service to the database: {service_name}.")

        # Create a new Service object
        service = Service(service_name, file)

        # Get the service info
        service_info = service.get_service_info()

        # Create a new Service object in the database
        db_service = Services(
            name=service_info["name"], description=service_info["description"]
        )

        session.add(db_service)
        session.commit()

        # Create a new ServiceAPI object in the database
        db_service_api = ServiceAPIs(
            service_id=db_service.id,
            version=service_info["version"],
            base_url=service_info["base_url"],
        )

        session.add(db_service_api)
        session.commit()

        # Create service endpoints
        for endpoint in service.get_service_endpoints():
            db_endpoint = APIEndpoint(
                service_id=db_service.id,
                api_id=db_service_api.id,
                path=endpoint["path"],
                method=endpoint["method"],
                summary=endpoint["summary"],
                description=endpoint["description"],
                definition=endpoint["definition"],
                embedding=endpoint["embedding"],
            )

            session.add(db_endpoint)
            session.commit()


    # Don't forget to close the session when you're done
    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--definition_files", nargs="*", help="A list of definition files", default=[]
    )
    parser.add_argument(
        "--recreate", action="store_true", help="Overwrite db entries for existing apis"
    )

    args = parser.parse_args()

    files = args.definition_files
    recreate = args.recreate

    # If no service_id is passed, then we will populate all the services
    # in ./definitions
    if len(files) == 0:
        definitions_dir = os.path.join(os.getcwd(), "openapi/definitions")
        files = glob.glob(os.path.join(definitions_dir, "slack.json"))
        # files = glob.glob(os.path.join(definitions_dir, "*.json"))
        # files.extend(glob.glob(os.path.join(definitions_dir, "*.yml")))
    main(files, recreate)
