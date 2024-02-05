from database import db
from sqlalchemy.dialects.sqlite import JSON, BLOB
import numpy as np
from typing import Dict, List, Tuple
import json
from sqlalchemy.orm.exc import NoResultFound


class Services(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=False)


class ServiceCategories(db.Model):
    __tablename__ = "service_categories"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    category = db.Column(db.String(80), nullable=False)


class ServiceAPIs(db.Model):
    __tablename__ = "service_apis"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    version = db.Column(db.String(80), nullable=False)
    base_url = db.Column(db.String(120), nullable=False)


class APIEndpoint(db.Model):
    __tablename__ = "api_endpoints"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    api_id = db.Column(db.Integer, db.ForeignKey("service_apis.id"), nullable=False)
    path = db.Column(db.String(), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    summary = db.Column(db.String(), nullable=True)
    description = db.Column(db.String(), nullable=True)
    parameters = db.Column(JSON, nullable=True)
    definition = db.Column(JSON, nullable=True)
    embedding = db.Column(BLOB)

    def to_dict(self):
        # Convert the definition JSON to a dictionary
        definition_dict = json.loads(self.definition) if self.definition else {}

        # Add the path and method as top-level fields
        definition_dict["path"] = self.path
        definition_dict["method"] = self.method

        return definition_dict

    @classmethod
    def get_embeddings_for_service(
        cls, service_name: str
    ) -> List[Tuple[object, np.ndarray]]:
        # Find the service by name
        all_services = Services.query.all()

        print("All services in the database:")
        for service in all_services:
            print(
                f"Service ID: {service.id}, Name: {service.name}, Description: {service.description}"
            )

        service = Services.query.filter_by(name=service_name).one()

        # Extract embeddings
        db_endpoints = cls.query.filter_by(service_id=service.id).all()
        embeddings = [
            (endpoint, np.frombuffer(endpoint.embedding))
            for endpoint in db_endpoints
            if endpoint.embedding
        ]

        return embeddings


class APIParameters(db.Model):
    __tablename__ = "api_parameters"  # Explicitly define the table name
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    endpoint_id = db.Column(
        db.Integer, db.ForeignKey("api_endpoints.id"), nullable=False
    )
    name = db.Column(db.String(), nullable=False)
    type = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    required = db.Column(db.Boolean, nullable=False)


def DeleteService(session, service_name):
    # Query for the service
    service = session.query(Services).filter(Services.name == service_name).first()

    # If the service exists, delete all related rows
    if service is not None:
        # Delete related rows in APIParameter
        session.query(APIParameters).filter(
            APIParameters.service_id == service.id
        ).delete()

        # Delete related rows in APIEndpoint
        session.query(APIEndpoint).filter(APIEndpoint.service_id == service.id).delete()

        # Delete related rows in ServiceAPI
        session.query(ServiceAPIs).filter(ServiceAPIs.service_id == service.id).delete()

        # Delete related rows in ServiceCategory
        session.query(ServiceCategories).filter(
            ServiceCategories.service_id == service.id
        ).delete()

        # Finally, delete the service itself
        session.delete(service)

        # Commit the transaction
        session.commit()

        print(f"Service {service_name} and all related rows deleted.")
    else:
        print(f"Service {service_name} not found.")
