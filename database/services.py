from database import db

class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    
    description = db.Column(db.String(), nullable=False)

class ServiceCategories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    category = db.Column(db.String(80), nullable=False)

class ServiceAPIs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    version = db.Column(db.String(80), nullable=False)
    base_url = db.Column(db.String(120), nullable=False)

class APIEndpoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    api_id = db.Column(db.Integer, db.ForeignKey('service_api.id'), nullable=False)
    path = db.Column(db.String(), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    summary = db.Column(db.String(), nullable=True)
    description = db.Column(db.String(), nullable=True)

class APIParameters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('api_endpoint.id'), nullable=False)
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
        session.query(APIParameters).filter(APIParameters.service_id == service.id).delete()

        # Delete related rows in APIEndpoint
        session.query(APIEndpoints).filter(APIEndpoints.service_id == service.id).delete()

        # Delete related rows in ServiceAPI
        session.query(ServiceAPIs).filter(ServiceAPIs.service_id == service.id).delete()

        # Delete related rows in ServiceCategory
        session.query(ServiceCategories).filter(ServiceCategories.service_id == service.id).delete()

        # Finally, delete the service itself
        session.delete(service)

        # Commit the transaction
        session.commit()

        print(f"Service {service_name} and all related rows deleted.")
    else:
        print(f"Service {service_name} not found.")