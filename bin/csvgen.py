import csv
import random
import string
import subprocess
import unicodedata
from datetime import datetime, timedelta

CANTIDAD_ACTIVOS = 250
ARCHIVO_SALIDA = "/home/juanx/kayn/import_250_activos_gekko.csv"

# Conjuntos (Hash Sets) para validación estricta de NO repetición (O(1))
nombres_usados = set()
usernames_usados = set()
hostnames_usados = set()
seriales_usados = set()

PRIMEROS_NOMBRES = [
    "Juan", "Mateo", "Santiago", "Nicolás", "Lautaro", "Facundo", "Agustín", "Lucas", "Martín", "Joaquín",
    "Tomás", "Franco", "Ignacio", "Bruno", "Gonzalo", "Sebastián", "Ramiro", "Ezequiel", "Matías", "Federico",
    "Sofía", "Martina", "Valentina", "Camila", "Lucía", "Catalina", "Julieta", "Micaela", "Florencia", "Agustina",
    "Paula", "Antonella", "Victoria", "Delfina", "Malena", "Carolina", "Rocío", "Bianca", "Clara", "Milagros",
    "Alejandro", "Diego", "Leandro", "Mariano", "Patricio"
]

SEGUNDOS_NOMBRES = [
    "Cruz", "Andrés", "Manuel", "Gabriel", "Javier", "Hernán", "Pablo", "Esteban", "Nahuel", "Damián",
    "Emiliano", "Fabián", "Germán", "Iván", "León", "Maximiliano", "Oscar", "Pedro", "Rodrigo", "Simón",
    "Belén", "Soledad", "Inés", "Luján", "Pilar", "Berenice", "Celeste", "Daniela", "Eugenia", "Guadalupe",
    "Helena", "Jimena", "Lorena", "Mercedes", "Natalia", "Oriana", "Romina", "Sabrina", "Tatiana", "Ximena",
    "Gael", "Bautista", "Gino", "Ciro", "Dante"
]

APELLIDOS_1 = [
    "Fernández", "Gómez", "Rodríguez", "González", "López", "Martínez", "Pérez", "Sánchez", "Romero", "Sosa",
    "Torres", "Álvarez", "Ruiz", "Ramírez", "Flores", "Acosta", "Benítez", "Medina", "Suárez", "Herrera",
    "Aguirre", "Pereyra", "Gutiérrez", "Giménez", "Molina", "Silva", "Castro", "Rojas", "Ortiz", "Núñez",
    "Luna", "Juárez", "Cabrera", "Ríos", "Morales", "Godoy", "Moreno", "Ferreira", "Domínguez", "Carrizo",
    "Peralta", "Castillo", "Ledesma", "Quiroga", "Vega", "Vera", "Muñoz", "Ojeda", "Ponce", "Villalba",
    "Cardozo", "Navarro", "Coronel", "Vázquez", "Ramos"
]

APELLIDOS_2 = [
    "Ragonese", "Rossi", "Bianchi", "Ferrari", "Russo", "Colombo", "Ricci", "Marino", "Greco", "Bruno",
    "Gallo", "Conti", "De Luca", "Costa", "Giordano", "Mancini", "Rizzo", "Lombardi", "Moretti", "Barbieri",
    "Fontana", "Santoro", "Mariani", "Rinaldi", "Caruso", "Ferraro", "Fabbri", "Galli", "Martini", "Leone",
    "Longo", "Gentile", "Martinelli", "Vitale", "Lombardo", "Serra", "Coppola", "De Santis", "D'Angelo", "Marchetti",
    "Parisi", "Villa", "Conte", "Ferrara", "Ferri", "Fabbiano", "Valente", "Sorrentino", "Farina", "Bianco",
    "Ibarra", "Bustos", "Ceballos", "Figueroa", "Garay"
]

def limpiar_ascii(texto):
    """Elimina tildes y caracteres especiales para armar usernames y mails limpios."""
    texto_norm = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in texto_norm if not unicodedata.combining(c)]).lower().replace(" ", "").replace("'", "")

def generar_persona_unica():
    """Validador estricto: garantiza que ni el nombre completo ni el username se repitan jamás."""
    while True:
        n1 = random.choice(PRIMEROS_NOMBRES)
        n2 = random.choice([n for n in SEGUNDOS_NOMBRES if n != n1])
        a1 = random.choice(APELLIDOS_1)
        a2 = random.choice([a for a in APELLIDOS_2 if a != a1])

        nombre_completo = f"{n1} {n2} {a1} {a2}"
        if nombre_completo in nombres_usados:
            continue

        # Username formato: inicial1 + inicial2 + . + apellido1 + . + inicial_apellido2 (ej: jc.fernandez.r)
        u_base = f"{limpiar_ascii(n1)[0]}{limpiar_ascii(n2)[0]}.{limpiar_ascii(a1)}.{limpiar_ascii(a2)[0]}"
        username = u_base
        sufijo = 2
        while username in usernames_usados:
            username = f"{u_base}{sufijo}"
            sufijo += 1

        nombres_usados.add(nombre_completo)
        usernames_usados.add(username)
        email = f"{username}@democorp.com"
        return nombre_completo, username, email

def obtener_config_placas():
    cmd = (
        'docker exec -i snipe-mysql sh -c \'mysql -u root -p"$MYSQL_ROOT_PASSWORD" '
        '-N -s snipeit -e "SELECT IFNULL(auto_increment_prefix, \'\'), '
        'IFNULL(next_auto_tag_base, 1), IFNULL(zerofill_count, 5) FROM settings LIMIT 1;"\''
    )
    try:
        salida = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
        partes = salida.split('\t')
        prefijo = partes[0] if len(partes) > 0 else ""
        base = int(partes[1]) if len(partes) > 1 and partes[1].isdigit() else 1
        zerofill = int(partes[2]) if len(partes) > 2 and partes[2].isdigit() else 5
        return prefijo, base, zerofill
    except Exception:
        return "VK-", 1, 5

MODELOS = [
    ("Lenovo", "Lenovo IdeaPad 3", "81RW", ["8GB DDR4", "12GB DDR4"], ["256GB NVMe", "512GB NVMe"], (580, 710), 2),
    ("HP", "HP Victus", "16-D0", ["16GB DDR5", "32GB DDR5"], ["512GB NVMe", "1TB NVMe"], (1250, 1550), 3),
    ("Apple", 'MacBook Pro 14"', 'MacBook Pro 14"', ["16GB Unified", "32GB Unified"], ["512GB SSD", "1TB SSD"], (1850, 2200), 3),
    ("Apple", 'MacBook Pro 14" M4', 'MacBook Pro 14" M4', ["16GB Unified", "24GB Unified", "36GB Unified"], ["512GB SSD", "1TB SSD"], (2100, 2600), 3),
    ("Apple", 'MacBook Pro 13"', 'MacBook Pro 13"', ["8GB Unified", "16GB Unified"], ["256GB SSD", "512GB SSD"], (1290, 1550), 2),
    ("Banghó", "MAX G0101", "G0101 i5", ["8GB DDR4", "16GB DDR4"], ["240GB SSD", "480GB SSD"], (480, 610), 2),
    ("Banghó", "MAX G5", "MAX G5 i7F", ["16GB DDR4"], ["480GB SSD", "512GB NVMe"], (720, 860), 2),
    ("Banghó", "ZERO G0505", "ZERO G0505", ["4GB DDR3", "8GB DDR3"], ["500GB HDD", "240GB SSD"], (320, 410), 1),
    ("Toshiba", "KIRAbook", "KIRAbook", ["8GB DDR3"], ["256GB SSD"], (450, 550), 1),
    ("Dell", "Inspiron 15 3567", "15-3567", ["8GB DDR4"], ["240GB SSD", "1TB HDD"], (460, 560), 1),
    ("Dell", "Inspiron 15", "Inspiron 15", ["8GB DDR4", "16GB DDR4"], ["256GB NVMe", "512GB NVMe"], (600, 740), 2),
    ("Dell", "Inspiron 15 5570", "15-5570", ["8GB DDR4", "16GB DDR4"], ["256GB SSD", "512GB SSD"], (650, 790), 2),
    ("Dell", "Inspiron 15 5566", "15-5566", ["8GB DDR4"], ["240GB SSD", "500GB HDD"], (450, 540), 1),
    ("Dell", "Inspiron 14 3467", "14-3467", ["4GB DDR4", "8GB DDR4"], ["240GB SSD", "500GB HDD"], (430, 520), 1),
    ("Dell", "Inspiron 14 5458", "14-5458", ["8GB DDR3"], ["240GB SSD", "500GB HDD"], (410, 500), 1),
    ("Dell", "Inspiron 15 5578 2-in-1", "15-5578", ["16GB DDR4"], ["512GB SSD"], (780, 920), 2),
    ("Dell", "Inspiron 15 3535", "3535-A813BLK", ["16GB DDR4"], ["512GB NVMe"], (710, 820), 3),
    ("Dell", "Inspiron 15 3520", "3520", ["16GB DDR4"], ["512GB NVMe"], (690, 790), 3),
    ("HP", "HP Laptop 15-ef", "15-ef2126wm", ["8GB DDR4", "12GB DDR4", "16GB DDR4"], ["256GB NVMe", "512GB NVMe"], (560, 680), 2),
    ("HP", "HP Laptop 15-ef", "15-ef2747wm", ["16GB DDR4"], ["512GB NVMe"], (610, 730), 2),
    ("HP", "ProBook 450 G5", "ProBook 450 G5", ["8GB DDR4", "16GB DDR4"], ["256GB NVMe", "512GB NVMe"], (680, 840), 2),
    ("HP", "HP Laptop 15-bs", "15-bs0xx", ["4GB DDR4", "8GB DDR4"], ["500GB HDD", "240GB SSD"], (390, 480), 1),
    ("HP", "HP Laptop 15-bs", "15-bs015dx", ["8GB DDR4"], ["240GB SSD"], (420, 510), 1),
    ("HP", "HP Laptop 15-ay", "15-ay103dx", ["4GB DDR3", "8GB DDR3"], ["500GB HDD", "240GB SSD"], (350, 440), 1),
    ("HP", "HP Laptop 15-bs", "15-bs023la", ["8GB DDR4"], ["240GB SSD", "480GB SSD"], (430, 520), 1),
    ("HP", "HP Laptop 15-bs", "15-bs115dx", ["8GB DDR4", "12GB DDR4"], ["256GB SSD"], (460, 560), 2),
    ("HP", "HP Laptop 15-bs", "15-bs1xx", ["8GB DDR4"], ["240GB SSD"], (440, 530), 1),
    ("HP", "HP 255 G10", "255 G10", ["16GB DDR4"], ["512GB NVMe"], (670, 780), 3),
    ("Lenovo", "IdeaPad 110-15ISK", "110-15ISK", ["4GB DDR4", "8GB DDR4"], ["500GB HDD", "240GB SSD"], (380, 460), 1),
    ("Lenovo", "IdeaPad 320-15ABR", "320-15ABR", ["8GB DDR4"], ["240GB SSD", "1TB HDD"], (410, 500), 1),
    ("Lenovo", "IdeaPad 110-15ACL", "110-15ACL", ["4GB DDR3", "8GB DDR3"], ["500GB HDD"], (340, 420), 1),
    ("Lenovo", "IdeaPad 3 14IIL05", "14IIL05", ["8GB DDR4", "16GB DDR4"], ["256GB NVMe", "512GB NVMe"], (590, 710), 2),
    ("Lenovo", "IdeaPad 3 15IML05", "15IML05", ["8GB DDR4", "12GB DDR4", "16GB DDR4"], ["256GB NVMe", "512GB NVMe"], (610, 730), 2),
    ("Lenovo", "IdeaPad 3 14IML05", "14IML05", ["8GB DDR4", "16GB DDR4"], ["256GB NVMe", "512GB NVMe"], (600, 720), 2),
    ("Lenovo", "IdeaPad 3 15ABA7", "15ABA7", ["16GB DDR4"], ["512GB NVMe"], (680, 790), 3),
    ("Lenovo", "IdeaPad 3 14ITL05", "14ITL05", ["8GB DDR4", "16GB DDR4"], ["256GB NVMe", "512GB NVMe"], (640, 760), 2),
    ("Lenovo", "IdeaPad 3 15ALC6", "15ALC6", ["16GB DDR4"], ["512GB NVMe"], (690, 810), 3),
    ("Lenovo", "Lenovo V330", "V330", ["8GB DDR4", "16GB DDR4"], ["256GB SSD", "512GB SSD"], (540, 670), 2),
    ("Lenovo", "Yoga 9 2-in-1 14ILL10", "14ILL10", ["16GB LPDDR5x", "32GB LPDDR5x"], ["1TB NVMe"], (1550, 1890), 3),
    ("Asus", "VivoBook 16", "M1603QA", ["16GB DDR4"], ["512GB NVMe"], (760, 890), 3),
    ("Asus", "VivoBook 15", "F1504ZA-SB76T", ["16GB DDR4"], ["512GB NVMe"], (730, 850), 3)
]

UBICACIONES_CODIGOS = {
    "OF01 - Patagones": "PAT",
    "CABA - Remoto": "CABA",
    "AMBA - Remoto": "AMBA",
    "Interior - Remoto": "INT",
    "Uruguay": "URU",
    "EEUU": "USA",
    "México": "MEX",
    "España": "ESP"
}

NOTAS_POR_ESTADO = {
    "En uso": [
        "Equipo operativo en producción. Agente de inventario y antivirus activos.",
        "Entregado con cargador original y periféricos. Disco cifrado con BitLocker/FileVault.",
        "Asignado a modalidad remota. Controles de seguridad y parches al día."
    ],
    "Disponible": [
        "Formateado con imagen corporativa base en OF01 - Patagones. Listo para asignación inmediata.",
        "En estantería de stock de IT. Verificado hardware, teclado, cámara y cargador.",
        "Equipo de contingencia (loaner) sanitizado y preparado para entrega."
    ],
    "Pendiente de formateo": [
        "Devolución por offboarding. En cola de laboratorio IT para borrado seguro y reinstalación.",
        "Ingresado a soporte sitio Patagones. Pendiente backup de perfil e imagen limpia."
    ],
    "Obsoleto": [
        "Equipo fuera de ciclo de vida útil. Rendimiento insuficiente para el stack actual.",
        "Batería agotada y desgaste en bisagras. Separado para baja técnica."
    ],
    "Perdido/Robo": [
        "Siniestro reportado. Denuncia policial adjunta en ticket de GLPI y credenciales revocadas."
    ],
    "Reciclado": [
        "Disco extraído y destruido según protocolo. Entregado a reciclaje de RAEE certificado."
    ]
}

def generar_serial_unico(marca):
    """Validador estricto de seriales por fabricante."""
    while True:
        alnum = string.ascii_uppercase + string.digits
        if marca == "Lenovo":
            s = random.choice(["PF", "MP"]) + "".join(random.choices(alnum, k=6))
        elif marca == "Dell":
            s = "".join(random.choices(alnum, k=7))
        elif marca == "HP":
            s = f"{random.choice(['5CD', 'CND'])}{random.randint(0, 5)}{random.randint(10, 52)}" + "".join(random.choices(alnum, k=4))
        elif marca == "Apple":
            s = random.choice(["C02", "J7X", "F8Y"]) + "".join(random.choices(alnum, k=7))
        elif marca == "Asus":
            s = random.choice(["N8N0CV", "R2N0CX", "M4N0CV"]) + "".join(random.choices(string.digits, k=6))
        elif marca == "Banghó":
            s = f"BGH{random.randint(2020, 2025)}{random.randint(10000, 99999)}"
        else:
            s = "9F" + "".join(random.choices(string.digits, k=6)) + random.choice(string.ascii_uppercase)

        if s not in seriales_usados:
            seriales_usados.add(s)
            return s

def generar_hostname_unico(cod_ubi, marca, indice):
    """Validador estricto de Item Name (Hostname) combinando sede, tipo, índice y sufijo hexadecimal."""
    pref_eq = "MAC" if marca == "Apple" else "NB"
    while True:
        sufijo_hex = "".join(random.choices("0123456789ABCDEF", k=2))
        hostname = f"VK-{cod_ubi}-{pref_eq}{str(indice).zfill(3)}-{sufijo_hex}"
        if hostname not in hostnames_usados:
            hostnames_usados.add(hostname)
            return hostname

def elegir_estado_y_ubicacion(era):
    if era == 1:
        estado = random.choices(
            ["En uso", "Disponible", "Pendiente de formateo", "Obsoleto", "Reciclado", "Perdido/Robo"],
            weights=[30, 8, 12, 30, 17, 3], k=1
        )[0]
    elif era == 2:
        estado = random.choices(
            ["En uso", "Disponible", "Pendiente de formateo", "Obsoleto", "Reciclado", "Perdido/Robo"],
            weights=[74, 12, 9, 2, 1, 2], k=1
        )[0]
    else:
        estado = random.choices(
            ["En uso", "Disponible", "Pendiente de formateo", "Perdido/Robo"],
            weights=[82, 12, 5, 1], k=1
        )[0]

    if estado in ["Disponible", "Pendiente de formateo", "Obsoleto", "Reciclado"]:
        ubicacion = random.choices(
            ["OF01 - Patagones", "CABA - Remoto", "Uruguay", "México"],
            weights=[85, 8, 4, 3], k=1
        )[0]
    else:
        ubicacion = random.choices(
            ["CABA - Remoto", "AMBA - Remoto", "OF01 - Patagones", "Interior - Remoto", "Uruguay", "México", "España", "EEUU"],
            weights=[30, 26, 15, 12, 6, 5, 3, 3], k=1
        )[0]

    return estado, ubicacion

def generar_fecha_compra(era):
    rangos = {
        1: (datetime(2019, 3, 1), datetime(2021, 12, 20)),
        2: (datetime(2022, 1, 10), datetime(2024, 6, 30)),
        3: (datetime(2024, 7, 1), datetime(2026, 8, 15))
    }
    inicio, fin = rangos[era]
    dias = (fin - inicio).days
    return (inicio + timedelta(days=random.randint(0, dias))).strftime("%Y-%m-%d")

def main():
    prefijo, base_num, zerofill = obtener_config_placas()
    print(f"[+] Configuración detectada -> Prefijo: '{prefijo}' | Base: {base_num} | Zerofill: {zerofill}")

    columnas = [
        "Asset Tag", "Item Name", "Category", "Manufacturer",
        "Model Name", "Model Number", "Serial", "Status",
        "Location", "Purchase Date", "Purchase Cost",
        "Warranty Months", "Full Name", "Username", "Email", "RAM", "Notes"
    ]

    conteo_estados = {}

    with open(ARCHIVO_SALIDA, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columnas)

        for i in range(1, CANTIDAD_ACTIVOS + 1):
            num_actual = base_num + i - 1
            asset_tag = f"{prefijo}{str(num_actual).zfill(zerofill)}"

            marca, mod_nombre, mod_num, rams, discos, rango_costo, era = random.choice(MODELOS)
            estado, ubicacion = elegir_estado_y_ubicacion(era)
            conteo_estados[estado] = conteo_estados.get(estado, 0) + 1

            cod_ubi = UBICACIONES_CODIGOS[ubicacion]
            item_name = generar_hostname_unico(cod_ubi, marca, i)
            serial = generar_serial_unico(marca)
            ram = random.choice(rams)
            disco = random.choice(discos)
            fecha_compra = generar_fecha_compra(era)

            costo = f"{random.uniform(rango_costo[0], rango_costo[1]):.2f}" if random.random() < 0.75 else ""
            garantia = 24 if era == 3 else 12
            obs_base = random.choice(NOTAS_POR_ESTADO[estado])

            # Si el activo está "En uso", le asignamos un colaborador único validado
            if estado == "En uso":
                full_name, username, email = generar_persona_unica()
                notas = f"Asignado a: {full_name} ({email}) | RAM: {ram} | Disco: {disco}. {obs_base}"
            else:
                full_name, username, email = "", "", ""
                notas = f"RAM: {ram} | Disco: {disco}. {obs_base}"

            writer.writerow([
                asset_tag, item_name, "Notebook", marca,
                mod_nombre, mod_num, serial, estado,
                ubicacion, fecha_compra, costo,
                garantia, full_name, username, email, ram, notas
            ])

    # Auditoría post-generación en consola
    print(f"[✔] Archivo generado: {ARCHIVO_SALIDA}")
    print(f"[✔] Validación de Unicidad -> Hostnames únicos: {len(hostnames_usados)}/250 | Seriales únicos: {len(seriales_usados)}/250 | Personas únicas asignadas: {len(nombres_usados)}")
    print("\nResumen por estado:")
    for est, cant in sorted(conteo_estados.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {est}: {cant}")

if __name__ == "__main__":
    main()
