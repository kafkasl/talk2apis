.PHONY: migrate
message ?= Auto-generated migration


migrate:
	alembic revision --autogenerate -m "$(message)"
	alembic upgrade head
clean-db:
	rm -rf apis.db alembic/versions/*
