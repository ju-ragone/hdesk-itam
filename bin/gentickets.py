#!/usr/bin/env python3
import sys
import random
import requests
from datetime import datetime, timedelta

# ==========================================
# CONFIGURACIÓN DE CONEXIÓN A GLPI API
# ==========================================
GLPI_URL = "http://localhost:9080/apirest.php"
USER_TOKEN = "DhKBxmN1EmhZMcHnL7ycYh7vX62rvqUDwUwCZ1or"
APP_TOKEN = "BW0tTg3QI5OKs9t9MoIVZeWouOj94Zv4WCqAqOkG"

# Solicitantes permitidos (Excluidos Juan Cruz IDs 2 y 9, y cuentas técnicas)
REQUESTER_IDS = [7, 8, 3, 5]  # egaray, fduarte, post-only, normal

# ==========================================
# GENERADORES DE DATOS DINÁMICOS
# ==========================================
def rand_asset():
    prefix = random.choice(["LNV-T14", "DLL-5430", "HP-840G8", "MON-DELL24", "MBL-MOTO50"])
    return f"{prefix}-{random.randint(1000, 9999)}"

def rand_ip():
    subnet = random.choice(["10.10.20", "10.10.50", "192.168.10", "172.16.4"])
    return f"{subnet}.{random.randint(15, 250)}"

def rand_mac():
    return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)]).upper()

def rand_date_recent():
    days_ago = random.randint(1, 5)
    dt = datetime.now() - timedelta(days=days_ago)
    return dt.strftime("%d/%m/%Y")

# ==========================================
# 1. CAT 5: HARDWARE > NOTEBOOKS Y PERIFÉRICOS
# (Formulario: Solicitud de nuevo equipamiento con "Es visible si...")
# ==========================================
def gen_cat5_equipamiento():
    motivos = [
        "Rotura o desperfecto",
        "Obsolencia",
        "No es compatible con mi trabajo",
        "Robo",
        "Pérdida",
        "Requerimiento del cliente",
        "Es una solicitud del cliente"
    ]
    equipos_pool = ["Celular", "Monitor", "Mouse", "Cargador", "Notebook"]
    motivo = random.choice(motivos)
    
    # Selección coherente de equipos según el motivo
    if motivo in ["Obsolencia", "No es compatible con mi trabajo"]:
        seleccion = ["Notebook"] if random.random() < 0.7 else ["Notebook", "Monitor"]
    elif motivo in ["Robo", "Pérdida"]:
        seleccion = random.sample(["Notebook", "Celular", "Cargador", "Mouse"], k=random.randint(1, 2))
    else:
        seleccion = random.sample(equipos_pool, k=random.randint(1, 3))

    equipos_str = ", ".join(seleccion)
    
    # Campos condicionales ("Es visible si...") según el motivo elegido
    if motivo == "Rotura o desperfecto":
        asset = rand_asset()
        falla = random.choice([
            "Bisagra izquierda quebrada al abrir la tapa y marco desprendido.",
            "Falla eléctrica en puerto de carga USB-C; no reconoce ningún transformador.",
            "Derrame accidental de líquido sobre el teclado; varias teclas en cortocircuito.",
            "Batería interna inflamada que levanta el touchpad y recalienta el chasis.",
            "Pantalla con líneas verticales fijas tras golpe en traslado."
        ])
        condicional_html = (
            f"<b>[Sección Condicional: Reporte de Siniestro / Desperfecto]</b><br>"
            f"<b>Etiqueta de Activo (Snipe-IT):</b> {asset}<br>"
            f"<b>Diagnóstico físico preliminar:</b> {falla}<br>"
            f"<b>¿Requiere equipo de backup inmediato?:</b> {'Sí' if 'Notebook' in seleccion else 'No'}<br>"
        )
        urg, imp = (4, 3) if "Notebook" in seleccion else (2, 2)

    elif motivo in ["Obsolencia", "No es compatible con mi trabajo"]:
        asset = rand_asset()
        limitacion = random.choice([
            "Los 8GB/16GB de RAM actuales se saturan al levantar contenedores Docker y entornos locales.",
            "El procesador actual genera cuellos de botella severos al compilar proyectos y correr VMs.",
            "Almacenamiento NVMe al 98% de capacidad sin posibilidad de expansión en este modelo.",
            "La placa gráfica integrada no soporta el renderizado requerido por el software del proyecto."
        ])
        spec_req = random.choice([
            "Notebook gama alta (32GB RAM, Procesador i7/Ryzen 7, 1TB SSD)",
            "Workstation móvil con soporte multipantalla 1440p",
            "Equipo estándar actualizado (16GB RAM DDR5, 512GB NVMe)"
        ])
        condicional_html = (
            f"<b>[Sección Condicional: Evaluación de Rendimiento Técnico]</b><br>"
            f"<b>Equipo actual a reemplazar:</b> {asset}<br>"
            f"<b>Limitación técnica detectada:</b> {limitacion}<br>"
            f"<b>Perfil de hardware requerido:</b> {spec_req}<br>"
        )
        urg, imp = random.choice([(1, 1), (2, 2)])

    elif motivo in ["Robo", "Pérdida"]:
        asset = rand_asset()
        lugar = random.choice(["Vía pública (traslado a oficina)", "Transporte público", "Cafetería / Espacio de coworking", "Estacionamiento"])
        denuncia = f"DEN-2026-{random.randint(10000, 99999)}"
        condicional_html = (
            f"<b>[Sección Condicional: Siniestro por Robo / Extravío]</b><br>"
            f"<b>Activo afectado:</b> {asset}<br>"
            f"<b>Fecha del incidente:</b> {rand_date_recent()}<br>"
            f"<b>Lugar del hecho:</b> {lugar}<br>"
            f"<b>Nº de Denuncia Policial adjunta:</b> {denuncia}<br>"
            f"<b>Estado de seguridad:</b> Se solicita bloqueo remoto por MDM y revocación de certificados VPN.<br>"
        )
        urg, imp = (4, 4)

    else:  # Requerimiento del cliente / Es una solicitud del cliente
        cliente = random.choice(["Banco Galicia", "MercadoLibre", "YPF Digital", "Telecom", "Globant", "Prisma Medios de Pago"])
        ceco = f"CC-{random.randint(400, 999)}-{cliente[:3].upper()}"
        aprobador = random.choice(["Gerencia de Operaciones", "Director de Cuenta", "Líder de Proyecto (PMO)"])
        condicional_html = (
            f"<b>[Sección Condicional: Imputación a Proyecto / Cliente]</b><br>"
            f"<b>Cliente / Cuenta destino:</b> {cliente}<br>"
            f"<b>Centro de Costos (CECO):</b> {ceco}<br>"
            f"<b>Aprobado por:</b> {aprobador}<br>"
            f"<b>Modalidad de entrega:</b> {'Envío a domicilio por logística' if random.random() < 0.5 else 'Retiro presencial en oficina de IT'}<br>"
        )
        urg, imp = (3, 3)

    title = f"Solicitud de nuevo equipamiento ({equipos_str}) - {motivo}"
    body = (
        f"<b>[Formulario: Solicitud de nuevo equipamiento]</b><br>"
        f"<b>Motivo de solicitud:</b> {motivo}<br>"
        f"<b>Equipo requerido:</b> {equipos_str}<br><hr>"
        f"{condicional_html}"
        f"<i>Nota: Solicitud sujeta a revisión y aprobación del área de Infraestructura.</i>"
    )
    return 5, title, body, urg, imp

# ==========================================
# 2. CAT 6: HARDWARE > IMPRESORAS Y MONITORES
# ==========================================
def gen_cat6_impresoras_monitores():
    tipo = random.choice(["Impresora", "Monitor"])
    if tipo == "Impresora":
        modelo = random.choice(["HP LaserJet Enterprise M611", "Brother MFC-L8900CDW", "Ricoh MP 402SPF", "Lexmark MX521"])
        sector = random.choice(["Piso 1 - Administración", "Piso 2 - RRHH", "Piso 3 - Operaciones", "Recepción Central"])
        problema = random.choice([
            ("Atasco de papel recurrente en la unidad fusora (Código de error 13.B9.D2)", 3, 3),
            ("Tóner negro agotado al 0% y cartel de reemplazo de unidad de imagen", 2, 2),
            ("Impresora fuera de línea en el servidor de impresión; no responde ping en red", 4, 3),
            ("Manchas verticales de tóner en todas las hojas impresas desde la bandeja 2", 2, 2)
        ])
        title = f"Incidencia en {modelo} ({sector}) - {problema[0][:35]}..."
        body = (
            f"<b>[Formulario: Soporte de Impresión y Periféricos de Sala]</b><br>"
            f"<b>Equipo:</b> {modelo}<br>"
            f"<b>Ubicación física:</b> {sector}<br>"
            f"<b>IP asignada:</b> {rand_ip()}<br>"
            f"<b>Falla reportada:</b> {problema[0]}<br>"
        )
        return 6, title, body, problema[1], problema[2]
    else:
        modelo = random.choice(["Dell 24\" P2422H", "Samsung Curvo 27\"", "Xiaomi 27\" 1440p", "LG UltraWide 29\""])
        falla = random.choice([
            ("Pérdida intermitente de señal por puerto HDMI / DisplayPort", 3, 2),
            ("Fuente de alimentación interna no enciende (LED de standby apagado)", 3, 3),
            ("Franja de píxeles muertos en el panel central", 2, 2)
        ])
        title = f"Falla de Monitor externo {modelo} - {falla[0][:30]}..."
        body = (
            f"<b>[Formulario: Soporte de Monitores]</b><br>"
            f"<b>Modelo de monitor:</b> {modelo}<br>"
            f"<b>Etiqueta de Inventario:</b> {rand_asset()}<br>"
            f"<b>Detalle del problema:</b> {falla[0]}<br>"
            f"<b>Pruebas realizadas por el usuario:</b> Se probó cambiando el cable HDMI y conectando a otra notebook sin éxito.<br>"
        )
        return 6, title, body, falla[1], falla[2]

# ==========================================
# 3. CAT 7: REDES > VPN Y ACCESO REMOTO
# ==========================================
def gen_cat7_vpn():
    cliente_vpn = random.choice(["FortiClient VPN", "OpenVPN Connect", "WireGuard Corporativo", "Cisco AnyConnect"])
    escenarios = [
        ("Error de negociación TLS / Handshake timeout en el 40% de conexión", "ISP domiciliario bloqueando puerto UDP o cambio de MTU.", 4, 3),
        ("Credenciales rechazadas tras validación de token MFA", "Desincronización con el servidor RADIUS / Active Directory.", 4, 4),
        ("Túnel VPN conecta pero sin ruteo a servidores internos (VLAN Producción)", "Falta empuje de rutas estáticas (split-tunneling) en el perfil del usuario.", 4, 4),
        ("Caída masiva de sesiones en concentrador VPN principal", "Saturación de sesiones concurrentes en el firewall de borde.", 5, 5),
        ("Error de certificado digital expirado o no confiable en equipo nuevo", "Falta instalar el certificado CA raíz corporativo en el almacén del sistema.", 3, 3)
    ]
    esc = random.choice(escenarios)
    isp = random.choice(["Personal Flow", "Movistar Fibra", "Telecentro", "Claro Fibra", "Iplan"])
    title = f"Falla {cliente_vpn}: {esc[0][:45]}"
    body = (
        f"<b>[Formulario: Conectividad VPN y Teletrabajo]</b><br>"
        f"<b>Cliente VPN utilizado:</b> {cliente_vpn}<br>"
        f"<b>Proveedor de Internet (ISP):</b> {isp}<br>"
        f"<b>IP local / túnel:</b> {rand_ip()}<br>"
        f"<b>Síntoma exacto:</b> {esc[0]}<br>"
        f"<b>Causa preliminar sospechada:</b> {esc[1]}<br>"
    )
    return 7, title, body, esc[2], esc[3]

# ==========================================
# 4. CAT 8: REDES > WI-FI Y RED LOCAL
# ==========================================
def gen_cat8_wifi_lan():
    zona = random.choice(["Piso 1 - Isla de Soporte", "Piso 2 - Desarrollo", "Sala de Directorio", "Depósito de IT / Laboratorio", "Comedor"])
    medio = random.choice(["Wi-Fi Corporativo (802.1X)", "Red Cableada Ethernet (Puesto de trabajo)"])
    problemas = [
        ("Sin respuesta de servidor DHCP (Equipo toma IP APIPA 169.254.x.x)", 4, 4),
        ("Pérdida de paquetes superior al 35% y latencia alta hacia el Gateway", 4, 3),
        ("Access Point sin luz de estado (posible caída de puerto PoE en Switch)", 5, 4),
        ("Boca de red física sin link en roseta de pared (requiere parcheo en rack)", 3, 2),
        ("Desconexiones constantes en videollamadas por solapamiento de canales 5GHz", 3, 3)
    ]
    prob = random.choice(problemas)
    title = f"Problema de red en {zona}: {prob[0][:40]}"
    body = (
        f"<b>[Formulario: Infraestructura de Red Local y Wi-Fi]</b><br>"
        f"<b>Ubicación / Sector:</b> {zona}<br>"
        f"<b>Tipo de conexión:</b> {medio}<br>"
        f"<b>Dirección MAC del equipo:</b> {rand_mac()}<br>"
        f"<b>Incidente reportado:</b> {prob[0]}<br>"
    )
    return 8, title, body, prob[1], prob[2]

# ==========================================
# 5. CAT 9: ACCESOS > BLANQUEO DE CONTRASEÑA
# ==========================================
def gen_cat9_blanqueo():
    sistema = random.choice([
        "Active Directory (Inicio de sesión Windows)",
        "Cuenta de Correo Corporativo / Microsoft 365",
        "Portal de Gestión ERP / SAP",
        "GitLab / Repositorio de Código",
        "Consola de Inventario Snipe-IT"
    ])
    causa = random.choice([
        ("Cuenta bloqueada automáticamente tras 5 intentos fallidos (clave anterior cacheada en celular)", 4, 3),
        ("Olvido de contraseña al reincorporarse de licencia por vacaciones", 3, 2),
        ("Cambio de teléfono móvil; requiere reseteo de semilla MFA / Google Authenticator", 4, 3),
        ("Contraseña expirada por política de seguridad de 90 días que no permitió cambio en pantalla", 3, 3)
    ])
    title = f"Blanqueo / Desbloqueo de cuenta: {sistema}"
    body = (
        f"<b>[Formulario: Blanqueo de Credenciales y MFA]</b><br>"
        f"<b>Plataforma / Sistema afectado:</b> {sistema}<br>"
        f"<b>Motivo del bloqueo:</b> {causa[0]}<br>"
        f"<b>Verificación de identidad:</b> Validada mediante supervisor directo.<br>"
    )
    return 9, title, body, causa[1], causa[2]

# ==========================================
# 6. CAT 10: ACCESOS > ONBOARDING / OFFBOARDING
# ==========================================
def gen_cat10_onboarding():
    tramite = random.choice(["Alta de Nuevo Ingreso (Onboarding)", "Baja de Colaborador (Offboarding)", "Cambio de Rol / Transferencia"])
    nombres = ["Lucía Domínguez", "Martín Pereyra", "Sofía Benítez", "Nicolás Cabrera", "Valentina Ríos", " Julián Moretti", "Camila Villalba"]
    empleado = random.choice(nombres)
    area = random.choice(["Desarrollo Backend", "QA & Testing", "Infraestructura y DevOps", "Finanzas", "Recursos Humanos", "Mesa de Ayuda"])
    
    if "Alta" in tramite:
        grupos = "GRP_VPN_USERS, GRP_DEV_GITLAB, GRP_M365_E3" if "Desarrollo" in area or "Infra" in area else "GRP_VPN_USERS, GRP_M365_BASIC, GRP_ERP_READ"
        urg, imp = (3, 3)
        detalle = (
            f"<b>Fecha de ingreso:</b> {(datetime.now() + timedelta(days=random.randint(2, 7))).strftime('%d/%m/%Y')}<br>"
            f"<b>Grupos de Active Directory a asignar:</b> {grupos}<br>"
            f"<b>¿Requiere preparación de Notebook en depósito?:</b> Sí (Perfil {area})<br>"
        )
    elif "Baja" in tramite:
        urg, imp = (4, 4)
        detalle = (
            f"<b>Fecha efectiva de desvinculación:</b> {datetime.now().strftime('%d/%m/%Y')} 18:00 hs<br>"
            f"<b>Acciones críticas:</b> Bloqueo inmediato de AD, cierre de sesiones activas en VPN/M365 y redirección de buzón a líder de área.<br>"
            f"<b>Recupero de activos:</b> Coordinar retiro de equipo {rand_asset()} con logística.<br>"
        )
    else:
        urg, imp = random.choice([(1, 1), (2, 2)])
        detalle = (
            f"<b>Nuevo rol asignado:</b> Analista Senior en {area}<br>"
            f"<b>Ajuste de permisos:</b> Mantener cuenta actual pero actualizar membresías de grupos en AD y carpetas compartidas.<br>"
        )

    title = f"{tramite}: {empleado} ({area})"
    body = (
        f"<b>[Formulario: Movimiento de Personal - RRHH / IT]</b><br>"
        f"<b>Tipo de operación:</b> {tramite}<br>"
        f"<b>Colaborador:</b> {empleado}<br>"
        f"<b>Departamento / Área:</b> {area}<br><hr>"
        f"{detalle}"
    )
    return 10, title, body, urg, imp

# ==========================================
# 7. CAT 11: SOFTWARE > CORREO Y SUITE OFIMÁTICA
# ==========================================
def gen_cat11_ofimatica():
    casos = [
        ("Buzón de correo lleno al 99% (50 GB); rebota recepción de correos externos", "Correo Corporativo", 4, 3),
        ("Solicitud de permisos de lectura y envío ('Send As') en buzón compartido", "Buzón Compartido (administracion@ / soporte@)", 2, 2),
        ("Archivo de datos local (.OST) corrupto; Outlook se cierra al sincronizar bandeja", "Microsoft Outlook", 3, 3),
        ("Falla de micrófono y cámara virtual al iniciar reuniones grupales", "Microsoft Teams / Google Meet", 3, 2),
        ("Bloqueo de macros y complementos contables por política de seguridad", "Planillas de Cálculo (Excel)", 3, 3)
    ]
    c = random.choice(casos)
    title = f"Soporte Ofimática ({c[1]}): {c[0][:40]}..."
    body = (
        f"<b>[Formulario: Correo y Herramientas de Colaboración]</b><br>"
        f"<b>Aplicación:</b> {c[1]}<br>"
        f"<b>Equipo del usuario:</b> {rand_asset()}<br>"
        f"<b>Descripción del inconveniente:</b> {c[0]}<br>"
    )
    return 11, title, body, c[2], c[3]

# ==========================================
# 8. CAT 12: SOFTWARE > SISTEMAS INTERNOS
# ==========================================
def gen_cat12_sistemas():
    sistemas = [
        ("Snipe-IT (Gestión de Activos)", "Error 500 al intentar generar el acta de asignación en PDF para una notebook.", 3, 3),
        ("Servidor GitLab Interno", "Falla en los runners de CI/CD; los pipelines quedan en estado 'pending' indefinidamente.", 4, 4),
        ("ERP de Facturación y Compras", "Caída de base de datos transaccional (Error SQLSTATE[HY000] [2002] Connection refused).", 5, 5),
        ("Entorno Docker / Virtualización", "Solicitud de permisos de administrador local para levantar demonios de contenedores y red bridge.", 2, 2),
        ("Portal GLPI / Catálogo", "Error de permisos de visualización en la bandeja de tickets del grupo técnico.", 3, 3),
        ("Sistema de Monitoreo Zabbix", "Falsos positivos de alerta por timeout de agente SNMP en switches de acceso.", 2, 3)
    ]
    s = random.choice(sistemas)
    title = f"Incidencia en {s[0]}: {s[1][:42]}..."
    body = (
        f"<b>[Formulario: Sistemas Internos y Herramientas de Gestión]</b><br>"
        f"<b>Plataforma afectada:</b> {s[0]}<br>"
        f"<b>Entorno:</b> {'Producción' if s[2] >= 4 else 'Operaciones Internas'}<br>"
        f"<b>Detalle técnico del reporte:</b> {s[1]}<br>"
        f"<b>Host / IP de referencia:</b> {rand_ip()}<br>"
    )
    return 12, title, body, s[2], s[3]

# Lista ponderada de generadores (le damos más peso al formulario de equipamiento Cat 5 para testearlo a fondo)
GENERATORS = [
    gen_cat5_equipamiento,
    gen_cat5_equipamiento,  # Doble peso para ver todas las ramas condicionales de equipamiento
    gen_cat6_impresoras_monitores,
    gen_cat7_vpn,
    gen_cat8_wifi_lan,
    gen_cat9_blanqueo,
    gen_cat10_onboarding,
    gen_cat11_ofimatica,
    gen_cat12_sistemas
]

# ==========================================
# FUNCIONES DE INTERACCIÓN CON LA REST API
# ==========================================
def init_session():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"user_token {USER_TOKEN}",
        "App-Token": APP_TOKEN
    }
    res = requests.get(f"{GLPI_URL}/initSession", headers=headers)
    if res.status_code != 200:
        print(f"[!] Error iniciando sesión en GLPI API ({res.status_code}): {res.text}")
        sys.exit(1)
    return res.json().get("session_token")

def kill_session(session_token):
    headers = {
        "Content-Type": "application/json",
        "Session-Token": session_token,
        "App-Token": APP_TOKEN
    }
    requests.get(f"{GLPI_URL}/killSession", headers=headers)

def create_ticket(session_token, requester_id, generator_func, seen_titles, attempt=1):
    cat_id, title, content, urgency, impact = generator_func()
    
    # Si en la misma ráfaga sale el mismo título base, le agregamos el identificador de activo o ticket ref para garantizar unicidad
    if title in seen_titles and attempt <= 3:
        return create_ticket(session_token, requester_id, generator_func, seen_titles, attempt + 1)
    if title in seen_titles:
        title = f"{title} [Ref #{random.randint(100, 999)}]"
    seen_titles.add(title)

    payload = {
        "input": {
            "name": title,
            "content": content,
            "itilcategories_id": cat_id,
            "urgency": urgency,
            "impact": impact,
            "_users_id_requester": requester_id
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Session-Token": session_token,
        "App-Token": APP_TOKEN
    }
    
    res = requests.post(f"{GLPI_URL}/Ticket", headers=headers, json=payload)
    if res.status_code == 201:
        return res.json().get("id"), title, cat_id, urgency, impact
    else:
        print(f"[!] Error creando ticket: {res.status_code} - {res.text}")
        return None, None, None, None, None

def main():
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            count = None
    else:
        print("=== GENERADOR AVANZADO DE TICKETS GLPI ===")
        print("Ráfagas soportadas sugeridas: 5, 10, 20, 40, 60, 70, 100")
        try:
            count = int(input("Ingresá la cantidad de tickets a generar: "))
        except (ValueError, KeyboardInterrupt):
            print("\nOperación cancelada.")
            sys.exit(0)

    if not count or count <= 0:
        print("[!] Cantidad inválida.")
        sys.exit(1)

    print(f"\n[+] Iniciando sesión vía REST API en {GLPI_URL}...")
    session_token = init_session()
    print(f"[✓] Sesión establecida correctamente.")
    print(f"[+] Disparando ráfaga de {count} tickets combinatorios...\n")

    exitos = 0
    seen_titles = set()
    stats_cat = {}

    for i in range(1, count + 1):
        requester = random.choice(REQUESTER_IDS)
        gen_func = random.choice(GENERATORS)
        
        t_id, title, cat_id, urg, imp = create_ticket(session_token, requester, gen_func, seen_titles)
        if t_id:
            exitos += 1
            stats_cat[cat_id] = stats_cat.get(cat_id, 0) + 1
            print(f"[{i:03d}/{count:03d}] Ticket #{t_id:<4} | Cat: {cat_id:<2} | U:{urg}/I:{imp} | Req: {requester} | {title}")
        else:
            print(f"[{i:03d}/{count:03d}] Falló la creación del ticket.")

    print(f"\n[+] Cerrando sesión...")
    kill_session(session_token)
    print(f"[✓] Finalizado: {exitos}/{count} tickets generados exitosamente.")
    print(f"[i] Distribución por categoría ITIL (ID): {dict(sorted(stats_cat.items()))}")

if __name__ == "__main__":
    main()
