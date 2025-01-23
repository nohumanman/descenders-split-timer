#!/bin/bash

echo "Starting PostgreSQL service..."
sudo docker-compose up -d

sleep 1 # wait for PostgreSQL to start

echo "Applying schema..."
sudo .venv/bin/python apply-schema.py

echo "Running tests..."
sudo .venv/bin/python -m unittest discover -s tests -p "*_test.py"

echo "Stopping PostgreSQL service..."
sudo docker-compose down
