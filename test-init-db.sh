#! /bin/sh

python src/manager.py db_empty
python src/manager.py db_init
python src/manager.py import_projects var/projects.json
python src/manager.py create_admin alan.turing@example.org ROTOR_III
python src/manager.py create_user john.doe@example.org password
