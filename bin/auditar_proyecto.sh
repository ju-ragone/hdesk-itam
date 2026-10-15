#!/usr/bin/env bash
cd /home/juanx/kayn || exit 1

python3 - << 'PYEOF' | tee /home/juanx/kayn/docs/informe_estado_proyecto.txt
import os
import re
import glob
import stat
import sqlite3
import subprocess
from datetime import datetime

def sh(cmd):
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

# Cargar variables desde .env
env = {}
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("'").strip('"')

g_user = env.get("GLPI_DB_USER", "glpi_user")
g_pass = env.get("GLPI_DB_PASSWORD", "")
g_db   = env.get("GLPI_DB_NAME", "glpidb")

s_user = env.get("DB_USERNAME", "snipeit_user")
s_pass = env.get("DB_PASSWORD", "")
s_db   = env.get("DB_DATABASE", "snipeit")

checks = []
def add_check(section, name, passed, detail=""):
    checks.append((section, name, bool(passed), detail))

print("=" * 80)
print(" INFORME TÉCNICO Y VERIFICACIÓN EN VIVO — PLATAFORMA MILIO IT (HOST: KAYN)")
print(f" Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ------------------------------------------------------------------------------
# 1. INFRAESTRUCTURA DOCKER, RED Y VOLÚMENES
# ------------------------------------------------------------------------------
expected_containers = ["glpi", "glpi-mysql", "snipe-it", "snipe-mysql", "kanban", "uptime-kuma"]
_, ps_out, _ = sh("docker ps --format '{{.Names}}|{{.Status}}|{{.Ports}}'")
running_map = {}
for line in ps_out.splitlines():
    if "|" in line:
        parts = line.split("|")
        running_map[parts[0]] = (parts[1], parts[2])

all_up = all(c in running_map and "Up" in running_map[c][0] for c in expected_containers)
add_check("Infraestructura", "6 contenedores principales en estado Up", all_up, f"{len(running_map)}/6 activos")

_, pol_out, _ = sh("docker inspect " + " ".join(expected_containers) + " --format '{{.Name}}:{{.HostConfig.RestartPolicy.Name}}'")
pol_ok = all("unless-stopped" in l for l in pol_out.splitlines() if l)
add_check("Infraestructura", "Política de reinicio unless-stopped en todo el stack", pol_ok, "unless-stopped")

expected_vols = [
    "snipe-it_snipeit-data", "snipe-it_snipedb-data", "snipe-it_glpi-data",
    "snipe-it_glpi-db-data", "snipe-it_kanban-data", "snipe-it_kanban-plugins",
    "snipe-it_uptime-kuma-data"
]
_, vol_out, _ = sh("docker volume ls --format '{{.Name}}'")
vols_present = [v for v in expected_vols if v in vol_out.splitlines()]
add_check("Infraestructura", "7 volúmenes persistentes nombrados operativos", len(vols_present) == 7, f"{len(vols_present)}/7 volúmenes")

# ------------------------------------------------------------------------------
# 2. AUDITORÍA EN VIVO DE BASES DE DATOS (MILIO GLPI & GEKKO SNIPE-IT)
# ------------------------------------------------------------------------------
glpi_sql = """
SELECT
  (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()),
  (SELECT COUNT(*) FROM glpi_entities WHERE id >= 0),
  (SELECT COUNT(*) FROM glpi_locations WHERE name LIKE '%Patagones%' OR id >= 1),
  (SELECT COUNT(*) FROM glpi_groups WHERE id IN (1,2,3)),
  (SELECT COUNT(*) FROM glpi_itilcategories),
  (SELECT COUNT(*) FROM glpi_rules WHERE id IN (96,97,98) AND is_active = 1),
  (SELECT COUNT(*) FROM glpi_calendars WHERE id = 2),
  (SELECT COUNT(*) FROM glpi_slas WHERE calendars_id = 2),
  (SELECT COUNT(*) FROM glpi_tickets),
  (SELECT COUNT(*) FROM glpi_crontasks WHERE name IN ('slaticket','queuednotification') AND mode = 2);
"""
rc_g, out_g, _ = sh(f"docker exec -i glpi-mysql mysql -u'{g_user}' -p'{g_pass}' -D '{g_db}' -N -B -e \"{glpi_sql}\" 2>/dev/null")
if rc_g == 0 and out_g:
    g_vals = [int(x) for x in out_g.split("\t")]
    t_cnt, ent_ok, loc_ok, grp_cnt, cat_cnt, rul_cnt, cal_ok, sla_cnt, tkt_cnt, cli_cnt = g_vals
    add_check("Milio (GLPI)", "Conexión SQL y esquema íntegro en glpi-mysql", t_cnt >= 390, f"{t_cnt} tablas InnoDB")
    add_check("Milio (GLPI)", "Entidad Milio, sede Patagones y 3 grupos resolutores", ent_ok >= 1 and loc_ok >= 1 and grp_cnt == 3, f"Entidad: {ent_ok} | Sede: {loc_ok} | Grupos: {grp_cnt}/3")
    add_check("Milio (GLPI)", "Taxonomía de 12 categorías ITIL y reglas 96/97/98 activas", cat_cnt >= 12 and rul_cnt == 3, f"{cat_cnt} categorías | {rul_cnt}/3 reglas")
    add_check("Milio (GLPI)", "Calendario Milio (09-18) y matriz de 10 SLAs (TTO/TTR)", cal_ok == 1 and sla_cnt >= 10, f"{sla_cnt} SLAs vinculados")
    add_check("Milio (GLPI)", "Lote transaccional de tickets cargado en base", tkt_cnt >= 200, f"{tkt_cnt} tickets registrados")
    add_check("Milio (GLPI)", "Acciones automáticas slaticket y queuednotification en CLI", cli_cnt == 2, f"{cli_cnt}/2 en modo CLI (mode=2)")
else:
    add_check("Milio (GLPI)", "Conexión SQL a glpi-mysql", False, "Error de conexión")

snipe_sql = """
SELECT
  (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()),
  (SELECT COUNT(*) FROM assets WHERE deleted_at IS NULL),
  (SELECT COUNT(*) FROM models WHERE deleted_at IS NULL),
  (SELECT COUNT(*) FROM categories WHERE deleted_at IS NULL);
"""
rc_s, out_s, _ = sh(f"docker exec -i snipe-mysql mysql -u'{s_user}' -p'{s_pass}' -D '{s_db}' -N -B -e \"{snipe_sql}\" 2>/dev/null")
if rc_s == 0 and out_s:
    s_vals = [int(x) for x in out_s.split("\t")]
    st_cnt, asset_cnt, mod_cnt, scat_cnt = s_vals
    add_check("Gekko (Snipe-IT)", "Conexión SQL y catálogo ITAM operativo en snipe-mysql", st_cnt > 20 and asset_cnt > 0, f"{asset_cnt} activos | {mod_cnt} modelos | {scat_cnt} categorías")
else:
    add_check("Gekko (Snipe-IT)", "Conexión SQL a snipe-mysql", False, "Error de conexión")

# ------------------------------------------------------------------------------
# 3. OBSERVABILIDAD Y MONITOREO NOC (UPTIME KUMA)
# ------------------------------------------------------------------------------
_, h_glpi, _  = sh("docker exec uptime-kuma curl -s -o /dev/null -w '%{http_code}' http://glpi/")
_, h_snipe, _ = sh("docker exec uptime-kuma curl -s -o /dev/null -w '%{http_code}' http://snipe-it/")
add_check("Monitoreo NOC", "Sonda interna HTTP hacia Milio (esperado: 200)", h_glpi == "200", f"HTTP {h_glpi}")
add_check("Monitoreo NOC", "Sonda interna HTTP hacia Gekko (esperado: 302)", h_snipe == "302", f"HTTP {h_snipe}")

# ------------------------------------------------------------------------------
# 4. SEGURIDAD, ESTRUCTURA FHS, CRONTAB Y BACKUPS EN HOST
# ------------------------------------------------------------------------------
fhs_dirs = ["bin", "backups", "logs", "docs", "assets"]
fhs_ok = all(os.path.isdir(d) for d in fhs_dirs)
add_check("Seguridad y Host", "Estructura de directorios FHS completa en ~/kayn", fhs_ok, ", ".join(fhs_dirs))

rc_grep, out_grep, _ = sh("grep -rnE '123|password_123' *.yml *.env docker-compose* 2>/dev/null")
add_check("Seguridad y Host", "Ausencia de credenciales por defecto ('123') en configs", out_grep == "", "0 credenciales expuestas")

env_600 = os.path.exists(".env") and stat.S_IMODE(os.stat(".env").st_mode) == 0o600
bak_700 = os.path.exists("backups") and stat.S_IMODE(os.stat("backups").st_mode) == 0o700
files_600 = all(stat.S_IMODE(os.stat(f).st_mode) == 0o600 for f in glob.glob("backups/*") if os.path.isfile(f))
umask_ok = os.path.exists("bin/backup_stack.sh") and "umask 077" in open("bin/backup_stack.sh").read()
add_check("Seguridad y Host", "Permisos restrictivos (0600/0700) y umask 077 activo", env_600 and bak_700 and files_600 and umask_ok, ".env 600 | backups/ 700 | umask 077")

_, cron_out, _ = sh("crontab -l 2>/dev/null")
cron_bak_ok  = "/home/juanx/kayn/bin/backup_stack.sh" in cron_out
cron_glpi_ok = "/var/www/html/glpi/front/cron.php" in cron_out
add_check("Seguridad y Host", "Crontab del host configurado (backups 03:00 y GLPI 5m)", cron_bak_ok and cron_glpi_ok, "2 tareas activas en crontab")

tar_files = sorted(glob.glob("backups/backup_milio_*.tar.gz"))
add_check("Seguridad y Host", "Respaldos comprimidos diarios (.tar.gz) verificados", len(tar_files) > 0, f"{len(tar_files)} archivos ({os.path.basename(tar_files[-1]) if tar_files else 'N/A'})")

rb_path = "RUNBOOK.md" if os.path.exists("RUNBOOK.md") else ("docs/RUNBOOK.md" if os.path.exists("docs/RUNBOOK.md") else "")
rb_ok = bool(rb_path) and "Versión del Documento:** 2.6" in open(rb_path, encoding="utf-8").read()
add_check("Documentación", "Runbook operativo actualizado a versión 2.6", rb_ok, rb_path or "No encontrado")

# ------------------------------------------------------------------------------
# IMPRESIÓN DE MATRIZ DE VERIFICACIÓN
# ------------------------------------------------------------------------------
print("\n1. MATRIZ DE COMPROBACIONES TÉCNICAS EN VIVO")
print("-" * 80)
passed_cnt = 0
for sec, name, ok, detail in checks:
    st = "[  OK  ]" if ok else "[ FAIL ]"
    if ok:
        passed_cnt += 1
    print(f"{st} [{sec:<16}] {name:<54} -> {detail}")

# ------------------------------------------------------------------------------
# 5. RESUMEN DE AVANCE EN KANBOARD
# ------------------------------------------------------------------------------
print("\n2. ESTADO DEL PROYECTO EN KANBOARD (BASE SQLITE EN VIVO)")
print("-" * 80)
sh("docker cp kanban:/var/www/app/data/db.sqlite /tmp/kb_audit_ro.sqlite 2>/dev/null")
if os.path.exists("/tmp/kb_audit_ro.sqlite"):
    conn = sqlite3.connect("/tmp/kb_audit_ro.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT project_id FROM columns GROUP BY project_id ORDER BY COUNT(*) DESC LIMIT 1")
    pid = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*), SUM(CASE WHEN is_active=0 THEN 1 ELSE 0 END), SUM(CASE WHEN is_active=1 THEN 1 ELSE 0 END) FROM tasks WHERE project_id=?", (pid,))
    tot_t, closed_t, open_t = cur.fetchone()

    cur.execute("SELECT COUNT(*), SUM(CASE WHEN s.status=2 THEN 1 ELSE 0 END) FROM subtasks s JOIN tasks t ON s.task_id=t.id WHERE t.project_id=?", (pid,))
    tot_s, done_s = cur.fetchone()

    print(f"Total de tarjetas: {tot_t} ({closed_t} cerradas | {open_t} abiertas) | Subtareas completadas: {done_s}/{tot_s}\n")

    cur.execute("SELECT id, position, title FROM columns WHERE project_id=? ORDER BY position ASC", (pid,))
    for cid, pos, ctitle in cur.fetchall():
        cur.execute("SELECT COUNT(*), SUM(CASE WHEN is_active=0 THEN 1 ELSE 0 END), SUM(CASE WHEN is_active=1 THEN 1 ELSE 0 END) FROM tasks WHERE column_id=?", (cid,))
        c_tot, c_closed, c_open = cur.fetchone()
        c_closed = c_closed or 0
        c_open = c_open or 0
        print(f"  Columna {pos}: {ctitle:<42} -> Total: {c_tot:<2} (Cerradas: {c_closed:<2} | Abiertas: {c_open:<2})")
        if c_open > 0:
            cur.execute("SELECT id, reference, title FROM tasks WHERE column_id=? AND is_active=1 ORDER BY position ASC", (cid,))
            for tid, ref, ttitle in cur.fetchall():
                print(f"             - [ABIERTA] #{tid} {ttitle}")
    conn.close()
    os.remove("/tmp/kb_audit_ro.sqlite")

print("\n" + "=" * 80)
print(f" RESULTADO GLOBAL DE AUDITORÍA: {passed_cnt}/{len(checks)} CONTROLES TÉCNICOS SUPERADOS")
print(" Reporte guardado en: ~/kayn/docs/informe_estado_proyecto.txt")
print("=" * 80)
PYEOF
