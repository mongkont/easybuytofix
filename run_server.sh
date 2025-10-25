#!/bin/bash
# Script to activate virtual environment and run Django development server

cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting Django development server with PostgreSQL..."
echo "Database: easybuytfix_db"
echo "Admin URL: http://127.0.0.1:8000/admin/"
echo "Username: mongkont"
echo "Press Ctrl+C to stop the server"
python manage.py runserver
