#!/bin/sh

DB_NAME=$POSTGRES_DB
DB_USER=$POSTGRES_USER
DUMP_FILE="/data/initial_data/db_dump.sql"

# Wait for PostgreSQL to be ready (optional but useful)
until pg_isready -U "$DB_USER"; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Restore the database
echo "Restoring database from $DUMP_FILE..."
psql -U "$DB_USER" -d "$DB_NAME" -f "$DUMP_FILE"

echo "Restore complete."
