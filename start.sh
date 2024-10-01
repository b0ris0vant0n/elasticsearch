#!/bin/bash

echo "Ожидание запуска PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL запущен."

echo "Очистка базы данных..."
psql postgresql://postgres:postgres@postgres:5432/postgres -f reset_db.sql

echo "Применение миграций..."
alembic upgrade head

echo "Запуск приложения..."
python main.py
