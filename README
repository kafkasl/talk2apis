# Talk2APIS 

Server code to test and show the potential of JIT Workflow automation.

**IMPORTANT**: we use flask and sqlite which may not be great for prod environments. However, if we are doing a demo to show people how this can change the world, we can make it stateless and scale horizontally (stateless replies) + load balancer.


### Run server

```
# Make sure you are running in a venv
pip install -r requirements.txt

# Edit the file and create a config for the server
cp sample.conf .env

# Start server
python app.py 
```

The server is a simple flask server (async not supported out-of-the-box) with a couple of endpoints. The static page is ugly and soul-less but it should be everything we need to test our assumptions.

### Database
We use sqlalchemy as ORM and alembic to manage the db migrations.

The models for the Service/APIs can be found in `database/services`

Run `make migrate` to create the sqlite file (db) with the schema defined in `database/*`

The `populate_db.py` will parse the files in `openapi/definition/*.json` and create entries for each service in the database. 


