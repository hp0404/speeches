#! /usr/bin/env bash

docker exec -t restapi_db_1 pg_dumpall -c -U postgres > assets/backups/db-dump.sql
