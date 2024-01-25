.PHONY: migrate
message ?= Auto-generated migration

freeze:
	pip freeze > requirements.txt
install:
	pip install -r requirements.txt%
migrate:
	alembic revision --autogenerate -m "$(message)"
	alembic upgrade head
clean-db:
	rm -rf apis.db alembic/versions/*
