#!/bin/bash
set -e

SERVICE_NAME="db_restore"    # nome do serviço no docker-compose
CONTAINER_NAME="postgres14-marialuiza-teste"  # nome exato do container
VOLUME_NAME="db_data"        # volume que você quer resetar

echo "🛑 Parando container $CONTAINER_NAME..."
sudo docker stop $CONTAINER_NAME 2>/dev/null || true

echo "🗑 Removendo container $CONTAINER_NAME..."
sudo docker rm $CONTAINER_NAME 2>/dev/null || true

echo "🗑 Removendo volume $VOLUME_NAME..."
sudo docker volume rm $VOLUME_NAME 2>/dev/null || true

echo "🚀 Subindo novamente..."
sudo docker compose up -d $SERVICE_NAME

echo "✅ Restore iniciado — ao criar o volume do zero, o Postgres executará backup.sql automaticamente."
