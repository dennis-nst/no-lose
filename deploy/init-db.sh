#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE wa_evolution'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'wa_evolution')\gexec
    GRANT ALL PRIVILEGES ON DATABASE wa_evolution TO $POSTGRES_USER;
EOSQL
