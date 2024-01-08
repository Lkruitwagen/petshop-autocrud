#!/bin/bash
echo "postgresql://$PG_DB_USER:$PG_DB_PW@$PG_DB_HOST:$PG_DB_PORT"
psql -c "CREATE DATABASE $PG_DB_NAME"
psql -d "$PG_DB_NAME" -c "CREATE EXTENSION pg_trgm;"
