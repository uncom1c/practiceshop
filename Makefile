install:
	python -m venv venv
	.\venv\Scripts\python.exe -m pip install pip-tools

sync: 
	.\venv\Scripts\pip-compile r.in
	.\venv\Scripts\pip-sync r.txt

start:
	.\venv\Scripts\python.exe main.py

init-migrate:
	.\venv\Scripts\alembic.exe init alembic

revision-migrate:
	.\venv\Scripts\alembic.exe revision --autogenerate -m "Another migration"

migrate:
	.\venv\Scripts\alembic.exe upgrade head

test:
    PYTHONPATH=.pytest


.PHONY: install sync start init-migrate revision-migrate migrate test

