#!/bin/bash

# Clean up any existing container
podman rm -f postgres-container 2>/dev/null

# Run PostgreSQL container
podman run -d \
  --name postgres-container \
  -p 5433:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -v ./postgres-sample-dbs:/docker-entrypoint-initdb.d:Z \
  docker.io/postgres:13

# Function to wait for container to be running
wait_for_container() {
    while true; do
        status=$(podman inspect -f '{{.State.Status}}' postgres-container 2>/dev/null)
        if [ "$status" = "running" ]; then
            break
        fi
        echo "Waiting for container to start..."
        sleep 1
    done
}

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
    while true; do
        podman exec postgres-container pg_isready -U postgres > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            break
        fi
        echo "Waiting for PostgreSQL to start..."
        sleep 1
    done
}

# Wait for container to be running
wait_for_container

# Wait for PostgreSQL to be ready
wait_for_postgres

# Create databases and load schemas
databases=("chinook" "pagila" "periodic_table" "happiness_index" "unused_db")

for db in "${databases[@]}"; do
  if [ "$db" != "unused_db" ]; then
    echo "Creating and initializing database: $db"
    podman exec postgres-container psql -U postgres -c "CREATE DATABASE $db;"
    podman exec postgres-container psql -U postgres -d $db -f /docker-entrypoint-initdb.d/$db.sql
  else
    echo "Creating unused database: unused_db"
    podman exec postgres-container psql -U postgres -c "CREATE DATABASE unused_db;"
  fi
done

echo "Deployment complete!"
echo "Connect to PostgreSQL using:"
echo "  Host: localhost"
echo "  Port: 5433"
echo "  User: postgres"
echo "  Password: postgres"
