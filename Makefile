.PHONY: migrate
message ?= Auto-generated migration


migrate:
	alembic revision --autogenerate -m "$(message)"
	alembic upgrade head