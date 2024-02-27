# Talk2APIS

Server code to test and show the potential of JIT Workflow automation.

**IMPORTANT**: we use flask and sqlite which may not be great for prod environments. However, if we are doing a demo to show people how this can change the world, we can make it stateless and scale horizontally (stateless replies) + load balancer.

## Run the code

### Set up environment

Create a .env file in the project root directory by copying the `sample.conf` and add the following environment variables:

```
DEBUG=True
HTTP_PORT=5000
HOST_PROJECT_PATH=/path/to/your/project/on/host
SQLALCHEMY_APIS_DATABASE_URI='sqlite:///apis.db'
OPENAI_API_KEY='your_openai_api_key'
```

### Run using docker (Recommended)

Replace /path/to/your/project/on/host with the absolute path to your project directory on your host machine. Replace your_openai_api_key with your actual OpenAI API key

Build the Docker images and start the Docker containers:

`docker-compose up --build`

### Run locally

```
# Make sure you are running in a venv
pip install -r requirements.txt

# Edit the file and create a config for the server
cp sample.conf .env

# Start server
python app.py
```

The server is a simple flask server (async not supported out-of-the-box) with a couple of endpoints.

### Adding a New API

To add a new API to the application, you need to run a script that populates the database with the API definitions. This is done using the `db-setup` service in Docker Compose.

Here's the step-by-step process:

1. **Add your API definition file**: Place your API definition file in the `openapi/definitions` directory. The file should be in the OpenAPI format and have a `.yaml` extension.

2. **Run the `db-setup` service**: Run the following command in your terminal:

   ```bash
   docker-compose run db-setup python populate_db.py --definition_files openapi/definitions/your-api-definition.yaml
   ```

   Replace `your-api-definition.yaml` with the name of your API definition file.

This command will start the `db-setup` service, which will run the `populate_db.py` script with your API definition file as an argument. The script will populate the database with the API definitions from the file.

**NOTE** The script will create an embedding for each endpoint. For an API with 36 endpoints this is less than $0.01, but you should be careful and monitor your spending on https://platform.openai.com/usage.

You will also to add a new option to the dropdown in `templates/index.html` with the new service.

```
<select id="service" name="service" class="form-control">
    <option value="github">Github</option>
    <option value="openai">OpenAI</option>
    ...
```

Use the name of the OpenAPI definition file in the `value` field.

### Database

We use sqlalchemy as ORM and alembic to manage the db migrations.

The models for the Service/APIs can be found in `database/services`

Run `make migrate` to create the sqlite file (db) with the schema defined in `database/*`

The `populate_db.py` will parse the files in `openapi/definition/*{json,yaml}` and create entries for each service in the database.
