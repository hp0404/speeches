#! /usr/bin/env bash

cat assets/backups/db-dump.sql | docker exec -i restapi_db_1 psql -U postgres
