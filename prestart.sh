#! /usr/bin/env bash

# Let the DB start
python app/database_pre_start.py

# Run migrations
alembic upgrade head