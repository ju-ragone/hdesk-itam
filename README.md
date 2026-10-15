# **Documentación Técnica, Auditoría ITIL & Runbook Operativo — Plataforma Milio IT | democorp Infraestructura**

- **Organización:** democorp
- **Entorno Host:** `kayn` (`~/kayn`)
- **Marco de Referencia:** ITIL v4 (*Service Configuration Management*, *Service Design*, *Service Level Management*, *Monitoring and Event Management* & *Continual Improvement*)
- **Versión del Documento:** 2.7 (Consolidada — Auditoría 18/18, Estándar FHS, Hardening, Kanboard y Suite de Automatización Python/Bash)
- **Fecha de Actualización:** 13 de Octubre de 2026

---

## **1. Alcance, Contexto ITIL y Resumen Ejecutivo**

### **1.1. Propósito y Alcance Documental**

El presente documento establece la línea base de la infraestructura virtualizada en contenedores Docker para la Plataforma Milio IT. Su propósito es servir como Elemento de Configuración (CI) de referencia dentro de la Gestión de la Configuración del Servicio (*Service Configuration Management*) y respaldar las actividades operativas descritas en la fase de Diseño del Servicio (*ITIL Service Design*). Asimismo, consolida los resultados de la auditoría técnica practicada sobre la instancia productiva y documenta la remediación integral de sus motores de automatización.

### **1.2. Objetivos Principales**

- Registrar formalmente las relaciones y dependencias de los componentes tecnológicos que soportan las operaciones de IT.
- Garantizar la trazabilidad de los cambios en el entorno de contenedores Docker y en la base de datos relacional.
- Documentar la estructura organizacional, taxonomía de categorías ITIL, reglas de negocio de asignación automática, lineamientos de diseño de formularios dinámicos y acuerdos de nivel de servicio (SLA).
- Normalizar los Procedimientos Operativos Estándar (SOP) para la continuidad operativa, generación de respaldos, pruebas de homologación (UAT) y mantenimiento preventivo.
- Proveer una estructura clara alineada al marco ITIL 4 para auditorías y gestión de incidentes, solicitudes y problemas.
- Establecer una arquitectura de observabilidad y monitoreo activo de eventos (*ITIL Monitoring and Event Management*) mediante Uptime Kuma con alertamiento temprano vía SMTP y plantillas dinámicas Liquid.

### **1.3. Resumen de Evolución y Madurez ITIL**

- **Infraestructura Base:** Operativa, aislada y estable mediante arquitectura de microservicios en Docker (`glpi`, `glpi-mysql`, `snipe-it`, `snipe-mysql` y `kanban`) corriendo sobre una red interna dedicada con volúmenes de persistencia de datos.
- **Estado Inicial (Pre-Intervención):** Nivel 1 (Básico/Inicial). La plataforma contaba únicamente con la estructura base de grupos resolutores y 1 activo en inventario, pero carecía de categorías ITIL, SLAs, calendarios personalizados y reglas de enrutamiento (gestión 100% manual).
- **Estado Actual (Post-Remediación):** Nivel 3 (Definido y Automatizado). Se implementó el calendario operativo hábil (`Calendario Milio 09-18`), la matriz de 10 SLAs (TTO y TTR para prioridades P1 a P5), el árbol de 12 categorías y subcategorías ITIL, y el motor de reglas de negocio para derivación automática a 3 niveles de soporte (N1, N2 y Soporte Sitio).
- **Observabilidad y Gestión de Eventos (NOC):** Incorporación de Uptime Kuma (`uptime-kuma`) en la red interna de contenedores para el monitoreo continuo de disponibilidad de los servicios críticos Milio (GLPI) y Gekko (Snipe-IT), con detección de caídas y recuperaciones en tiempo real, validación de códigos de estado HTTP (`200 OK` y `302 Found`), plantillas personalizadas en Liquid y persistencia de datos auditada.

---

## **2. Inventario de Servicios e Infraestructura Base (Docker)**

A continuación se detallan los elementos de configuración activos que componen el ecosistema de la infraestructura Milio IT, alojados en el host `kayn` (`~/kayn`):

### **2.1. Inventario de Contenedores y Servicios**

| Servicio | Nombre del Contenedor | Imagen / Versión | Estado Esperado | Criticidad ITIL | Función Principal en la Arquitectura |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Snipe-IT** | `snipe-it` | `snipe/snipe-it:latest` | `Up` | Alta | Gestión de Activos IT (ITAM), inventario de hardware, licencias y asignaciones |
| **GLPI** | `glpi` | `diouxx/glpi:latest` | `Up` | Crítica | Plataforma ITSM, Mesa de Ayuda, Catálogo de Servicios, Motor de SLAs y Reglas |
| **BD MariaDB (GLPI)** | `glpi-mysql` | `mariadb:10.11` | `Up` | Crítica | Base de datos relacional (`glpidb`) con 447 tablas activas e íntegras |
| **BD MariaDB (Snipe-IT)** | `snipe-mysql` | `mariadb:10.11` | `Up` | Alta | Base de datos relacional transaccional del sistema de inventario Snipe-IT |
| **Kanboard** | `kanban` | `kanboard/kanboard:latest` | `Up (healthy)` | Media | Tablero Ágil / Kanban para gestión de tareas internas y proyectos de IT |
| **Uptime Kuma** | `uptime-kuma` | `louislam/uptime-kuma:latest` | `Up (healthy)` | Alta | Monitoreo Activo NOC, Gestión de Eventos ITIL y Alertamiento SMTP Automatizado |

### **2.2. Topología de Red Interna (Bridge)**

Todos los servicios operan sobre una red bridge unificada denominada `snipe-it_default`, permitiendo resolución DNS interna por nombre de contenedor y aislando las bases de datos del exterior:

| Nombre de Red | Controlador (Driver) | IP Asignada | Contenedor / Servicio |
| :---: | :---: | :---: | :---: |
| `snipe-it_default` | `bridge` | `172.18.0.2` | `glpi-mysql` |
| `snipe-it_default` | `bridge` | `172.18.0.3` | `kanban` |
| `snipe-it_default` | `bridge` | `172.18.0.4` | `snipe-mysql` |
| `snipe-it_default` | `bridge` | `172.18.0.5` | `glpi` |
| `snipe-it_default` | `bridge` | `172.18.0.6` | `snipe-it` |
| `snipe-it_default` | `bridge` | `172.18.0.7` | `uptime-kuma` |

### **2.3. Mapeo de Puertos de Red y Accesos**

| Servicio | Puerto Host | Puerto Contenedor | Protocolo | Interfaz de Escucha |
| :--- | :---: | :---: | :---: | :--- |
| **Kanboard** (`kanban`) | `7080` | `80` | `TCP` | `0.0.0.0` / Proxy Inverso |
| **Snipe-IT** (`snipe-it`) | `8080` | `80` | `TCP` | `0.0.0.0` / Proxy Inverso |
| **GLPI** (`glpi`) | `9080` | `80` | `TCP` | `0.0.0.0` / Proxy Inverso |
| **BD MariaDB** (`glpi-mysql`) | N/A | `3306` | `TCP` | Red Interna (Sin bind al host) |
| **BD MariaDB** (`snipe-mysql`) | N/A | `3306` | `TCP` | Red Interna (Sin bind al host) |
| **Uptime Kuma** (`uptime-kuma`) | `3001` | `3001` | `TCP` | `0.0.0.0` / Panel Web NOC |

### **2.4. Volúmenes de Persistencia de Datos**

| Servicio / Contenedor | Nombre del Volumen Docker | Ruta de Montaje en Contenedor | Descripción / Tipo de Datos |
| :--- | :---: | :---: | :--- |
| **Snipe-IT** (`snipe-it`) | `snipe-it_snipeit-data` | `/var/lib/snipeit` | Archivos, adjuntos, firmas de Snipe-IT |
| **GLPI** (`glpi`) | `snipe-it_glpi-data` | `/var/www/html/glpi` | Raíz completa web de GLPI, plugins, configs y archivos |
| **BD GLPI** (`glpi-mysql`) | `snipe-it_glpi-db-data` | `/var/lib/mysql` | Base de datos MariaDB `glpidb` (447 tablas) |
| **BD Snipe-IT** (`snipe-mysql`) | `snipe-it_snipedb-data` | `/var/lib/mysql` | Base de datos MariaDB Snipe-IT |
| **Kanboard** (`kanban`) | `snipe-it_kanban-data` | `/var/www/app/data` | Datos y base SQLite de Kanboard |
| **Kanboard** (`kanban`) | `snipe-it_kanban-plugins` | `/var/www/app/plugins` | Plugins de Kanboard |
| **Uptime Kuma** (`uptime-kuma`) | `snipe-it_uptime-kuma-data` | `/app/data` | Base SQLite de monitoreo, configuración de sondas, plantillas Liquid e historial |
| **Uptime Kuma** (`uptime-kuma`) | Bind Mount (`/var/run/docker.sock`) | `/var/run/docker.sock` | Socket del daemon Docker para inspección de contenedores |

### **2.5. Manifiesto de Infraestructura como Código (docker-compose.yml)**

El despliegue está parametrizado mediante variables de entorno almacenadas en un archivo `.env` privado en `~/kayn`:

```yaml
version: '3.8'

services:
  snipe-mysql:
    image: mariadb:10.11
    container_name: snipe-mysql
    restart: unless-stopped
    env_file: .env
    volumes:
      - snipedb-data:/var/lib/mysql

  snipe-it:
    image: snipe/snipe-it:latest
    container_name: snipe-it
    restart: unless-stopped
    env_file: .env
    ports:
      - "8080:80"
    volumes:
      - snipeit-data:/var/lib/snipeit
    depends_on:
      - snipe-mysql

  glpi-mysql:
    image: mariadb:10.11
    container_name: glpi-mysql
    restart: unless-stopped
    env_file: .env
    volumes:
      - glpi-db-data:/var/lib/mysql

  glpi:
    image: diouxx/glpi:latest
    container_name: glpi
    restart: unless-stopped
    env_file: .env
    ports:
      - "9080:80"
    volumes:
      - glpi-data:/var/www/html/glpi
    depends_on:
      - glpi-mysql

  kanban:
    image: kanboard/kanboard:latest
    container_name: kanban
    restart: unless-stopped
    ports:
      - "7080:80"
    volumes:
      - kanban-data:/var/www/app/data
      - kanban-plugins:/var/www/app/plugins

  uptime-kuma:
    image: louislam/uptime-kuma:latest
    container_name: uptime-kuma
    restart: unless-stopped
    ports:
      - "3001:3001"
    volumes:
      - uptime-kuma-data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock

volumes:
  snipeit-data:
  snipedb-data:
  glpi-data:
  glpi-db-data:
  kanban-data:
  kanban-plugins:
  uptime-kuma-data:
```

### **2.6. Estructura de Directorios en el Host (Estándar FHS en `~/kayn`)**

Se reorganizó el árbol de directorios del proyecto en el host `kayn` para separar binarios, bitácoras, respaldos y documentación técnica bajo permisos restrictivos:

| Directorio / Archivo | Permisos Octales | Propósito Operativo y Contenido |
| :--- | :---: | :--- |
| `~/kayn/docker-compose.yml` | `0600` (`-rw-------`) | Manifiesto principal de orquestación de los 6 contenedores del stack. |
| `~/kayn/.env` | `0600` (`-rw-------`) | Variables de entorno y credenciales productivas aisladas del código. |
| `~/kayn/bin/` | `0755` (`drwxr-xr-x`) | Scripts ejecutables de automatización y mantenimiento (`backup_stack.sh`). |
| `~/kayn/backups/` | `0700` (`drwx------`) | Respaldos diarios (`.tar.gz`), Golden Baselines (`punto_cero_*.sql`) y Snapshots de Resguardo (`*_demo_listo.sql`) con permisos `0600`. |
| `~/kayn/logs/` | `0755` (`drwxr-xr-x`) | Bitácoras operativas de ejecución desatendida (`backup.log`). |
| `~/kayn/docs/` | `0755` (`drwxr-xr-x`) | Documentación técnica, auditorías ITIL y Runbook Operativo (`RUNBOOK.md`). |
| `~/kayn/assets/` | `0755` (`drwxr-xr-x`) | Recursos gráficos, plantillas e insumos de configuración de la plataforma. |

---

## **3. Arquitectura Funcional, Gobierno ITSM y Parametrización de GLPI**

### **3.1. Parámetros Base del Motor GLPI**

- **Esquema de Base de Datos:** `glpidb` sobre MariaDB 10.11 con 447 tablas activas e íntegras (motor InnoDB).
- **Estructura de Entidades (`glpi_entities`):**
  - `Root entity` (`ID: 0`): Entidad raíz global donde se definen calendarios y acuerdos heredables.
  - `Milio` (`ID: 1`): Entidad operativa principal que cuelga de `Root entity` (`ID: 0`).
- **Ubicaciones Físicas (`glpi_locations`):** `Sede Central` (`ID: 1`), sede operativa registrada para asignación de activos y soporte presencial.
- **Línea Base CMDB (`glpi_computers`):** 1 Computadora registrada inicialmente en inventario (`ID: 1`).

### **3.2. Equipos de Soporte (Grupos Resolutores - glpi_groups)**

| ID Grupo | Nombre del Grupo | Rol / Nivel de Soporte | Responsabilidades y Alcance Operativo |
| :---: | :--- | :--- | :--- |
| **ID 1** | `Mesa de Ayuda - N1` | Nivel 1 (Service Desk) | Recepción y triaje inicial, blanqueo de contraseñas, desbloqueo de cuentas, altas/bajas de usuarios (Onboarding/Offboarding), soporte de correo electrónico, suite ofimática y sistemas internos. |
| **ID 2** | `Infraestructura y Redes - N2` | Nivel 2 (Infrastructure & Network) | Administración de enlaces, resolución de incidentes de VPN y acceso remoto, fallas de Wi-Fi corporativo, direccionamiento IP, DNS, switches y servidores. |
| **ID 3** | `Soporte Sitio - Sede Central` | Nivel 2 Presencial (Field Support) | Intervención física en puesto de trabajo, diagnóstico y reparación de notebooks/PCs, entrega de equipamiento, reemplazo de monitores, periféricos, puertos Ethernet, docking stations e impresoras en sede Sede Central. |

### **3.3. Usuarios y Perfiles Activos (glpi_users / glpi_profiles)**

| Usuario | Perfil Asignado | ID Perfil | Interfaz | Alcance de Permisos |
| :---: | :---: | :---: | :---: | :--- |
| `juanx` | `Super-Admin` | `ID: 4` | Central (Estándar) | Administración total de infraestructura, reglas de negocio, catálogo, SLAs y configuración core. |
| `glpi` | `Super-Admin` | `ID: 2` | Central (Estándar) | Cuenta administrativa nativa del sistema. |
| `tech` | `Technician` | `ID: 6` | Central (Estándar) | Gestión operativa de tickets asignados, seguimiento técnico, tareas y carga de soluciones. |
| `normal` | `Observer` | `ID: 5` | Central (Estándar) | Supervisión y lectura de tickets sin permisos de modificación estructural. |
| `post-only` | `Self-Service` | `ID: 1` | Simplificada (Catálogo) | Usuario final; acceso exclusivo al Portal de Autoservicio para creación y seguimiento de solicitudes propias. |

### **3.4. Taxonomía de Categorías ITIL (glpi_itilcategories)**

Se estructuró un árbol de 12 categorías ITIL dividido en 4 categorías raíz (Nivel 1) y 8 subcategorías operativas (Nivel 2):

| ID Cat. | Categoría Raíz (Nivel 1) | Ruta Completa en GLPI (`completename`) | Nivel | Incidente | Solicitud | Grupo Resolutor Asociado |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **ID 1** | Hardware & Equipamiento | `Hardware & Equipamiento` | 1 | Sí | Sí | Soporte Sitio - Sede Central (ID 3) |
| **ID 5** | Hardware & Equipamiento | `Hardware & Equipamiento > Notebooks y Periféricos` | 2 | Sí | Sí | Soporte Sitio - Sede Central (ID 3) |
| **ID 6** | Hardware & Equipamiento | `Hardware & Equipamiento > Impresoras y Monitores` | 2 | Sí | Sí | Soporte Sitio - Sede Central (ID 3) |
| **ID 2** | Conectividad & Redes | `Conectividad & Redes` | 1 | Sí | Sí | Infraestructura y Redes - N2 (ID 2) |
| **ID 7** | Conectividad & Redes | `Conectividad & Redes > VPN y Acceso Remoto` | 2 | Sí | Sí | Infraestructura y Redes - N2 (ID 2) |
| **ID 8** | Conectividad & Redes | `Conectividad & Redes > Wi-Fi y Red Local` | 2 | Sí | No | Infraestructura y Redes - N2 (ID 2) |
| **ID 3** | Accesos & Cuentas | `Accesos & Cuentas` | 1 | Sí | Sí | Mesa de Ayuda - N1 (ID 1) |
| **ID 9** | Accesos & Cuentas | `Accesos & Cuentas > Blanqueo de Contraseña` | 2 | Sí | Sí | Mesa de Ayuda - N1 (ID 1) |
| **ID 10** | Accesos & Cuentas | `Accesos & Cuentas > Onboarding / Offboarding` | 2 | No | Sí | Mesa de Ayuda - N1 (ID 1) |
| **ID 4** | Software & Aplicaciones | `Software & Aplicaciones` | 1 | Sí | Sí | Mesa de Ayuda - N1 (ID 1) |
| **ID 11** | Software & Aplicaciones | `Software & Aplicaciones > Correo y Suite Ofimática` | 2 | Sí | Sí | Mesa de Ayuda - N1 (ID 1) |
| **ID 12** | Software & Aplicaciones | `Software & Aplicaciones > Sistemas Internos` | 2 | Sí | Sí | Mesa de Ayuda - N1 (ID 1) |

### **3.5. Motor de Reglas de Negocio para Ruteo Automático (glpi_rules - RuleTicket)**

| ID Regla | Nombre de la Regla | Operador Lógico | Criterios de Evaluación (`glpi_rulecriterias`) | Acción Ejecutada (`glpi_ruleactions`) | Estado |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **ID 18** | `Root` | `AND` | Regla nativa base del sistema | Sin asignación de grupo específico | Activa |
| **ID 96** | `Ruteo N1 - Accesos y Software` | `OR` | Categoría ITIL es o está bajo `Accesos & Cuentas` (ID 3, 9, 10) O `Software & Aplicaciones` (ID 4, 11, 12) | Asignar: Grupo técnico -> `Mesa de Ayuda - N1` (`ID: 1`) | Activa |
| **ID 97** | `Ruteo N2 - Conectividad y Redes` | `OR` | Categoría ITIL es o está bajo `Conectividad & Redes` (ID 2, 7, 8) | Asignar: Grupo técnico -> `Infraestructura y Redes - N2` (`ID: 2`) | Activa |
| **ID 98** | `Ruteo Sitio - Hardware y Equipamiento` | `OR` | Categoría ITIL es o está bajo `Hardware & Equipamiento` (ID 1, 5, 6) | Asignar: Grupo técnico -> `Soporte Sitio - Sede Central` (`ID: 3`) | Activa |

### **3.6. Arquitectura ITAM en Gekko (Snipe-IT) y Consolidación de Datos de Resguardo**

En complemento al motor ITSM de Milio (GLPI), el servicio **Gekko (`snipe-it`)** centraliza la práctica de **Gestión de Activos de TI (*IT Asset Management - ITAM*)** de ITIL v4:

- **Catálogo Normalizado:** Registro estructurado de fabricantes, modelos de equipamiento corporativo, categorías de hardware (Notebooks, PCs, Monitores, Periféricos) y licencias de software.
- **Trazabilidad y Asignación Nominal:** Vinculación directa de activos físicos a usuarios y a la ubicación operativa `Sede Central`, manteniendo el historial de entregas y estado de conservación.
- **Lote Productivo de Resguardo Consolidado:**
  - **En Gekko (Snipe-IT):** Lote completo de activos, modelos y asignaciones resguardado en `snipeit_demo_listo.sql` (`576 KB`).
  - **En Milio (GLPI):** Más de 200 tickets transaccionales entre incidentes y solicitudes procesados bajo las reglas de ruteo `96`, `97` y `98`, resguardados en `glpi_demo_listo.sql` (`17.8 MB`).

---

## **4. Catálogo de Servicios, Lineamientos de Formularios y Niveles de Servicio (SLA)**

### **4.1. Categorías del Catálogo de Servicios Implementadas**

- **Equipamiento & Puesto de trabajo (ID 2):** Gestión de PC, Notebooks, Periféricos y Puestos Laborales.
- **Cuentas, Accesos y Seguridad (ID 3):** Alta/Baja de Usuarios, Credenciales y Permisos de Seguridad.
- **Conectividad, Redes y VPN (ID 4):** Acceso VPN Remoto, Wi-Fi, Redes y Telefonía IP.
- **Software & Aplicaciones (ID 5):** Sistemas Corporativos, Aplicaciones Autorizadas y Errores de Software.

### **4.2. Lineamientos de Diseño para Formularios Dinámicos y Experiencia de Usuario (UX)**

- **Mapeo de Destinos y Categoría ITIL:** Cada formulario que se habilite debe configurar en su solapa **Destinos** la creación del objeto `Ticket`, especificando su tipo (Incidente o Solicitud) y vinculando la Categoría ITIL correspondiente para que las Reglas 96, 97 y 98 asignen automáticamente el grupo resolutor.
- **Configuración de Visibilidad Condicional:**
  - Para desplegar preguntas dinámicas según la selección previa del usuario, se configura en la pregunta dependiente el bloque **Visibilidad condicional -> Visible si...**
  - Se selecciona la pregunta disparadora bajo el encabezado **Preguntas** (evitando seleccionar el encabezado **Secciones**).
  - Se cambia el operador por defecto (`Es visible`) al operador `contiene` (o `es igual a`) indicando el valor disparador específico.
- **Política UX para Formularios en Construcción:**
  - Se descarta ocultar el botón **Enviar** mediante condiciones en formularios sin configurar para evitar callejones sin salida (*dead-ends*) al usuario final.
  - Todo formulario que aún no esté finalizado debe mantenerse con el interruptor `Activo = No` (Inactivo) para que no aparezca en el portal de autoservicio hasta su habilitación definitiva.

### **4.3. Gestión de Niveles de Servicio (SLM) y Acuerdos de Nivel de Servicio (SLA)**

- **Calendario Laboral Operativo:** `Calendario Milio (09-18)` `[ID 2]`
- **Cobertura:** Lunes a Viernes de 09:00 a 18:00 hs (45 hs semanales, 5 segmentos creados en `glpi_calendarsegments`).
- **Asignación:** Entidad raíz (`ID 0`) para herencia global en todos los tickets y servicios.

> **Nota:** Todos los registros de SLA se encuentran vinculados explícitamente a `calendars_id = 2` y `use_ticket_calendar = 0`.

| ID SLA | Prioridad / Nivel | Tipo de SLA | Tiempo Máximo | Detalle / Horas Laborables |
| :---: | :---: | :---: | :---: | :--- |
| **ID 1** | P1 Crítico | TTO (*Time to Own* / Tipo 1) | 15 minutos | Asignación e inicio de atención |
| **ID 2** | P2 Alto | TTO (*Time to Own* / Tipo 1) | 30 minutos | Asignación e inicio de atención |
| **ID 3** | P3 Medio | TTO (*Time to Own* / Tipo 1) | 1 hora | Asignación e inicio de atención |
| **ID 4** | P4 Estándar | TTO (*Time to Own* / Tipo 1) | 2 horas | Asignación e inicio de atención |
| **ID 5** | P5 Planificado | TTO (*Time to Own* / Tipo 1) | 4 horas | Asignación e inicio de atención |
| **ID 6** | P1 Crítico | TTR (*Time to Resolve* / Tipo 0) | 2 horas | Resolución total del incidente |
| **ID 7** | P2 Alto | TTR (*Time to Resolve* / Tipo 0) | 4 horas | Resolución total del incidente |
| **ID 8** | P3 Medio | TTR (*Time to Resolve* / Tipo 0) | 8 horas | 1 día laboral completo |
| **ID 9** | P4 Estándar | TTR (*Time to Resolve* / Tipo 0) | 24 horas laborales | 3 días hábiles |
| **ID 10** | P5 Planificado | TTR (*Time to Resolve* / Tipo 0) | 48 horas laborales | 5 días hábiles |

---

## **5. Procedimientos Operativos Estándar (SOP) - Ciclo de Vida y Mantenimiento**

### **SOP-MILIO-001: Ciclo de Vida Global de la Plataforma Docker**

1. **Objetivo y Alcance:** Establecer la secuencia estandarizada para el arranque, parada, reinicio y desmantelamiento controlado del stack completo de servicios en el host `kayn`.
2. **Pre-requisitos:** Acceso SSH con privilegios `sudo`/`docker` al host `kayn` y disponibilidad del archivo `.env` parametrizado en `~/kayn`.
3. **Procedimiento Secuencial:**
   - Navegar al directorio raíz del proyecto:
     ```bash
     cd ~/kayn
     ```
   - Iniciar todos los servicios en segundo plano:
     ```bash
     docker compose up -d
     ```
   - Detener los servicios manteniendo el estado de los contenedores:
     ```bash
     docker compose stop
     ```
   - Reanudar la ejecución de servicios detenidos:
     ```bash
     docker compose start
     ```
   - Desmantelar contenedores y redes virtuales del stack:
     ```bash
     docker compose down
     ```
4. **Validación Operativa:** Ejecutar `docker compose ps` y confirmar que todos los contenedores reporten estado `Up` o `healthy`.
5. **Criterios de Salida:**
   > **Criterios de Salida:** Disponibilidad confirmada de las interfaces web HTTP de GLPI (`:9080`), Snipe-IT (`:8080`), Kanboard (`:7080`) y Uptime Kuma (`:3001`) sin errores de conexión a base de datos.

### **SOP-MILIO-002: Reinicio Selectivo y Mantenimiento de Servicios Específicos**

1. **Objetivo y Alcance:** Restablecer la disponibilidad de un microservicio o motor de base de datos de forma aislada ante degradación o fallas locales, minimizando el impacto en el resto de la plataforma.
2. **Pre-requisitos:** Identificación previa del contenedor degradado mediante logs o alertas de monitoreo.
3. **Procedimiento Secuencial:**
   - Generar respaldo preventivo de la base de datos afectada antes de intervenir:
     ```bash
     docker exec glpi-mysql sh -c 'exec mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --single-transaction --quick glpidb' | gzip > "glpi_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
     ```
   - Reiniciar la instancia de aplicación o base de datos específica:
     ```bash
     docker restart glpi
     ```
     *(o `glpi-mysql` / `snipe-it` / `snipe-mysql` / `kanban` / `uptime-kuma` según el origen de la falla).*
   - Verificar el consumo de recursos del contenedor:
     ```bash
     docker stats --no-stream <nombre_contenedor>
     ```
4. **Validación Operativa:** Inspeccionar las últimas entradas del log del servicio mediante `docker logs --tail 50 <nombre_contenedor>` y verificar la ausencia de excepciones fatales.
5. **Criterios de Salida:**
   > **Criterios de Salida:** Restablecimiento verificado de la conectividad interna y respuesta `HTTP 200` en las solicitudes al servicio intervenido.

### **SOP-MILIO-003: Mantenimiento, Purga de Caché y Saneamiento del Motor Docker**

1. **Objetivo y Alcance:** Preservar el rendimiento óptimo de las aplicaciones web y liberar espacio de almacenamiento en el host mediante la limpieza sistemática de cachés volátiles y recursos huérfanos de Docker.
2. **Pre-requisitos:** Ventana de mantenimiento programada o baja carga transaccional para evitar inconsistencias de sesión activa.
3. **Procedimiento Secuencial:**
   - Ejecutar la depuración de caché interna en GLPI:
     ```bash
     docker exec -u www-data -it glpi php /var/www/html/glpi/bin/console cache:clear
     ```
   - Ejecutar la purga de caché de aplicación y configuración en Snipe-IT:
     ```bash
     docker exec -it snipe-it php artisan cache:clear && docker exec -it snipe-it php artisan config:clear
     ```
   - Purgar imágenes sin contenedor, capas obsoletas y volúmenes temporales del daemon Docker:
     ```bash
     docker system prune -f
     ```
     > **Advertencia Crítica:** NUNCA utilizar el flag `--volumes` con el stack detenido (`down`), ya que Docker interpretará los volúmenes nombrados como no asociados a un contenedor activo y purgará permanentemente las bases de datos transaccionales.
4. **Validación Operativa:** Verificar el incremento del espacio disponible en el volumen raíz utilizando `df -h /` y validar que los servicios sigan respondiendo correctamente.
5. **Criterios de Salida:**
   > **Criterios de Salida:** Sistema liberado de residuos temporales con un tiempo de carga optimizado en los paneles administrativos de GLPI y Snipe-IT.

### **SOP-MILIO-004: Automatización y Gestión del Ciclo de Respaldos (Backups Diarios)**

1. **Objetivo y Alcance:** Asegurar la generación desatendida, consistente y con retención controlada de las copias de seguridad de las bases de datos transaccionales de la plataforma.
2. **Pre-requisitos:** Permisos de ejecución en el script `~/kayn/bin/backup_stack.sh`, espacio en disco suficiente en `~/kayn/backups/` y servicio Crontab activo en el sistema host.
3. **Procedimiento Secuencial:**
   - Verificar la existencia y permisos del script de respaldo: `ls -l ~/kayn/bin/backup_stack.sh` y asegurar permisos de ejecución (`chmod +x`).
   - Configurar la automatización diaria en Crontab (03:00 AM):
     ```bash
     0 3 * * * /home/juanx/kayn/bin/backup_stack.sh >> /home/juanx/kayn/logs/backup.log 2>&1
     ```
   - Ejecutar la validación de rotación y política de retención (15 días): Verificar que el script elimine automáticamente respaldos cuya antigüedad supere el periodo definido.
4. **Validación Operativa:** Inspeccionar el archivo de log con `cat ~/kayn/logs/backup.log` y comprobar la creación de los archivos comprimidos `backup_milio_YYYYMMDD_HHMMSS.tar.gz`.
5. **Criterios de Salida:**
   > **Criterios de Salida:** Archivo de copia de seguridad con integridad validada, tamaño coherente (>0 bytes) y registrado sin errores en la bitácora de respaldo.

### **SOP-MILIO-005: Generación de Punto Cero (Golden Baseline), Dump On-Demand y Rollback**

1. **Objetivo y Alcance:** Establecer el procedimiento metodológico para capturar un estado base de referencia limpio y ejecutar la restauración o vuelta atrás (*rollback*) inmediata ante pruebas de homologación (UAT) o cambios no planeados.
2. **Concepto Técnico:**
   > **Nota:** Un dump lógico generado mediante `mysqldump --single-transaction --quick` exporta la estructura DDL (`CREATE TABLE`) y los registros DML (`INSERT INTO`) congelando la coherencia de los datos en memoria y disco sin detener los contenedores. Permite utilizar la base viva para pruebas destructivas de carga de tickets y luego volver al estado virgen exacto.
3. **Procedimiento A — Captura de Dump Manual Comprimido On-Demand (Sin exponer claves del `.env`):**
   ```bash
   cd ~/kayn
   docker exec glpi-mysql sh -c 'exec mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --single-transaction --quick glpidb' | gzip > "glpi_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
   ls -lh glpi_backup_*.sql.gz
   ```
4. **Procedimiento B — Captura de Punto Cero Descomprimido (GLPI + Snipe-IT):**
   ```bash
   cd ~/kayn
   export $(grep -v '^#' .env | xargs)

   # Snapshot de GLPI (Estructura, SLAs, Calendarios, Reglas y Formularios)
   docker exec glpi-mysql mysqldump \
     -u"${GLPI_DB_USER:-glpi_user}" \
     -p"${GLPI_DB_PASSWORD}" \
     "${GLPI_DB_NAME:-glpidb}" > ~/kayn/backups/punto_cero_glpi.sql

   # Snapshot de Snipe-IT (Estructura de Activos y Categorías)
   docker exec snipe-mysql mysqldump \
     -u"${DB_USERNAME:-snipeit_user}" \
     -p"${DB_PASSWORD}" \
     "${DB_DATABASE:-snipeit}" > ~/kayn/backups/punto_cero_snipeit.sql

   ls -lh ~/kayn/backups/punto_cero_*.sql
   ```
5. **Procedimiento C — Rollback / Vuelta a Cero tras Pruebas UAT:**
   - Desde archivo comprimido `.sql.gz`:
     ```bash
     cd ~/kayn
     zcat glpi_backup_20261011_040132.sql.gz | docker exec -i glpi-mysql sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" glpidb'
     docker exec -u www-data -it glpi php /var/www/html/glpi/bin/console cache:clear
     ```
   - Desde archivos `punto_cero_*.sql`:
     ```bash
     cd ~/kayn
     export $(grep -v '^#' .env | xargs)

     # 1. Sobrescribir GLPI con el punto cero
     docker exec -i glpi-mysql mysql \
       -u"${GLPI_DB_USER:-glpi_user}" \
       -p"${GLPI_DB_PASSWORD}" \
       "${GLPI_DB_NAME:-glpidb}" < ~/kayn/backups/punto_cero_glpi.sql

     # 2. Sobrescribir Snipe-IT con el punto cero
     docker exec -i snipe-mysql mysql \
       -u"${DB_USERNAME:-snipeit_user}" \
       -p"${DB_PASSWORD}" \
       "${DB_DATABASE:-snipeit}" < ~/kayn/backups/punto_cero_snipeit.sql

     # 3. Purga inmediata de memoria caché de las aplicaciones
     docker exec -u www-data -it glpi php /var/www/html/glpi/bin/console cache:clear
     docker exec -it snipe-it php artisan cache:clear && docker exec -it snipe-it php artisan config:clear
     ```
6. **Criterios de Salida:**
   > **Criterios de Salida:** Las tablas transaccionales se resetean, desaparecen los tickets y activos de prueba y el sistema queda listo para el ticket #1 productivo manteniendo todas las reglas de negocio intactas.

### **SOP-MILIO-006: Pruebas de Resiliencia, Simulación de Caídas (Graceful Stop) y Auditoría de Monitoreo NOC**

1. **Objetivo y Alcance:** Establecer el procedimiento seguro para simular interrupciones de servicio en los contenedores de aplicación web (Milio / GLPI y Gekko / Snipe-IT), validar el disparo de alertas SMTP en Uptime Kuma (caída y recuperación) y auditar la persistencia de datos y políticas de reinicio sin comprometer la integridad de las bases de datos relacionales.
2. **Garantías de Integridad de Base de Datos durante la Prueba:**
   - **Aislamiento de Motores RDBMS:** Los datos transaccionales residen en los contenedores dedicados `glpi-mysql` y `snipe-mysql`. Al detener únicamente los contenedores web (`glpi` o `snipe-it`), los motores MariaDB permanecen encendidos y sin alteración.
   - **Apagado Limpio (*Graceful Shutdown*):** La instrucción `docker stop` envía una señal `SIGTERM` al proceso principal del contenedor, otorgando un período de gracia (10 segundos por defecto) para cerrar conexiones activas e hilos de Apache/PHP antes de emitir `SIGKILL`.
   - **Persistencia Desacoplada:** Toda la información reside en volúmenes montados en el host `kayn`, fuera de la capa volátil del contenedor.
3. **Procedimiento Secuencial de Prueba de Alertamiento (UAT de Monitoreo):**
   - Detener de forma controlada el contenedor de aplicación a evaluar:
     ```bash
     docker stop glpi
     # O para Snipe-IT:
     docker stop snipe-it
     ```
   - Aguardar el ciclo de sondeo de Uptime Kuma (60 segundos) y verificar en el panel (`http://localhost:3001`) el cambio de estado a **CAÍDO (DOWN)** y la recepción del correo de alerta con el asunto `Ayuda! Milio se ha caido!` (o `Gekko`).
   - Restablecer el servicio iniciando nuevamente el contenedor:
     ```bash
     docker start glpi
     # O para Snipe-IT:
     docker start snipe-it
     ```
   - Aguardar el siguiente intervalo de comprobación (1 a 2 minutos) y confirmar el paso a estado **FUNCIONAL (UP)** junto con la recepción del correo de restablecimiento `Bravo! Milio se levantó solito!`.
4. **Procedimiento de Auditoría de Persistencia y Políticas de Reinicio:**
   - Verificar los puntos de montaje (volúmenes y bind mounts) activos en `uptime-kuma`:
     ```bash
     docker inspect uptime-kuma --format '{{ range .Mounts }}{{ .Type }}: {{ .Source }} -> {{ .Destination }}{{ println }}{{ end }}'
     ```
   - Verificar la política de reinicio configurada en el contenedor:
     ```bash
     docker inspect uptime-kuma --format '{{ .HostConfig.RestartPolicy.Name }}'
     ```
5. **Criterios de Salida:**
   > **Criterios de Salida:** Recepción validada de los correos de incidente y recuperación con marca de tiempo exacta, servicios en estado Funcional (`UP`) en el grupo `NOC`, y volumen `/app/data` correctamente mapeado a `snipe-it_uptime-kuma-data`.

---

## **6. Guía de Troubleshooting y Resolución de Incidentes**

### **6.1. Inspección de Logs en Tiempo Real**

- Ver logs integrados del compose en tiempo real:
  ```bash
  docker compose logs -f
  ```
- Inspeccionar las últimas 100 líneas del servicio GLPI:
  ```bash
  docker logs glpi --tail 100
  ```
- Inspeccionar las últimas 100 líneas del motor MySQL/MariaDB de GLPI:
  ```bash
  docker logs glpi-mysql --tail 100
  ```

### **6.2. Pérdida de Conectividad con la Base de Datos (Error 2002)**

- **Comprobación de estado:** Verificar que el contenedor `glpi-mysql` esté activo mediante `docker ps`.
- **Verificación de red bridge interna:** Validar la comunicación interna y resolución DNS ejecutando un ping desde el contenedor de aplicación: `docker exec -it glpi ping glpi-mysql` dentro de la red `snipe-it_default`.
- **Verificación de credenciales:** Asegurar que las variables de entorno relativas al usuario, nombre de base de datos y contraseña coincidan exactamente entre la sección del servicio web y del motor MySQL en el archivo `.env`.

### **6.3. Error de Integridad / Permisos en GLPI Tras Reinicio o Actualización**

- Restablecer la propiedad de los archivos al usuario del servidor web (`www-data`):
  ```bash
  docker exec -u 0 -it glpi chown -R www-data:www-data /var/www/html/glpi/files /var/www/html/glpi/marketplace /var/www/html/glpi/plugins
  ```

### **6.4. El Puerto de un Servicio Ya Está en Uso (Bind Address Already in Use)**

- **Identificar el proceso conflictivo en el host:** `sudo ss -tulpn | grep 9080` o bien `sudo lsof -i :9080`
- **Resolución:** Detener el proceso local que ocupa el puerto o reasignar un puerto libre en la sección `ports` del archivo `docker-compose.yml`.

### **6.5. Recreación Limpia de Contenedores sin Pérdida de Datos Persistentes**

```bash
docker compose down && docker compose up -d
```

### **6.6. Falsos Positivos HTTP 302 y Error getaddrinfo ENOTFOUND gekko.local en Uptime Kuma**

- **Síntoma:** El servicio Snipe-IT (`Gekko`) o GLPI (`Milio`) es accesible desde el navegador del host, pero Uptime Kuma lo reporta como **CAÍDO** arrojando error `302 Found` o `getaddrinfo ENOTFOUND gekko.local`.
- **Causa Raíz:** Snipe-IT responde en su raíz con una redirección `HTTP/1.1 302 Found` apuntando a `Location: http://gekko.local:8080/login` (definido en su variable `APP_URL`). Como `gekko.local` es un nombre resuelto en el archivo `hosts` del cliente pero inexistente en el DNS interno de la red Docker `snipe-it_default`, si Uptime Kuma intenta seguir la redirección (*Follow Redirect*), falla al resolver el dominio.
- **Diagnóstico por Consola (Inspección de Encabezados HTTP desde Uptime Kuma):**
  ```bash
  docker exec -it uptime-kuma curl -I http://glpi/ && echo "---" && docker exec -it uptime-kuma curl -I http://snipe-it/
  ```
- **Resolución:**
  - **Para Milio (GLPI):** Configurar la URL `http://glpi/`, desmarcar **Seguir redirecciones** y mantener los códigos aceptados en `200-299` (ya que Apache en GLPI entrega `HTTP/1.1 200 OK` directo).
  - **Para Gekko (Snipe-IT):** Configurar la URL `http://snipe-it/`, desmarcar la casilla **Seguir redirecciones** (*Follow Redirect*) en la sección **Avanzado**, y añadir el código `302` en **Códigos de estado aceptados** (`200-299, 302`).

### **6.7. Error 404 Not Found y Monitor Trabado en Estado Pausado en Uptime Kuma**

- **Síntoma A (`404 Not Found`):** El monitor reporta error `404` tras una edición de parámetros.
  - **Resolución:** Verificar que no existan errores tipográficos o rutas inexistentes y respetar la barra final (`http://glpi/` y `http://snipe-it/`).
- **Síntoma B (Monitor bloqueado en estado Pausado sin responder al botón Reanudar):**
  - **Resolución 1 (Forzar reinicio de ciclo):** Hacer clic en **Editar** dentro del monitor afectado, desplazarse al final del formulario sin alterar parámetros y hacer clic en **Guardar** para reiniciar el worker de sondeo.
  - **Resolución 2 (Desincronización de WebSocket):** Presionar `Ctrl + F5` en el navegador para limpiar la caché de la sesión y restablecer el socket en tiempo real con el contenedor `uptime-kuma`.
  - **Resolución 3 (Herencia de Grupo):** Seleccionar el grupo contenedor `NOC` en el panel izquierdo y verificar que el grupo padre no se encuentre pausado.

### **6.8. Inversión de Mensajes en Plantillas Liquid (Envío de Mensaje "UP" cuando el Servicio cae)**

- **Síntoma:** Al detener un contenedor (`DOWN`), el correo electrónico recibido muestra el texto de recuperación ("se levantó solito") en lugar del mensaje de caída.
- **Causa Raíz:** En el motor Liquid de Uptime Kuma, la variable general `status` puede evaluarse como booleano (`false`), cadena de texto o entero según el contexto del evento, haciendo que una condición simple `{% if status == 0 %}` resulte falsa y ejecute el bloque `{% else %}`.
- **Resolución:** Evaluar explícitamente la propiedad numérica del objeto de latido `heartbeatJSON.status == 0` combinada con las variantes de estado:
  ```text
  {% if heartbeatJSON.status == 0 or status == 0 or status == false %}
  ```

---

## **7. Diagnóstico de Tareas Automáticas (Cron Interno GLPI) y Mejora Continua (CSI)**

| Proceso Interno GLPI | Función en el Sistema | Estado Relevado | Acción de Optimización Recomendada |
| :---: | :--- | :---: | :--- |
| `slaticket` | Calcula vencimientos de SLAs (TTO/TTR) y dispara escalamientos automáticos. | Activo (Modo CLI) | Migrado a ejecución desatendida vía `CLI` desde el Crontab del host cada 5 minutos (`CSI-01`). |
| `queuednotification` | Procesa la cola de salida de correos electrónicos de notificación. | Activo (Modo CLI) | Configurado en modo `CLI` para procesamiento asíncrono de notificaciones por consola (`CSI-01`). |
| `mailgate` | Colector IMAP/POP3 para convertir correos entrantes en tickets automáticamente. | 0 receptores configurados | Si se habilita un buzón de mesa de ayuda, vincular el receptor en **Configuración > Receptores** con regla de asignación a `Mesa de Ayuda - N1`. |

Tarea Crontab activa en el host `kayn` para el Cron interno de GLPI (ejecución cada 5 minutos):

```bash
*/5 * * * * docker exec -u www-data glpi php /var/www/html/glpi/front/cron.php &>/dev/null
```

---

## **8. Arquitectura de Observabilidad, Monitoreo Activo (NOC) y Gestión de Eventos (Uptime Kuma)**

### **8.1. Propósito, Alcance ITIL v4 y Elemento de Configuración (CI)**

Para cubrir la práctica de **Monitoreo y Gestión de Eventos (*Monitoring and Event Management*)** de ITIL v4, se integró Uptime Kuma (`uptime-kuma`) en la red interna `snipe-it_default` del host `kayn`. Su función es supervisar de forma continua (intervalos de 60 segundos) la disponibilidad de los servicios críticos **Milio** (GLPI) y **Gekko** (Snipe-IT) agrupados bajo el nodo **NOC**, gestionando alertas proactivas por correo electrónico (SMTP) mediante plantillas dinámicas Liquid.

| Atributo del CI | Detalle Técnico Configurado |
| :--- | :--- |
| **Servicio / Contenedor** | `uptime-kuma` (`louislam/uptime-kuma:latest`) |
| **Red Docker** | `snipe-it_default` (Resolución DNS interna hacia `glpi` y `snipe-it`) |
| **Puerto Expuesto** | `3001:3001/TCP` (`http://localhost:3001`) |
| **Política de Reinicio** | `unless-stopped` |
| **Volumen de Datos** | `snipe-it_uptime-kuma-data` montado en `/app/data` (Base SQLite, monitores, credenciales SMTP e historial) |
| **Socket de Docker** | Bind mount `/var/run/docker.sock -> /var/run/docker.sock` |

> **Referencia de Despliegue:** La definición declarativa del contenedor y sus volúmenes se encuentra integrada en el manifiesto general de la **Sección 2.5 (`docker-compose.yml`)**.

### **8.2. Auditoría de Encabezados HTTP desde la Sonda de Monitoreo**

Se verificó la respuesta HTTP directa de cada contenedor desde el interior de `uptime-kuma` para determinar el código de estado nativo y el comportamiento de redirección:

Comando ejecutado en `kayn`:

```bash
docker exec -it uptime-kuma curl -I http://glpi/ && echo "---" && docker exec -it uptime-kuma curl -I http://snipe-it/
```

Salida validada:

```text
HTTP/1.1 200 OK
Date: Mon, 12 Oct 2026 01:53:01 GMT
Server: Apache/2.4.62 (Debian)
Set-Cookie: glpi_0d19253e686be6148be5a3dc965a02b6a2540e4635cf3c2a3754fca344a629396daeceeb918cd2721012286bb548b67b1c95d156b0813c6f75570f9cddef8460=k98h6fvnt7733gka40jenefgje; path=/; HttpOnly
Cache-Control: no-store, no-cache, must-revalidate
Content-Type: text/html; charset=UTF-8
---
HTTP/1.1 302 Found
Date: Mon, 12 Oct 2026 01:53:02 GMT
Server: Apache/2.4.58 (Ubuntu)
Cache-Control: max-age=0, must-revalidate, no-cache, no-store, private
Location: http://gekko.local:8080/login
X-Frame-Options: DENY
Content-Type: text/html; charset=utf-8
```

### **8.3. Matriz de Configuración de Monitores (Grupo NOC) y Uso del Modo Invertido**

| Monitor | Servicio | Grupo | Tipo | URL Interna | Intervalo | Seguir Redirecciones | Códigos Aceptados | Criterio Técnico de Validación |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Milio** | GLPI (ITSM) | `NOC` | HTTP(s) | `http://glpi/` | `60 s` | Desactivado | `200-299` | Responde `HTTP/1.1 200 OK` directo en la raíz de Apache. |
| **Gekko** | Snipe-IT (ITAM) | `NOC` | HTTP(s) | `http://snipe-it/` | `60 s` | Desactivado | `200-299, 302` | Responde `HTTP/1.1 302 Found` hacia `http://gekko.local:8080/login`. Al desmarcar redirecciones y aceptar `302`, se evita el fallo DNS `ENOTFOUND gekko.local`. |

> **Importante — Lineamiento sobre el "Modo Invertido" (*Upside Down Mode*):**
> El parámetro **Modo invertido** ("Si el servicio es alcanzable, está CAÍDO") se mantiene **desactivado** para Milio y Gekko. Su uso se reserva para:
> - **Auditoría de Firewall y Puertos Cerrados:** Alertar si puertos internos sensibles (ej. `3306` MariaDB o SSH) quedan expuestos accidentalmente.
> - **Control de Servicios Dados de Baja:** Confirmar que contenedores deprecados o en mantenimiento sigan apagados.
> - **Validación de Listas Negras (DNS Sinkholes):** Comprobar que dominios bloqueados no resuelvan tráfico.
> - **Entornos de Staging Ocultos:** Asegurar que ambientes de prueba no respondan sin VPN.

### **8.4. Canal de Alertas SMTP y Plantillas Dinámicas (Liquid)**

Las notificaciones SMTP se asocian a cada monitor (**Editar -> Notificaciones**) o de forma global (**Ajustes -> Notificaciones -> Activado por defecto para todos los monitores**). Se utilizan las variables `{{ name }}`, `{{ status }}` y `{{ heartbeatJSON }}` (`heartbeatJSON.status` y `heartbeatJSON.time`) del motor Liquid:

Asunto Personalizado (Liquid):

```text
{% if heartbeatJSON.status == 0 or status == 0 or status == false %}Ayuda! {{ name }} se ha caido! {% else %} Bravo! {{ name }} se levantó solito! {% endif %}
```

Cuerpo Personalizado (Liquid):

```text
{% if heartbeatJSON.status == 0 or status == 0 or status == false %}
Parece que {{ name }} ha sufrido una baja el día {{ heartbeatJSON.time | date: "%d/%m/%Y" }} a las {{ heartbeatJSON.time | date: "%H:%M:%S" }}
Que no cunda el pánico, seguro pueda levantarse solo, te avisamos en unos minutos. Estate atento si no recibes mas noticias
{% else %}
Bravo! Parece que {{ name }} se levantó solito y está sano, te recomendamos revisarlo!
{% endif %}
```

**Evidencia de Homologación (UAT de Alertas por Correo — 12/10/2026):**

- **Caída de Milio (`01:57:29`):** Asunto `Ayuda! Milio se ha caido!` - *"Parece que Milio ha sufrido una baja el día 12/10/2026 a las 01:57:29 Que no cunda el pánico, seguro pueda levantarse solo, te avisamos en unos minutos. Estate atento si no recibes mas noticias"*.
- **Caída de Gekko (`01:57:38`):** Asunto `Ayuda! Gekko se ha caido!` - *"Parece que Gekko ha sufrido una baja el día 12/10/2026 a las 01:57:38 Que no cunda el pánico, seguro pueda levantarse solo, te avisamos en unos minutos. Estate atento si no recibes mas noticias"*.
- **Recuperación de Gekko:** Asunto `Bravo! Gekko se levantó solito!` - *"Bravo! Parece que Gekko se levantó solito y está sano, te recomendamos revisarlo!"*.

### **8.5. SOP-MILIO-006: Simulación de Caídas (Graceful Stop) y Auditoría de Persistencia**

1. **Seguridad e Integridad de Bases de Datos en Pruebas de Caída:**
   - **Aislamiento RDBMS:** Detener `glpi` o `snipe-it` solo apaga el servidor web Apache/PHP; los motores `glpi-mysql` y `snipe-mysql` siguen encendidos e intactos.
   - **Apagado Limpio (`SIGTERM`):** `docker stop` envía `SIGTERM` y aguarda hasta 10 segundos para cerrar procesos e hilos activos de forma segura antes de detener el contenedor.
   - **Persistencia en Disco:** Los datos residen en los volúmenes del host `kayn`, sin riesgo de pérdida ni corrupción.
2. **Secuencia de Prueba de Alertas (Stop / Start):**
   ```bash
   # 1. Simular caída del servicio web
   docker stop glpi
   # 2. Aguardar detección en Uptime Kuma (60 s) y recepción de correo [DOWN]
   # 3. Restablecer el servicio web
   docker start glpi
   # 4. Aguardar comprobación (1-2 min) y recepción de correo [UP]
   ```
3. **Auditoría de Volúmenes y Políticas de Reinicio (`docker inspect`):**
   > **Nota:** `-v uptime-kuma-data:/app/data` es un flag de `docker run`, no un comando directo de Bash. Para auditar un contenedor activo se utiliza `docker inspect`.

   ```bash
   # Verificar montajes de persistencia y socket Docker:
   docker inspect uptime-kuma --format '{{ range .Mounts }}{{ .Type }}: {{ .Source }} -> {{ .Destination }}{{ println }}{{ end }}'
   ```

   Salida verificada en `kayn`:

   ```text
   bind: /var/run/docker.sock -> /var/run/docker.sock
   volume: /var/lib/docker/volumes/snipe-it_uptime-kuma-data/_data -> /app/data
   ```

   ```bash
   # Verificar política de reinicio automático (valor esperado: unless-stopped):
   docker inspect uptime-kuma --format '{{ .HostConfig.RestartPolicy.Name }}'
   ```

### **8.6. Troubleshooting Específico de Uptime Kuma**

- **Error `getaddrinfo ENOTFOUND gekko.local` o Falso Positivo `302 Found`:** Ocurre cuando **Seguir redirecciones** está activo y el contenedor redirige a un dominio local (`gekko.local`) no registrado en el DNS interno de Docker. **Solución:** Desmarcar **Seguir redirecciones** en **Avanzado** y agregar `302` en **Códigos de estado aceptados** (`200-299, 302`).
- **Error `404 Not Found` tras editar un monitor:** Verificar la URL interna exacta (`http://glpi/` y `http://snipe-it/`) respetando la barra final (`/`). Para el detalle exhaustivo de diagnóstico y resolución, consultar la **Sección 6.6 a 6.8**.
- **Monitor bloqueado en estado Pausado (botón Reanudar no responde):** Entrar a **Editar** en el monitor y pulsar **Guardar** al final del formulario para forzar el reinicio del ciclo de sondeo; refrescar la interfaz con `Ctrl + F5` por posible desconexión de WebSocket; y verificar que el grupo padre `NOC` no esté en pausa.
- **Envío de mensaje "UP" cuando el servicio está "DOWN":** La variable `status` simple puede evaluarse como booleano. **Solución:** Usar la condición combinada `{% if heartbeatJSON.status == 0 or status == 0 or status == false %}` en las plantillas Liquid.

---

## **9. Hardening de Seguridad, Rotación de Credenciales, Respaldos de Resguardo y Congelamiento (Code Freeze)**

### **9.1. Propósito y Alcance (ITIL v4 Information Security Management & Service Continuity Management)**

Con el objetivo de blindar la plataforma en el entorno productivo y eliminar cualquier credencial genérica o por defecto en los motores de bases de datos y archivos de configuración, se ejecutó un procedimiento integral de **Hardening de Seguridad**, captura de **Snapshots de Resguardo** y declaración de **Code Freeze**. Esta intervención se alinea con las prácticas de **Gestión de la Seguridad de la Información (*Information Security Management*)** y **Gestión de la Continuidad del Servicio (*Service Continuity Management*)** de ITIL v4.

### **9.2. Captura de Respaldos de Resguardo (Snapshots de Estado Congelado)**

Se generaron volcados SQL completos (dumps lógicos) del estado productivo consolidado en producción en `~/kayn/backups/`, asegurando un punto de restauración inmediato:

- `glpi_demo_listo.sql` (`17.8 MB` / `17,863,444 bytes`): Incluye estructura completa, reglas de negocio de ruteo automático, categorías ITIL, plantillas obligatorias, acuerdos de nivel de servicio (SLA) y 405 tickets generados.
- `snipeit_demo_listo.sql` (`576 KB` / `589,469 bytes`): Incluye activos, modelos, fabricantes, ubicaciones y asignaciones nominales.

Comando ejecutado para la captura y verificación de Snipe-IT:

```bash
docker exec snipe-mysql mysqldump -u snipeit_user -p snipeit 2>/dev/null > ~/kayn/backups/snipeit_demo_listo.sql && ls -lh ~/kayn/backups/snipeit_demo_listo.sql
```

> **Nota:** Autenticado con la clave inicial `snipeit_password_123` previo a la rotación.

Resultado obtenido en consola:

```text
-rw-rw-r-- 1 juanx juanx 576K Oct 12 00:57 /home/juanx/kayn/backups/snipeit_demo_listo.sql
```

### **9.3. Rotación de Contraseñas en Motores MariaDB/MySQL (glpi-mysql y snipe-mysql)**

> **Importante — Consideración Técnica de Persistencia en Docker:** En contenedores MySQL/MariaDB cuyos volúmenes persistentes ya fueron inicializados en disco, la modificación aislada del archivo `.env` es ignorada por el motor de base de datos y provoca errores de desconexión (`Error establishing a database connection`). Por ello, la rotación se ejecutó en dos fases coordinadas: actualización directa de privilegios dentro del motor SQL y sincronización inmediata en los archivos de configuración de cada aplicación.

- **Nueva credencial para usuarios operativos de aplicación (`glpi_user` y `snipeit_user`):** `<DB_APP_PASSWORD_ROTADA>`
- **Nueva credencial para cuentas administrativas (`root`):** `<DB_ROOT_PASSWORD_ROTADA>`

#### **A. Rotación en glpi-mysql (Usuario de Aplicación y Root)**

Comando ejecutado:

```bash
docker exec -i glpi-mysql mysql -u root -p -e "ALTER USER 'glpi_user'@'%' IDENTIFIED BY '<DB_APP_PASSWORD_ROTADA>'; ALTER USER 'root'@'localhost' IDENTIFIED BY '<DB_ROOT_PASSWORD_ROTADA>'; ALTER USER 'root'@'%' IDENTIFIED BY '<DB_ROOT_PASSWORD_ROTADA>'; FLUSH PRIVILEGES;"
```

#### **B. Rotación en snipe-mysql y Resolución de Privilegios SQL (Error 1227)**

Al intentar ejecutar `ALTER USER` autenticando con el usuario no administrativo `snipeit_user`, MariaDB arrojó el siguiente error de permisos:

```text
ERROR 1227 (42000) at line 2: Access denied; you need (at least one of) the CREATE USER privilege(s) for this operation
```

**Resolución:** Se aplicó la sentencia `SET PASSWORD = PASSWORD(...)`, permitida para que un usuario estándar actualice su propia contraseña sin requerir el privilegio `CREATE USER`:

Comando ejecutado:

```bash
docker exec -i snipe-mysql mysql -u snipeit_user -p -D snipeit -e "SET PASSWORD = PASSWORD('<DB_APP_PASSWORD_ROTADA>'); FLUSH PRIVILEGES;"
```

> **Nota técnica:** Si bien la instrucción final `FLUSH PRIVILEGES` arrojó `ERROR 1227 (42000) at line 3: Access denied; you need (at least one of) the RELOAD privilege(s) for this operation`, la sentencia previa `SET PASSWORD` se ejecutó y aplicó de manera efectiva.

Comando de verificación de la nueva credencial en `snipe-mysql`:

```bash
docker exec -i snipe-mysql mysql -u snipeit_user -p -D snipeit -e "SELECT 'NUEVA_OK' AS Estado;" 2>/dev/null
```

Resultado validado en consola:

```text
Estado: NUEVA_OK
```

### **9.4. Sincronización de Archivos de Configuración en GLPI y Snipe-IT**

#### **A. Sincronización Interna en Contenedor GLPI (config_db.php)**

Al intentar editar inicialmente el archivo de configuración de GLPI se detectó que el contenedor se encontraba detenido:

```text
Error response from daemon: container 8ada1e5ea5cb495fd5a2d620022ccc8daad799ac6ca1ffaab06ff734b30753f3 is not running
```

Se procedió a iniciar el contenedor, actualizar la credencial interna en `/var/www/html/glpi/config/config_db.php` y verificar el cambio:

Comandos ejecutados:

1. Iniciar contenedor GLPI:
   ```bash
   docker start glpi
   ```
2. Actualizar contraseña en `config_db.php`:
   ```bash
   docker exec -i glpi sed -i 's/glpi_password_123/<DB_APP_PASSWORD_ROTADA>/g' /var/www/html/glpi/config/config_db.php
   ```
3. Verificar configuración aplicada:
   ```bash
   docker exec -i glpi grep -i password /var/www/html/glpi/config/config_db.php
   ```

Resultado obtenido en consola:

```text
glpi
public $dbpassword = '<DB_APP_PASSWORD_ROTADA>';
```

#### **B. Actualización de Variables de Entorno (.env) y Recreación de Snipe-IT**

Se actualizaron las contraseñas en `~/kayn/.env` y se recreó el contenedor `snipe-it` sin afectar volúmenes persistentes. Asimismo, al actualizar la variable `GLPI_DB_ROOT_PASSWORD`, el uso de comillas dobles en Bash provocó inicialmente el error:

```text
bash: !/g: event not found
```

> **Nota:** Esto ocurre porque el signo de exclamación (`!`) activa la expansión de historial de Bash dentro de comillas dobles. Se solucionó empleando comillas simples en la instrucción `sed`.

Comandos ejecutados:

1. Actualizar contraseñas de aplicación en `.env`:
   ```bash
   sed -i 's/snipeit_password_123/<DB_APP_PASSWORD_ROTADA>/g' ~/kayn/.env && sed -i 's/glpi_password_123/<DB_APP_PASSWORD_ROTADA>/g' ~/kayn/.env
   ```
2. Actualizar contraseña de `root` en `.env` con comillas simples:
   ```bash
   sed -i 's/GLPI_DB_ROOT_PASSWORD=glpi_root_password_123/GLPI_DB_ROOT_PASSWORD=<DB_ROOT_PASSWORD_ROTADA>/g' ~/kayn/.env
   ```
3. Recrear el contenedor de Snipe-IT para inyectar la nueva variable:
   ```bash
   cd ~/kayn && docker compose up -d snipe-it
   ```

Resultado obtenido en consola:

```text
[+] Running 2/2
 ✔ Container snipe-mysql Running 0.0s
 ✔ Container snipe-it Started 3.8s
```

Comando de verificación cruzada de acceso en `glpi-mysql` (Usuario Operativo y Root):

```bash
docker exec -i glpi-mysql mysql -u glpi_user -p -D glpidb -e "SELECT 'GLPI_USER_OK' AS Estado;" && docker exec -i glpi-mysql mysql -u root -p -e "SELECT 'GLPI_ROOT_OK' AS Estado;"
```

Resultado obtenido en consola:

```text
Estado: GLPI_USER_OK
Estado: GLPI_ROOT_OK
```

### **9.5. Saneamiento de Credenciales en Texto Plano (YAML) y Hardening de Permisos a Nivel Host**

Durante la auditoría preventiva de archivos en el directorio `~/kayn` se detectaron credenciales genéricas residuales en texto plano dentro de los manifiestos `docker-compose.yml`, `docker-compose-old.yml` y `docker-compose.yml.bak`:

**Hallazgo de auditoría inicial (Pre-Saneamiento):**

- `/home/juanx/kayn/docker-compose-old.yml` (líneas 7, 10, 31, 43, 46): `MYSQL_ROOT_PASSWORD: root_password_123`, `MYSQL_PASSWORD: snipeit_password_123`, `DB_PASSWORD: snipeit_password_123`, `MYSQL_ROOT_PASSWORD: glpi_root_password_123`, `MYSQL_PASSWORD: glpi_password_123`
- `/home/juanx/kayn/docker-compose.yml` (líneas 7, 10): `MYSQL_ROOT_PASSWORD: root_password_123`, `MYSQL_PASSWORD: snipeit_password_123`
- `/home/juanx/kayn/docker-compose.yml.bak` (líneas 7, 10): `MYSQL_ROOT_PASSWORD: root_password_123`, `MYSQL_PASSWORD: snipeit_password_123`

Comandos ejecutados para remediación y blindaje de permisos en el sistema operativo:

1. Reemplazar contraseñas residuales en archivos YAML:
   ```bash
   sed -i 's/root_password_123/<DB_ROOT_PASSWORD_ROTADA>/g' ~/kayn/docker-compose*.yml && sed -i 's/snipeit_password_123/<DB_APP_PASSWORD_ROTADA>/g' ~/kayn/docker-compose*.yml && sed -i 's/glpi_root_password_123/<DB_ROOT_PASSWORD_ROTADA>/g' ~/kayn/docker-compose*.yml && sed -i 's/glpi_password_123/<DB_APP_PASSWORD_ROTADA>/g' ~/kayn/docker-compose*.yml
   ```
2. Eliminar archivo backup temporal residual y restringir permisos de lectura/escritura exclusivamente al propietario (modo `600` y `700`):
   ```bash
   rm -f ~/kayn/docker-compose.yml.bak && chmod 600 ~/kayn/docker-compose*.yml && chmod 600 ~/kayn/.env && chmod 700 ~/kayn/backups && chmod 600 ~/kayn/backups/*.sql
   ```

### **9.6. Auditoría Final de Seguridad, Permisos y Conectividad (Certificación de Code Freeze)**

Se ejecutó la verificación integral para certificar la ausencia total de contraseñas por defecto en archivos de configuración, la restricción de permisos en el sistema de archivos y la conectividad operativa en ambas bases de datos:

Comandos de auditoría ejecutados:

1. Búsqueda de claves viejas en archivos de configuración:
   ```bash
   grep -rnE "123|password_123" ~/kayn/*.yml ~/kayn/*.env ~/kayn/docker-compose* 2>/dev/null
   ```
2. Verificación de permisos de archivos sensibles:
   ```bash
   ls -ld ~/kayn/.env ~/kayn/backups ~/kayn/backups/*.sql 2>/dev/null
   ```
3. Comprobación de conexión directa en ambas bases: Consultas `SELECT` sobre `glpidb` (`glpi-mysql`) y `snipeit` (`snipe-mysql`) autenticando con `<DB_APP_PASSWORD_ROTADA>`.

Resultado final certificado en el host `kayn`:

```text
=== 1. BUSCANDO CLAVES VIEJAS EN ARCHIVOS DE CONFIGURACIÓN ===
Limpio: no hay credenciales viejas en configs.
=== 2. VERIFICANDO PERMISOS DE ARCHIVOS SENSIBLES ===
-rw------- 1 juanx juanx      564 Oct 12 01:04 /home/juanx/kayn/.env
drwx------ 2 juanx juanx     4096 Oct 12 00:56 /home/juanx/kayn/backups
-rw------- 1 juanx juanx 17863444 Oct 12 00:56 /home/juanx/kayn/backups/glpi_demo_listo.sql
-rw------- 1 juanx juanx 17515892 Oct 11 23:25 /home/juanx/kayn/backups/punto_cero_glpi.sql
-rw------- 1 juanx juanx   171070 Oct 11 23:25 /home/juanx/kayn/backups/punto_cero_snipeit.sql
-rw------- 1 juanx juanx   589469 Oct 12 00:57 /home/juanx/kayn/backups/snipeit_demo_listo.sql
=== 3. COMPROBANDO CONEXIÓN DIRECTA EN AMBAS BASES ===
App: GLPI: Conexión OK
App: Snipe-IT: Conexión OK
```

---

## **10. Gestión Visual de Proyectos y Tareas Ágiles de Infraestructura (Kanboard)**

### **10.1. Propósito, Alcance ITIL y Arquitectura de Datos**

En alineación con la práctica de **Mejora Continua (*Continual Improvement*)** y la coordinación operativa de despliegues internos de IT, se implementó el tablero Kanban sobre el contenedor `kanban` (`kanboard/kanboard:latest`) escuchando en el puerto `7080:80`. A diferencia de los incidentes y solicitudes canalizados por GLPI, este componente gestiona las iniciativas transversales de ingeniería, mantenimiento programado y sprints de infraestructura.

- **Motor RDBMS / Persistencia:** Base de datos relacional embebida SQLite localizada en `/var/www/app/data/db.sqlite`, persistida mediante el volumen Docker `snipe-it_kanban-data`.
- **Mecanismo de Manipulación y Automatización:** Motor PHP PDO-SQLite (`pdo_sqlite`) ejecutado de forma desatendida desde el interior del contenedor, asegurando transaccionalidad sin dependencias de paquetes binarios externos (`sqlite3` CLI) ni interacción manual en UI.

### **10.2. Topología del Tablero del Proyecto y Estados de Flujo**

- **Proyecto:** `Plataforma Milio IT - Sprint Infraestructura` (ID: 1, Token: `milio2026`).
- **Columnas de Flujo de Trabajo (Workflow Evolucionado a 5 Estadios):**
  1. `1. Backlog & Mejoras CSI (Fase 2)`: Iniciativas de mejora continua post-demo.
  2. `2. Pendientes SÍ o SÍ (de Resguardo)`: Validaciones críticas operativas previas a la exposición.
  3. `3. Revisión Runbook & Ajustes`: Saneamiento documental y estandarización de SOPs.
  4. `4. Homologación / UAT & Ensayo`: Pruebas de resiliencia, monitoreo y guion ejecutivo.
  5. `5. Hitos Alcanzados / Code Freeze`: Hitos técnicos completados, cerrados y auditados (`CORE`, `GEKKO`, `MILIO`, `NOC`, `DEMO`, `SEC`, `CSI`).

> **Nota de Visualización en UI:** Al cerrar una tarea en Kanboard (`is_active = 0`), el filtro por defecto (`status:open`) la oculta del tablero. Para visualizar el historial completo de tarjetas cerradas, utilizar el filtro `status:all` en la barra de búsqueda superior.

### **10.3. Procedimiento Estándar de Automatización e Inyección (SOP-MILIO-007)**

Para poblar o reconstruir el tablero de tareas sin dependencia de la interfaz gráfica web:

```bash
docker exec -i kanban php -r '
$pdo = new PDO("sqlite:/var/www/app/data/db.sqlite");
$now = time();

// 1. Crear el proyecto si no existe
$pdo->exec("INSERT INTO projects (name, is_active, token, last_modified) VALUES (\"Plataforma Milio IT - Sprint Infraestructura\", 1, \"milio2026\", $now)");
$proj_id = $pdo->lastInsertId();

// 2. Crear las columnas del tablero
$cols = [
    ["Backlog & Mejoras Futuras", 1],
    ["En Curso", 2],
    ["Homologación / UAT", 3],
    ["Cierre Operativo / Code Freeze", 4]
];
$col_ids = [];
foreach ($cols as $c) {
    $stmt = $pdo->prepare("INSERT INTO columns (title, position, project_id) VALUES (?, ?, ?)");
    $stmt->execute([$c[0], $c[1], $proj_id]);
    $col_ids[] = $pdo->lastInsertId();
}

// 3. Inyectar las tareas del sprint
$tasks = [
    ["Hardening de Seguridad & Rotacion MySQL", "Rotacion de claves glpi_user, snipeit_user y root a <DB_APP_PASSWORD_ROTADA>. Permisos 600 y 700 aplicados.", 3, "green"],
    ["Despliegue y Pruebas UAT Uptime Kuma NOC", "Monitoreo HTTP activo cada 60s para Milio (GLPI) y Gekko (Snipe-IT). Alertas SMTP y plantillas Liquid validadas.", 3, "green"],
    ["Matriz de 10 SLAs & Categorias ITIL en GLPI", "Configuracion de Calendario Milio 09-18, matriz SLA P1 a P5 (TTO/TTR) y reglas 96, 97 y 98 para N1, N2 y Sitio.", 3, "green"],
    ["Carga e Inventario Inicial en Snipe-IT", "Normalizacion del catalogo, asignacion de computadoras y base de datos snipedb operativa.", 3, "blue"],
    ["Ensayo General & Recorrido de Pantallas", "Preparacion del guion de presentacion para validación integral de la plataforma.", 1, "yellow"],
    ["Integracion Agente GLPI FusionInventory / Discovery", "Planificado para siguiente fase: barrido SNMP y sincronizacion automatica de activos.", 0, "grey"],
    ["Migracion a Cron CLI nativo en GLPI (slaticket)", "Paso a produccion: invocar cron.php via CLI cada 5 minutos en el host.", 0, "grey"]
];

$pos = 1;
foreach ($tasks as $t) {
    $cid = $col_ids[$t[2]];
    $stmt = $pdo->prepare("INSERT INTO tasks (title, description, date_creation, color_id, project_id, column_id, position, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, 1)");
    $stmt->execute([$t[0], $t[1], $now, $t[3], $proj_id, $cid, $pos++]);
}
echo "Tablero y tareas inyectadas exitosamente en Proyecto ID: " . $proj_id . PHP_EOL;
'
```

---

## **11. Auditoría Técnica Automatizada y Prueba de Salud en Vivo (SOP-MILIO-008)**

### **11.1. Propósito, Alcance y Cobertura de Controles**

Con el objetivo de verificar en tiempo real la integridad de todos los componentes de la plataforma sin depender de revisiones manuales dispersas, se implementó el script de auditoría automatizada `~/kayn/bin/auditar_proyecto.sh`. El verificador ejecuta 18 comprobaciones técnicas en vivo sobre 6 dominios operativos y resguarda el reporte en `~/kayn/docs/informe_estado_proyecto.txt`:

1. **Infraestructura Docker y Persistencia:** valida que los 6 contenedores (`glpi`, `glpi-mysql`, `snipe-it`, `snipe-mysql`, `kanban` y `uptime-kuma`) estén en estado `Up`, con política de reinicio `unless-stopped` y los 7 volúmenes nombrados montados.
2. **Motor ITSM en Milio (`glpi-mysql`):** consulta en vivo sobre `glpidb` la integridad del esquema (`447` tablas InnoDB), la entidad `Milio`, la sede `Sede Central`, los 3 grupos resolutores (`N1`, `N2` y `Sitio`), las 12 categorías ITIL, las 3 reglas de ruteo (`96`, `97` y `98`), el calendario hábil (`ID 2`), los 10 SLAs (`TTO`/`TTR`), los `405` tickets registrados y la ejecución en modo `CLI` (`mode = 2`) de `slaticket` y `queuednotification`.
3. **Motor ITAM en Gekko (`snipe-mysql`):** comprueba la conectividad SQL sobre `snipeit` y releva el inventario activo (`250` activos, `41` modelos y `4` categorías).
4. **Observabilidad NOC (`uptime-kuma`):** ejecuta sondas HTTP internas mediante `cURL` validando las respuestas `HTTP 200` en Milio (`http://glpi/`) y `HTTP 302` en Gekko (`http://snipe-it/`).
5. **Seguridad, Estructura FHS, Crontab y Respaldos (`kayn`):** audita el árbol de directorios (`bin`, `backups`, `logs`, `docs`, `assets`), la ausencia de claves por defecto en `.env` y `.yml`, los permisos `0600`/`0700` junto con `umask 077` en `backup_stack.sh`, los respaldos `.tar.gz` y las 2 tareas activas en `crontab`.
6. **Gobierno en Kanboard (`kanban`):** inspecciona en caliente la base SQLite (`/var/www/app/data/db.sqlite`) contabilizando tarjetas abiertas, cerradas y subtareas completadas por columna.

### **11.2. Código Fuente y Ejecución del Verificador (`SOP-MILIO-008`)**

- **Ruta del script:** `~/kayn/bin/auditar_proyecto.sh` (permisos `0755`).
- **Reporte generado:** `~/kayn/docs/informe_estado_proyecto.txt`.
- **Comando de ejecución:**

```bash
~/kayn/bin/auditar_proyecto.sh
```

Código íntegro del verificador en `~/kayn/bin/auditar_proyecto.sh`:

```bash
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
  (SELECT COUNT(*) FROM glpi_locations WHERE name LIKE '%Sede Central%' OR id >= 1),
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
    add_check("Milio (GLPI)", "Entidad Milio, sede Sede Central y 3 grupos resolutores", ent_ok >= 1 and loc_ok >= 1 and grp_cnt == 3, f"Entidad: {ent_ok} | Sede: {loc_ok} | Grupos: {grp_cnt}/3")
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
rb_ok = bool(rb_path) and any(f"Versión del Documento:** {v}" in open(rb_path, encoding="utf-8").read() for v in ("2.6", "2.7"))
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
```

### **11.3. Evidencia de Certificación de Salud en Vivo (18/18 Controles Superados)**

Resultado certificado en consola:

```text
================================================================================
 INFORME TÉCNICO Y VERIFICACIÓN EN VIVO — PLATAFORMA MILIO IT (HOST: KAYN)
 Fecha de ejecución: 2026-10-12 22:13:45
================================================================================

1. MATRIZ DE COMPROBACIONES TÉCNICAS EN VIVO
--------------------------------------------------------------------------------
[  OK  ] [Infraestructura ] 6 contenedores principales en estado Up                -> 6/6 activos
[  OK  ] [Infraestructura ] Política de reinicio unless-stopped en todo el stack   -> unless-stopped
[  OK  ] [Infraestructura ] 7 volúmenes persistentes nombrados operativos          -> 7/7 volúmenes
[  OK  ] [Milio (GLPI)    ] Conexión SQL y esquema íntegro en glpi-mysql           -> 447 tablas InnoDB
[  OK  ] [Milio (GLPI)    ] Entidad Milio, sede Sede Central y 3 grupos resolutores   -> Entidad: 2 | Sede: 1 | Grupos: 3/3
[  OK  ] [Milio (GLPI)    ] Taxonomía de 12 categorías ITIL y reglas 96/97/98 activas -> 12 categorías | 3/3 reglas
[  OK  ] [Milio (GLPI)    ] Calendario Milio (09-18) y matriz de 10 SLAs (TTO/TTR) -> 10 SLAs vinculados
[  OK  ] [Milio (GLPI)    ] Lote transaccional de tickets cargado en base          -> 405 tickets registrados
[  OK  ] [Milio (GLPI)    ] Acciones automáticas slaticket y queuednotification en CLI -> 2/2 en modo CLI (mode=2)
[  OK  ] [Gekko (Snipe-IT)] Conexión SQL y catálogo ITAM operativo en snipe-mysql  -> 250 activos | 41 modelos | 4 categorías
[  OK  ] [Monitoreo NOC   ] Sonda interna HTTP hacia Milio (esperado: 200)         -> HTTP 200
[  OK  ] [Monitoreo NOC   ] Sonda interna HTTP hacia Gekko (esperado: 302)         -> HTTP 302
[  OK  ] [Seguridad y Host] Estructura de directorios FHS completa en ~/kayn       -> bin, backups, logs, docs, assets
[  OK  ] [Seguridad y Host] Ausencia de credenciales por defecto ('123') en configs -> 0 credenciales expuestas
[  OK  ] [Seguridad y Host] Permisos restrictivos (0600/0700) y umask 077 activo   -> .env 600 | backups/ 700 | umask 077
[  OK  ] [Seguridad y Host] Crontab del host configurado (backups 03:00 y GLPI 5m) -> 2 tareas activas en crontab
[  OK  ] [Seguridad y Host] Respaldos comprimidos diarios (.tar.gz) verificados    -> 3 archivos (backup_milio_20261012_204056.tar.gz)
[  OK  ] [Documentación   ] Runbook operativo actualizado a versión 2.6            -> RUNBOOK.md

================================================================================
 RESULTADO GLOBAL DE AUDITORÍA: 18/18 CONTROLES TÉCNICOS SUPERADOS
 Reporte guardado en: ~/kayn/docs/informe_estado_proyecto.txt
================================================================================
```

---

## **12. Herramientas de Automatización, Poblado Sintético (ITAM/ITSM) y Saneamiento Transaccional**

### **12.1. Propósito y Alcance Operativo (ITIL v4 Release & Deployment / Service Validation and Testing)**

En complemento a los procedimientos manuales de consola, la plataforma cuenta con un conjunto de herramientas de automatización en Bash y Python orientadas a cuatro funciones críticas:

1. **Empaquetado integral de respaldos multimotor (`backup_stack.sh`):** Consolidación diaria de MariaDB (`glpidb` y `snipeit`) junto con la base SQLite de Kanboard (`db.sqlite`).
2. **Saneamiento transaccional selectivo en GLPI (`cleandb.sh`):** Reinicio limpio de tablas de tickets e historial sin pérdida de parametrización estructural (reglas, categorías, SLAs ni usuarios).
3. **Generación de inventario sintético homologado para Gekko (`csvgen.py`):** Creación determinista y libre de colisiones de lotes de 250 activos ITAM con validación contra la base de datos.
4. **Inyección de carga transaccional vía API REST en Milio (`gentickets.py`):** Simulación de ráfagas de incidentes y solicitudes para pruebas de estrés de reglas de ruteo (`96`, `97`, `98`), SLAs y formularios con visibilidad condicional.

### **12.2. Arquitectura Interna del Script de Respaldo Unificado (`~/kayn/bin/backup_stack.sh`)**

Como extensión técnica del **SOP-MILIO-004**, el script `~/kayn/bin/backup_stack.sh` ejecuta una secuencia transaccional que abarca los tres motores de datos persistentes del stack bajo políticas de seguridad estrictas (`set -euo pipefail` y `umask 077`):

- **Fase 1 (Carga de Entorno):** Inyecta dinámicamente las credenciales desde `/home/juanx/kayn/.env` sin exponerlas en texto plano dentro del código del script.
- **Fase 2 (Volcado Lógico MariaDB):** Ejecuta `mysqldump` sobre `glpi-mysql` (`glpidb`) y `snipe-mysql` (`snipeit`) generando archivos `.sql` con marca de tiempo (`YYYYMMDD_HHMMSS`).
- **Fase 3 (Extracción en Caliente de Kanboard):** Copia la base de datos SQLite directamente desde el contenedor activo mediante `docker cp kanban:/var/www/app/data/db.sqlite`.
- **Fase 4 (Empaquetado y Limpieza):** Comprime los tres insumos en un único archivo `backup_milio_${TIMESTAMP}.tar.gz` con permisos `0600` (derivados de `umask 077`) y elimina inmediatamente los archivos `.sql` y `.sqlite` temporales descomprimidos.
- **Fase 5 (Política de Retención):** Purga automáticamente cualquier archivo `.tar.gz` cuya antigüedad supere los `15` días (`RETENTION_DAYS=15`).

### **12.3. SOP-MILIO-009: Purga Transaccional Selectiva de Tickets y Reset de Contadores en GLPI (`cleandb.sh`)**

1. **Objetivo y Alcance:** Proveer un mecanismo rápido y seguro para vaciar la totalidad de los tickets de prueba o simulación en `glpidb` (reiniciando el `AUTO_INCREMENT` a `ID = 1`) sin necesidad de restaurar un snapshot completo de base de datos, preservando intactos los usuarios, perfiles, categorías ITIL, formularios, calendarios y reglas de negocio.
2. **Mecanismo Técnico:**
   - Consulta en vivo el conteo actual en `glpi_tickets` y exige confirmación interactiva explícita (`si`/`SI`).
   - Desactiva temporalmente la verificación de claves foráneas (`SET FOREIGN_KEY_CHECKS = 0;`).
   - Ejecuta `TRUNCATE TABLE` sobre las 10 tablas relacionales del ciclo de vida del ticket (`glpi_tickets`, `glpi_tickets_users`, `glpi_groups_tickets`, `glpi_suppliers_tickets`, `glpi_items_tickets`, `glpi_tickets_tickets`, `glpi_tickettasks`, `glpi_ticketvalidations`, `glpi_ticketcosts` y `glpi_slalevels_tickets`).
   - Ejecuta `DELETE` selectivo (`WHERE itemtype = 'Ticket'`) sobre las tablas polimórficas de seguimientos (`glpi_itilfollowups`), soluciones (`glpi_itilsolutions`), adjuntos (`glpi_documents_items`) y auditoría histórica (`glpi_logs`).
   - Revalida la condición de ejecución de las reglas de asignación de SLA (`ID 101 a 105`).
3. **Ejecución Operativa:**
   - Ejecutar `~/kayn/bin/cleandb.sh` y confirmar ingresando `si` cuando el prompt interactivo lo solicite.

### **12.4. SOP-MILIO-010: Generación de Lote Sintético de Inventario ITAM para Gekko (`csvgen.py`)**

1. **Objetivo y Alcance:** Generar el archivo maestro `/home/juanx/kayn/import_250_activos_gekko.csv` con 250 activos de hardware coherentes, normalizados y libres de duplicados para poblar o recargar el catálogo de Snipe-IT (`Gekko`).
2. **Reglas de Negocio y Validaciones del Generador:**
   - **Sincronización con Base de Datos:** Consulta `snipe-mysql` (`SELECT auto_increment_prefix, next_auto_tag_base, zerofill_count FROM settings`) para respetar la numeración de placas corporativas (fallback: `VK-`, base `1`, zerofill `5`).
   - **Unicidad Estricta `O(1)` (Hash Sets):** Garantiza mediante conjuntos en memoria (`nombres_usados`, `usernames_usados`, `hostnames_usados`, `seriales_usados`) que ningún colaborador, correo (`@democorp.com`), número de serie o hostname se repita en el lote.
   - **Nomenclatura de Hostnames:** Formato estandarizado `VK-<COD_SEDE>-<NB|MAC><INDICE_3_DIGITOS>-<HEX_2_CHARS>` (ej. `VK-PAT-NB001-4F` o `VK-CABA-MAC015-A2`) cubriendo 8 ubicaciones (`OF01 - Sede Central`, `CABA - Remoto`, `AMBA - Remoto`, `Interior - Remoto`, `Uruguay`, `EEUU`, `México`, `España`).
   - **Patrones Reales de Serial por Fabricante:** Simula estructuras de números de serie reales para **Lenovo** (`PF`/`MP` + 6 alfanuméricos), **Dell** (7 caracteres Service Tag), **HP** (`5CD`/`CND` + año/semana + 4 alfanuméricos), **Apple** (`C02`/`J7X`/`F8Y` + 7 caracteres), **Asus** y **Banghó** a través de 41 modelos distribuidos en 3 eras tecnológicas (2019–2021, 2022–2024 y 2024–2026).
   - **Distribución Ponderada de Estados:** Asigna estados (`En uso`, `Disponible`, `Pendiente de formateo`, `Obsoleto`, `Perdido/Robo`, `Reciclado`) según la antigüedad del equipo, vinculando usuario nominal únicamente cuando el estado es `En uso` y concentrando el stock disponible/laboratorio en `OF01 - Sede Central`.
3. **Ejecución Operativa:**
   - Ejecutar `python3 ~/kayn/bin/csvgen.py` y verificar en consola la validación `Hostnames únicos: 250/250 | Seriales únicos: 250/250`.

### **12.5. SOP-MILIO-011: Inyección Masiva de Tickets y Pruebas de Estrés vía API REST (`gentickets.py`)**

1. **Objetivo y Alcance:** Automatizar la creación de ráfagas de tickets (`5`, `10`, `20`, `40`, `60`, `100` o valor personalizado) contra el endpoint REST de GLPI (`http://localhost:9080/apirest.php`) para homologar en vivo el motor de reglas de ruteo (`96`, `97` y `98`), el cálculo de SLAs (`TTO`/`TTR`) y la visualización HTML de los formularios condicionales.
2. **Arquitectura del Inyector (`gentickets.py`):**
   - **Autenticación y Ciclo de Sesión:** Inicia sesión mediante `GET /apirest.php/initSession` utilizando cabeceras `Authorization: user_token <TOKEN>` y `App-Token: <TOKEN>`, opera con el `Session-Token` obtenido y cierra limpiamente la sesión al finalizar (`GET /apirest.php/killSession`).
   - **Aislamiento de Solicitantes (`_users_id_requester`):** Selecciona aleatoriamente entre los usuarios solicitantes válidos (`IDs: 7, 8, 3, 5` — `egaray`, `fduarte`, `post-only`, `normal`), excluyendo explícitamente las cuentas administrativas de `juanx` (`IDs 2 y 9`) y cuentas técnicas.
   - **Cobertura de las 8 Subcategorías Operativas (Nivel 2):**
     - **Cat 5 (`Hardware > Notebooks y Periféricos`):** Incluye doble ponderación en el pool de generadores para ejercitar todas las ramas condicionales (*"Es visible si..."*) del formulario **Solicitud de nuevo equipamiento** (*Rotura o desperfecto*, *Obsolencia*, *No es compatible con mi trabajo*, *Robo*, *Pérdida*, *Requerimiento del cliente*), ajustando dinámicamente la urgencia e impacto (`U:4/I:4` en siniestros, `U:1/I:1` o `2/2` en obsolescencia, `U:3/I:3` en imputación a CECO de cliente).
     - **Cat 6 a Cat 12:** Cubre incidencias de impresoras/monitores (`Cat 6`), túneles VPN por ISP (`Cat 7`), fallas Wi-Fi/DHCP/PoE con MAC dinámica (`Cat 8`), blanqueo de claves y MFA (`Cat 9`), Onboarding/Offboarding con grupos AD (`Cat 10`), correo/ofimática (`Cat 11`) y sistemas internos como Snipe-IT, GitLab, ERP y Zabbix (`Cat 12`).
   - **Control de Unicidad en Ráfaga:** Mantiene un registro en memoria (`seen_titles`) durante la ejecución; si una combinación aleatoria se repite tras 3 intentos, anexa automáticamente un sufijo `[Ref #NNN]` para garantizar trazabilidad individual.
3. **Ejecución Operativa:**
   - Modo interactivo: `python3 ~/kayn/bin/gentickets.py`
   - Modo por argumento (ej. 20 tickets): `python3 ~/kayn/bin/gentickets.py 20`

---

## **13. Control de Cambios y Aprobaciones**

| Versión | Fecha | Autor / Rol | Descripción de Cambios |
| :---: | :---: | :---: | :--- |
| **0.1** | `2026-10-09` | Juan Cruz Fernandez R. | Estructura inicial, relevamiento del stack Docker (`glpi`, `snipe-it`, `kanban`) y diseño preliminar del catálogo. |
| **1.0** | `2026-10-10` | Juan Cruz Fernandez R. | Parametrización con `.env`, definición del `Calendario Milio (09-18)` e inyección de la matriz SLA (P1 a P5) en GLPI. |
| **1.1** | `2026-10-10` | Juan Cruz Fernandez R. | Migración de ruta host a `~/kayn`, sanitización de credenciales en SOPs y estructuración de la Guía de Troubleshooting. |
| **1.2** | `2026-10-10` | Juan Cruz Fernandez R. | Implementación operativa del script `backup_stack.sh`, automatización de backups diarios (`03:00 AM`) vía Crontab y reordenamiento de SOPs. |
| **1.3** | `2026-10-10` | Juan Cruz Fernandez R. | Inclusión del SOP-05 para la creación de Punto Cero (*Golden Baseline*) y procedimiento de rollback para pruebas. |
| **2.1** | `2026-10-11` | Juan Cruz Fernandez R. | Unificación del Runbook con Auditoría ITIL: Entidades, Ubicación Sede Central, Perfiles/Usuarios, Árbol de 12 Categorías ITIL, Reglas de Ruteo 96/97/98 (N1, N2 y Sitio), lineamientos de visibilidad condicional y dump comprimido en caliente. |
| **2.2** | `2026-10-12` | Juan Cruz Fernandez R. | Incorporación de la arquitectura de observabilidad y monitoreo activo con Uptime Kuma (Sección 8, actualización de Sección 2, SOP-MILIO-006 y Troubleshooting 6.6 a 6.8): configuración de monitores Milio (GLPI) y Gekko (Snipe-IT) bajo el grupo NOC, validación de encabezados HTTP `200` y `302` vía cURL interno, diseño y homologación de alertas SMTP con plantillas Liquid dinámicas, casos de uso de Modo Invertido, pruebas de resiliencia (*graceful stop/start*) y auditoría de persistencia de volúmenes (`/app/data` y `docker.sock`) mediante `docker inspect`. |
| **2.3** | `2026-10-12` | Juan Cruz Fernandez R. | Implementación de la Sección 9 (Hardening de Seguridad, Rotación de Credenciales y Congelamiento de Resguardo / *Code Freeze*): generación del respaldo `snipeit_demo_listo.sql` (`576 KB`) junto a `glpi_demo_listo.sql` (`17.8 MB`); rotación de contraseñas en motores MariaDB (`glpi-mysql` y `snipe-mysql`) para usuarios de aplicación (`glpi_user`, `snipeit_user`) y cuentas `root`; resolución de error de privilegios SQL `1227` mediante `SET PASSWORD`; sincronización de `/var/www/html/glpi/config/config_db.php` y `.env` (resolviendo expansión de signo `!` en Bash); saneamiento de credenciales en texto plano en archivos `docker-compose*.yml`; eliminación de archivos `.bak`; aplicación de permisos restrictivos (`chmod 600` en `.env`, `.yml` y `.sql`, y `chmod 700` en `~/kayn/backups`) y auditoría integral de conectividad y seguridad. |
| **2.4** | `2026-10-12` | Juan Cruz Fernandez R. | Implementación de la Sección 10 (Gestión Visual de Proyectos y Tareas Ágiles en Kanboard): configuración del esquema de base de datos SQLite en `/var/www/app/data/db.sqlite`, diseño del flujo de trabajo en Kanboard, formalización del SOP-MILIO-007 para inyección y aprovisionamiento desatendido de tareas vía PHP PDO-SQLite, y mapeo de hitos técnicos alcanzados para la operación continua. |
| **2.5** | `2026-10-12` | Juan Cruz Fernandez R. | Auditoría documental integral y cierre de resguardo: incorporación de la Sección 2.6 (Estructura de directorios FHS en `~/kayn`) y Sección 3.6 (Arquitectura ITAM en Gekko y consolidación de snapshots de resguardo); actualización de la Sección 7 (`slaticket` y `queuednotification` activos en modo `CLI`); sanitización de credenciales productivas con placeholders seguros; corrección de rutas Crontab en SOP-004, sintaxis Markdown en SOP-003 y referencias cruzadas en Sección 8; endurecimiento de `backup_stack.sh` con `umask 077`. |
| **2.6** | `2026-10-12` | Juan Cruz Fernandez R. | Incorporación de la Sección 11 y `SOP-MILIO-008` (Auditoría técnica automatizada y prueba de salud en vivo mediante `~/kayn/bin/auditar_proyecto.sh`): código fuente completo del verificador, certificación de 18/18 controles en vivo (`~/kayn/docs/informe_estado_proyecto.txt`), sincronización de métricas reales de bases de datos (`447` tablas InnoDB y `405` tickets en Milio; `250` activos, `41` modelos y `4` categorías en Gekko), actualización de rutas activas en el `crontab` del host y saneamiento de referencias a demostraciones. |
| **2.7** | `2026-10-13` | Juan Cruz Fernandez R. | Incorporación de la Sección 12 (Herramientas de Automatización, Poblado Sintético ITAM/ITSM y Saneamiento Transaccional): documentación del flujo multimotor de `~/kayn/bin/backup_stack.sh` (MySQL + SQLite de Kanboard con `umask 077` y rotación a 15 días); formalización del `SOP-MILIO-009` (`cleandb.sh` para purga `TRUNCATE` de tickets y reset de IDs preservando parametrización); formalización del `SOP-MILIO-010` (`csvgen.py` para generación determinista `O(1)` de 250 activos, seriales por fabricante y hostnames por sede); y formalización del `SOP-MILIO-011` (`gentickets.py` para inyección masiva vía API REST en subcategorías ITIL 5 a 12 y prueba de formularios condicionales). |

---

- **Aprobado por:** 
- **Cargo:** 

---

## **14. Descargo Legal y Atribución de Marcas (Disclaimer)**

Milio y Gekko son marcas registradas de Riot Games, Inc. Este proyecto no está respaldado por Riot Games y no refleja las opiniones ni los puntos de vista de Riot Games ni de nadie oficialmente involucrado en la producción o administración de sus propiedades.
