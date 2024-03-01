.PHONY: migrate
message ?= Auto-generated migration

run:
	docker-compose up --build
freeze:
	pip freeze > requirements.txt
install:
	pip install -r requirements.txt%
deploy:
	rsync -avz --progress --exclude='*.pyc' --exclude='__pycache__/' --exclude='talk2apis/' --exclude='.env' . talk:/home/service/app
	ssh -S talk "cd /home/service/app && sudo docker-compose up --build -d"
migrate:
	alembic revision --autogenerate -m "$(message)"
	alembic upgrade head
clean-db:
	rm -rf apis.db alembic/versions/*
