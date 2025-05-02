#!/bin/sh

echo "Esperando a la base de datos..."
while ! nc -z db 5432; do
  sleep 0.5
done

echo "Ejecutando flask db upgrade..."
flask db upgrade

echo "Ejecutando init_app.py..."
python init_app.py

echo "Iniciando servidor Flask..."
exec python run.py
