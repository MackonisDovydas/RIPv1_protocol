docker-compose up -d
sleep 3
virtualenv venv
pipenv lock
pipenv install
alembic upgrade head

