#!/usr/bin/env bash
set -euo pipefail
umask 077

# Configuración
PROJECT_DIR="/home/juanx/kayn"
BACKUP_DIR="${PROJECT_DIR}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=15

# Cargar variables del .env si existe
if [ -f "${PROJECT_DIR}/.env" ]; then
    export $(grep -v '^#' "${PROJECT_DIR}/.env" | xargs)
fi

mkdir -p "${BACKUP_DIR}"

echo "[$(date)] Kayn está haciendo un backup..."

# 1. Backup Base de Datos GLPI
echo "Milio está guardando sus datos!"
docker exec glpi-mysql mysqldump \
    -u"${GLPI_DB_USER:-glpi_user}" \
    -p"${GLPI_DB_PASSWORD}" \
    "${GLPI_DB_NAME:-glpidb}" > "${BACKUP_DIR}/glpi_${TIMESTAMP}.sql"

# 2. Backup Base de Datos Snipe-IT
echo "Gekko está guardando sus datos!"
docker exec snipe-mysql mysqldump \
    -u"${DB_USERNAME:-snipeit_user}" \
    -p"${DB_PASSWORD}" \
    "${DB_DATABASE:-snipeit}" > "${BACKUP_DIR}/snipeit_${TIMESTAMP}.sql"

# 3. Backup Base de Datos Kanboard (SQLite)
echo "Kayn está guardando las tarjetas de Kanboard!"
docker cp kanban:/var/www/app/data/db.sqlite "${BACKUP_DIR}/kanboard_${TIMESTAMP}.sqlite"

# 4. Comprimir volcados (GLPI + Snipe-IT + Kanboard)
echo "Kayn está empaquetando todo..."
cd "${BACKUP_DIR}"
tar -czf "backup_milio_${TIMESTAMP}.tar.gz" \
    "glpi_${TIMESTAMP}.sql" \
    "snipeit_${TIMESTAMP}.sql" \
    "kanboard_${TIMESTAMP}.sqlite"

# Limpieza de temporales descomprimidos
rm -f "glpi_${TIMESTAMP}.sql" "snipeit_${TIMESTAMP}.sql" "kanboard_${TIMESTAMP}.sqlite"

# 5. Rotación: eliminar backups de más de RETENTION_DAYS días
find "${BACKUP_DIR}" -name "backup_milio_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete

echo "[$(date)] Listo! Si nada se rompió, acá esta el backup: ${BACKUP_DIR}/backup_milio_${TIMESTAMP}.tar.gz"
