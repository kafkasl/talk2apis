# Talk2APIS

Server code to test and show the potential of JIT Workflow automation.

**IMPORTANT**: we use flask and sqlite which may not be great for prod environments. However, if we are doing a demo to show people how this can change the world, we can make it stateless and scale horizontally (stateless replies) + load balancer.

### Run the code

Create a .env file in the project root directory by copying the `sample.conf` and add the following environment variables:

```
DEBUG=True
HTTP_PORT=5000
HOST_PROJECT_PATH=/path/to/your/project/on/host
SQLALCHEMY_APIS_DATABASE_URI='sqlite:///apis.db'
OPENAI_API_KEY='your_openai_api_key'
```

### Run using docker

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

### Database

We use sqlalchemy as ORM and alembic to manage the db migrations.

The models for the Service/APIs can be found in `database/services`

Run `make migrate` to create the sqlite file (db) with the schema defined in `database/*`

The `populate_db.py` will parse the files in `openapi/definition/*{json,yaml}` and create entries for each service in the database.
