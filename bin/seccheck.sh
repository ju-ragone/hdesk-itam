#!/usr/bin/env bash
# ==============================================================================
# SCRIPT DE AUDITORÍA DE SEGURIDAD Y HARDENING - PLATAFORMA MILIO / VOOLKIA
# Entorno Host: kayn (~/kayn)
# ==============================================================================

set -o pipefail

COLOR_RESET="\e[0m"
COLOR_GREEN="\e[32m"
COLOR_YELLOW="\e[33m"
COLOR_RED="\e[31m"
COLOR_CYAN="\e[36m"
COLOR_BOLD="\e[1m"

pass() { echo -e "  [${COLOR_GREEN}PASS${COLOR_RESET}] $1"; }
warn() { echo -e "  [${COLOR_YELLOW}WARN${COLOR_RESET}] $1"; }
fail() { echo -e "  [${COLOR_RED}FAIL${COLOR_RESET}] $1"; }
info() { echo -e "  [${COLOR_CYAN}INFO${COLOR_RESET}] $1"; }

KAYN_DIR="home/juanx/kayn"
TOTAL_FAILURES=0

echo -e "\n${COLOR_BOLD}=== INICIANDO AUDITORÍA DE SEGURIDAD EN HOST $(hostname) ===${COLOR_RESET}\n"

# ------------------------------------------------------------------------------
# 1. AUDITORÍA DE PUERTOS EXPUESTOS (SOCKET AUDIT)
# ------------------------------------------------------------------------------
echo -e "${COLOR_BOLD}1. Verificando aislamiento de puertos y sockets de red...${COLOR_RESET}"

# 1.1 Verificar que MariaDB (3306) NO esté expuesto al exterior
if ss -tulpn 2>/dev/null | grep -q ":3306 "; then
    fail "Puerto 3306 (MariaDB) detectado en interfaces del host. Peligro de exposición directa."
    ((TOTAL_FAILURES++))
else
    pass "Puerto 3306 (MariaDB) aislado correctamente en la red interna de Docker."
fi

# 1.2 Verificar servicios web esperados
for PORT in 9080 8080 7080 3001; do
    if ss -tulpn 2>/dev/null | grep -q ":${PORT} "; then
        pass "Servicio web en puerto ${PORT} activo y atendiendo peticiones."
    else
        warn "Puerto ${PORT} no detectado como LISTEN en el host."
    fi
done

# ------------------------------------------------------------------------------
# 2. AUDITORÍA DE PERMISOS DE ARCHIVOS SENSIBLES (LEAST PRIVILEGE)
# ------------------------------------------------------------------------------
echo -e "\n${COLOR_BOLD}2. Verificando permisos en archivos de configuración y backups...${COLOR_RESET}"

check_perm() {
    local target="$1"
    local expected="$2"
    if [ -e "$target" ]; then
        local actual
        actual=$(stat -c "%a" "$target")
        if [ "$actual" -le "$expected" ]; then
            pass "Permisos correctos en $target (${actual} <= ${expected})."
        else
            fail "Permisos permisivos en $target (${actual} > ${expected}). Corregir con chmod ${expected}."
            ((TOTAL_FAILURES++))
        fi
    else
        info "Archivo/Directorio $target no encontrado (omitiendo)."
    fi
}

check_perm "${KAYN_DIR}/.env" 600
check_perm "${KAYN_DIR}/docker-compose.yml" 600
check_perm "${KAYN_DIR}/backups" 700

# Validar permisos 600 en dumps .sql si existen
if compgen -G "${KAYN_DIR}/backups/*.sql" > /dev/null; then
    SQL_PERM_FAIL=0
    for f in "${KAYN_DIR}/backups"/*.sql; do
        actual=$(stat -c "%a" "$f")
        if [ "$actual" -gt 600 ]; then
            fail "Dump SQL con permisos inseguros: $f ($actual). Ejecutar chmod 600."
            SQL_PERM_FAIL=1
            ((TOTAL_FAILURES++))
        fi
    done
    [ $SQL_PERM_FAIL -eq 0 ] && pass "Todos los backups .sql poseen permisos estrictos (600)."
fi

# ------------------------------------------------------------------------------
# 3. ESCANEO DE CREDENCIALES POR DEFECTO EN ARCHIVOS DE CONFIGURACIÓN
# ------------------------------------------------------------------------------
echo -e "\n${COLOR_BOLD}3. Buscando credenciales por defecto o residuales en texto plano...${COLOR_RESET}"

LEAK_FOUND=0
PATTERN="password_123|root_password_123|glpi_password_123|snipeit_password_123"

if grep -rnE "$PATTERN" "${KAYN_DIR}"/*.yml "${KAYN_DIR}"/*.env "${KAYN_DIR}"/docker-compose* 2>/dev/null; then
    fail "Se detectaron credenciales residuales/default en archivos de configuración."
    LEAK_FOUND=1
    ((TOTAL_FAILURES++))
fi

[ $LEAK_FOUND -eq 0 ] && pass "No se encontraron contraseñas genéricas en los manifiestos de configuración."

# ------------------------------------------------------------------------------
# 4. AUDITORÍA DE SOCKET DOCKER (/var/run/docker.sock)
# ------------------------------------------------------------------------------
echo -e "\n${COLOR_BOLD}4. Verificando estado del montaje docker.sock en Uptime Kuma...${COLOR_RESET}"

if docker ps --format '{{.Names}}' | grep -q "^uptime-kuma$"; then
    SOCK_RW=$(docker inspect uptime-kuma --format '{{range .Mounts}}{{if eq .Destination "/var/run/docker.sock"}}{{.RW}}{{end}}{{end}}')
    if [ "$SOCK_RW" = "false" ]; then
        pass "docker.sock montado como Read-Only (RW: false) en uptime-kuma."
    elif [ "$SOCK_RW" = "true" ]; then
        fail "docker.sock montado como Read-Write (RW: true) en uptime-kuma. Riesgo de escalamiento de privilegios."
        ((TOTAL_FAILURES++))
    else
        info "No se detectó el socket docker.sock montado en uptime-kuma."
    fi
else
    warn "Contenedor uptime-kuma no se encuentra en ejecución."
fi

# ------------------------------------------------------------------------------
# 5. PRIVILEGIOS DE PROCESOS WEB EN CONTENEDORES
# ------------------------------------------------------------------------------
echo -e "\n${COLOR_BOLD}5. Verificando ejecución de procesos sin privilegios de root...${COLOR_RESET}"

# 5.1 GLPI
if docker ps --format '{{.Names}}' | grep -q "^glpi$"; then
    if docker top glpi 2>/dev/null | grep apache2 | grep -v "^\s*root" | grep -q "www-data"; then
        pass "GLPI: Workers de Apache ejecutándose bajo usuario sin privilegios (www-data)."
    else
        fail "GLPI: No se detectaron workers de Apache corriendo bajo usuario www-data."
        ((TOTAL_FAILURES++))
    fi
fi

# 5.2 Snipe-IT
if docker ps --format '{{.Names}}' | grep -q "^snipe-it$"; then
    if docker top snipe-it 2>/dev/null | grep apache2 | grep -v "^\s*root" | grep -q -E "10000|www-data"; then
        pass "Snipe-IT: Workers de Apache ejecutándose bajo UID no-root (10000 / www-data)."
    else
        fail "Snipe-IT: No se detectaron workers de Apache corriendo bajo usuario sin privilegios."
        ((TOTAL_FAILURES++))
    fi
fi

# ------------------------------------------------------------------------------
# RESUMEN FINAL
# ------------------------------------------------------------------------------
echo -e "\n------------------------------------------------------------------------------"
if [ "$TOTAL_FAILURES" -eq 0 ]; then
    echo -e "${COLOR_GREEN}${COLOR_BOLD}RESULTADO FINAL: AUDITORÍA APROBADA (0 hallazgos críticos).${COLOR_RESET}"
    exit 0
else
    echo -e "${COLOR_RED}${COLOR_BOLD}RESULTADO FINAL: SE ENCONTRARON ${TOTAL_FAILURES} OBSERVACIONES CRÍTICAS.${COLOR_RESET}"
    exit 1
fi
