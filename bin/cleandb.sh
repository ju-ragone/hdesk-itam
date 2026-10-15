#!/usr/bin/env bash

DB_CONTAINER="glpi-mysql"
DB_USER="root"
DB_PASS="Admin.DemoCorp.Sec.2026!"
DB_NAME="glpidb"

# Consultar cantidad actual de tickets
TICKET_COUNT=$(docker exec -i "$DB_CONTAINER" mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -sN -e "SELECT COUNT(*) FROM glpi_tickets;" 2>/dev/null)

if [ -z "$TICKET_COUNT" ]; then
    echo "[!] Error: No se pudo conectar al contenedor $DB_CONTAINER o a la base$DB_NAME."
    exit 1
fi

echo "=========================================================="
echo " ⚠️  ADVERTENCIA: LIMPIEZA TOTAL DE TICKETS EN GLPI"
echo "=========================================================="
echo " Tickets actuales en la base de datos : $TICKET_COUNT"
echo " Acción                               : TRUNCATE (ID vuelve a 1)"
echo " Elementos preservados                : Usuarios, Reglas, SLAs, Formularios, Categorías"
echo "=========================================================="
read -r -p "¿Estás seguro de que querés eliminar TODOS los tickets? (escribí 'si' para confirmar): " CONFIRM

if [[ "$CONFIRM" != "si" && "$CONFIRM" != "SI" ]]; then
    echo "[i] Operación cancelada. No se modificó ningún dato."
    exit 0
fi

echo -e "\n[+] Limpiando tablas de tickets y registros asociados..."

docker exec -i "$DB_CONTAINER" mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE glpi_tickets;
TRUNCATE TABLE glpi_tickets_users;
TRUNCATE TABLE glpi_groups_tickets;
TRUNCATE TABLE glpi_suppliers_tickets;
TRUNCATE TABLE glpi_items_tickets;
TRUNCATE TABLE glpi_tickets_tickets;
TRUNCATE TABLE glpi_tickettasks;
TRUNCATE TABLE glpi_ticketvalidations;
TRUNCATE TABLE glpi_ticketcosts;
TRUNCATE TABLE glpi_slalevels_tickets;
DELETE FROM glpi_itilfollowups WHERE itemtype = 'Ticket';
DELETE FROM glpi_itilsolutions WHERE itemtype = 'Ticket';
DELETE FROM glpi_documents_items WHERE itemtype = 'Ticket';
DELETE FROM glpi_logs WHERE itemtype = 'Ticket';
SET FOREIGN_KEY_CHECKS = 1;

UPDATE glpi_rules SET \`condition\` = 3 WHERE id BETWEEN 101 AND 105;
UPDATE glpi_rulecriterias SET \`condition\` = 0 WHERE rules_id BETWEEN 101 AND 105 AND criteria = 'priority';
"

if [ $? -eq 0 ]; then
    echo "[✓] Base de tickets limpia (ID reseteado a 1) y reglas de SLA verificadas."
else
    echo "[!] Ocurrió un error durante la limpieza."
    exit 1
fi
