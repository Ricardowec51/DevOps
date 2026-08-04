# Mapa de Proyectos - Ricardo Wagner

**Última actualización:** 4 de Agosto de 2026 (auditoría de seguridad: secretos sueltos en home + disco externo)

---

## ⚠️ REGLA FIJA: todo proyecto nuevo se crea en el disco externo

**Todo proyecto nuevo (código, repos, scaffolding — cualquier cosa que empiece desde cero) debe crearse en `/Volumes/Externo`, NUNCA en el home (`/Users/rwagner`).** Esto es una instrucción permanente de Ricardo, no una preferencia puntual.

- Ubicación sugerida por defecto: `/Volumes/Externo/skills/<categoría>/` (ver estructura en la sección "Almacenamiento Externo" más abajo — `ai/`, `automation/`, `consulting/`, `infra/`, `web/`) o la raíz de `/Volumes/Externo` si no encaja en ninguna categoría.
- Esto aplica siempre que Ricardo pida "crear" o "empezar" un proyecto nuevo — antes de correr `git init`/`mkdir`/scaffolding de cualquier tipo, confirmar que la ruta de destino está bajo `/Volumes/Externo`.
- No aplica retroactivamente a proyectos ya existentes en el home (ej. `SUPACODE`, `pulso-final` en `Downloads`) — esos se quedan donde están salvo que Ricardo pida moverlos explícitamente.

---

## 📊 Resumen Ejecutivo

Este documento proporciona un inventario del estado actual de proyectos, repositorios y directorios de desarrollo en la máquina — **disco principal y disco externo**. La revisión del 29 de julio reveló que la mayoría del trabajo de negocio real de Ricardo (EMPRENDEDORES.LTD, ERP, herramientas para clientes, agentes SRI) vive en `/Volumes/Externo`, fuera del escaneo original de febrero, que solo cubría el home.

---

## 🗂️ Proyectos Propios (con remoto en cuenta de Ricardo)

### 1. **PULSO a la IA**
- **Ubicación real y activa:** `/Users/rwagner/.gemini/antigravity/scratch/pulso-ia-gemini` — **corrección 2026-08-04:** `~/Downloads/pulso-final` (anotado antes como la ubicación) está desactualizado; la copia que realmente corre en producción, con cron automático, es esta otra.
- **Remoto:** `github.com/Ricardowec51/pulso-ia` (el de `Downloads/pulso-final`; la copia activa en `.gemini/` no tiene remoto propio verificado)
- **Automatización:** crontab de macOS — lunes 8:00am genera+envía, 9:00am reintenta (`pulso_cron.sh`).
- **Descripción:** Newsletter semanal de IA de EMPRENDEDORES.LTD. Pipeline en Python (curación con Google Gemini) para generar, editar y enviar la edición por Gmail SMTP.
- **Bug corregido 2026-08-04:** `pulso_cron.sh` solo miraba si el `.docx` ya existía para decidir si reintentar — un fallo de SMTP (app password de Gmail vencida) en el intento de las 8am hacía que el reintento de las 9am no hiciera nada, y la Edición 31 nunca se envió. Se corrigió: `send_email()` ahora escribe un marcador `cache/edition_N.sent` solo tras éxito real, y el cron reintenta solo el envío (`--send-only`) si el docx existe pero el marcador no. Edición 31 reenviada manualmente. Ver memoria `project_pulso_ia.md`.
- **Nota de seguridad:** `Downloads/pulso-final/config.yaml` contiene API keys reales (Anthropic, Gemini, token de Facebook Graph API) en texto plano — está en `.gitignore`, nunca se comiteó.
- **Estado:** Activo y automatizado — próxima verificación programada para el lunes 10-ago (recordatorio en Google Calendar).

### 2. **proxmox-vm-creator**
- **Ubicación real:** `/Volumes/Externo/skills/infra/proxmox/proxmox-vm-creator` (NO en el home — se movió ahí en algún momento tras el 20 de enero de 2026; el registro de sesiones antiguo en `~/.claude/projects/-Users-rwagner-proxmox-vm-creator` quedó apuntando a la ruta vieja del home, que ya no existe)
- **Remoto:** `github.com/Ricardowec51/DevOps`
- **Último commit:** 2026-01-20 — "v4.0.0: K3s HA cluster deployment with interactive menu" (archivos modificados hasta 2026-06-20, aunque sin commits nuevos desde entonces)
- **Descripción:** Herramienta Python/Bash para crear y administrar VMs en el cluster Proxmox, usada para levantar el **K3s Cluster de EMPRENDEDORES.LTD** (ver `project_k3s_cluster.md`). Según `LAST.md`: cluster K3s HA funcionando con 8 nodos, MetalLB instalado (192.168.1.51-61), código subido a GitHub.
- **Incidente relevante:** 2026-01-18, VMs (3001, 3003, 3005) creadas por error en el nodo físico equivocado (DELL), lo que obligó a hacer hard reset de las máquinas físicas afectadas.
- **Pendiente:** implementar Proxmox HA para los VMs del cluster k3s una vez terminen las migraciones a `msa`/iSCSI-VMS (ver memoria `project_proxmox_ha` en `/Volumes/Externo`).
- **Estado:** Activo, ligado directamente a la infraestructura K3s en producción.

### 3. **emprendedores-ltda** ⭐ (sitio y servicio real a usuarios de EMPRENDEDORES.LTD)
- **Ubicación:** `/Volumes/Externo/skills/consulting/emprendedores-ltda`
- **Remoto:** `github.com/Ricardowec51/emprendedores-ltda`
- **Último commit:** 2026-07-29 — "Attach newsletter editions as PDF instead of raw .docx" (`2e118a5`, pusheado)
- **Descripción:** El sitio web, blog y **admin-panel reales de EMPRENDEDORES.LTD** — backend de contacto, generador de blog, páginas legales, suscripción a PULSO a la IA, deploy a Docker/K8s. Es el repo detrás del "admin-panel con imagen propia" ya anotado en la memoria del K3s Cluster.
- **Revisado y comiteado 2026-07-29:** el commit del 25 de julio (suscripción a PULSO) estaba solo en el disco externo, **nunca se había pusheado a GitHub** — ya está publicado. Además había una feature completa sin comitear (2 días, no meses): conversión automática de .docx → PDF con LibreOffice headless al subir una edición del newsletter, para adjuntar el PDF con el diseño real en vez del .docx crudo. A diferencia de `factuscan`, aquí sí existía la migración SQL lista y **es idempotente** (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`) — se comiteó y pusheó (`2e118a5`).
- **Pendiente de verificar por Ricardo:** si la migración (`k8s/migration-pdf-ediciones.sql`) ya se aplicó contra la base de datos real del cluster, y si la imagen del admin-panel en producción ya incluye LibreOffice — no se tocó ni la BD ni el deploy, solo el código en git.
- **Estado:** **El proyecto más activo de todos**, ahora al día con GitHub.

### 4. **MiERP** ⭐ (prioridad futura alta — decisión explícita de Ricardo, NO archivar)
- **Ubicación:** `/Volumes/Externo/MiERP`
- **Remoto:** `github.com/Ricardowec51/MiERP`
- **Último commit:** 2026-05-11 — "docs: Add comprehensive MODULES.md reference guide"
- **Descripción:** ERP propio basado en un **fork completo de Odoo** (repo de 1.5GB: `addons/` 1GB + `odoo/` 113MB de código estándar de Odoo, no propio).
- **Revisado 2026-07-29:** lo propio de Ricardo vive en `custom_addons/` — 9 módulos (`mierp_base`, `mierp_accounting`, `mierp_sale`, `mierp_purchase`, `mierp_inventory`, `mierp_hr`, `mierp_project`, `mierp_helpdesk`, `mierp_portal`), pero son **puro scaffolding**: 392KB, 546 líneas de Python en total, cada módulo solo extiende modelos de Odoo con 2-4 campos de ejemplo, sin lógica de negocio real. 5 commits, todos el mismo día (2026-05-11) — armado en una sola sesión, sin tocar desde entonces. No hay `docker-compose.yml` ni evidencia de que se haya llegado a ejecutar/conectar a PostgreSQL.
- **Decisión de Ricardo (2026-07-29):** **se queda activo, es prioridad futura de mucha importancia.** El objetivo es convertirlo en un ejecutable de primer orden, completamente configurado.
- **Diagnóstico del Odoo descargado (2026-07-29) — VIABLE, mejor de lo esperado:** `odoo-bin --version` corrió sin errores ("Odoo Server 19.0", versión reciente) — el clon está íntegro, sin corrupción. El `venv/` tiene las 69 dependencias correctas instaladas, coincidiendo exactamente con los pins de `requirements.txt` para Python 3.12 (psycopg2, gevent, lxml, reportlab, Werkzeug, etc.) — no quedó a medias.
- **Setup local completado (2026-07-29):** PostgreSQL 14 corriendo, BD `mierp_dev` creada, `odoo.conf` creado. **Servidor confirmado corriendo de verdad** (`curl` → HTTP 200 en `/web/login`, no solo "instala sin error"). **8 de 9 módulos propios instalados y funcionando:** `mierp_base`, `mierp_accounting`, `mierp_sale`, `mierp_purchase`, `mierp_inventory`, `mierp_project`, `mierp_helpdesk`, `mierp_portal`. `mierp_hr` bloqueado por dependencia a `hr_payroll` (Odoo Enterprise, no disponible en Community) — ver documento dedicado para las 3 opciones. Falta instalar `wkhtmltopdf` (Homebrew ya no lo tiene) para reportes PDF, no bloqueante.
- **Se encontraron y corrigieron 5 categorías de bugs reales en el scaffolding** (nunca se había probado contra un Odoo corriendo): 27 archivos `.po`/`.pot` sin la línea de módulo requerida por Odoo 19; orden de carga `menu.xml`/vistas invertido en 8 manifests; `mierp_helpdesk` con `<tree>` en vez de `<list>`, chatter sin `mail.activity.mixin`, y una vista referenciada antes de definirse; 4 módulos con IDs de acciones de Odoo core mal escritos; `mierp_portal` referenciaba una acción que nunca se había creado (se creó desde cero). Detalle completo en el documento de abajo.
- **Comiteado y pusheado 2026-07-29** (`97989c58`, `github.com/Ricardowec51/MiERP`) — los 53 archivos + el documento de estado ya están respaldados en GitHub.
- **Documento detallado de continuación:** `/Volumes/Externo/MiERP/ESTADO-Y-PLAN-2026-07-29.md` — contiene cada bug con archivo/línea, estado de cada uno de los 9 módulos, las 3 opciones para `mierp_hr`, y una tabla verificada (vía búsqueda web, 2026-07-29) de qué repos de OCA (Odoo Community Association) tienen rama `19.0` disponible para cada dominio (ventas, compras, inventario, RRHH, nómina, helpdesk, portal) — incluye que `OCA/helpdesk` es candidato fuerte a reemplazar `mierp_helpdesk` completo, y que `OCA/l10n-ecuador` **todavía no soporta Odoo 19** (solo hasta 17.0).
- **Comando de arranque (2026-07-30):** `mierp` — global, en `~/.local/bin/mierp` (wrapper con `exec`, sigue el mismo patrón que el comando `pulso` de PULSO a la IA). Llama a `/Volumes/Externo/MiERP/mierp.sh` (comiteado y pusheado, `2e8b0184`), que levanta PostgreSQL si no está corriendo y arranca Odoo contra `mierp_dev` en `http://localhost:8069`. `Ctrl-C`/`kill` lo detiene limpio sin dejar procesos huérfanos (se corrigió un bug de eso durante la prueba — el wrapper inicial no usaba `exec`).
- **Verificado arrancando de nuevo 2026-07-30** (un día después del setup): PostgreSQL persistió, BD intacta, 103 módulos cargan sin errores, HTTP 200 real en `/web/login`. No fue una casualidad del primer arranque.
- **Estado:** Corriendo localmente, 8/9 módulos instalados, comando global `mierp` para levantarlo — pero es solo scaffolding funcional, sin lógica de negocio real. **Debe continuarse pronto** (instrucción explícita de Ricardo). Ver memoria dedicada `project_mierp.md` y el documento de arriba.

### 5. **k3s-ha-cluster** ⭐ (importante — infraestructura real de la red doméstica de Ricardo)
- **Ubicación:** `/Volumes/Externo/k3s-ha-cluster`
- **Remoto:** `github.com/Ricardowec51/k3s-ha-cluster`
- **Último commit:** 2026-07-29 — "Restructure README: production-grade framing, per-script docs, prerequisites" (`9de3625`)
- **Descripción:** Instalador profesional del cluster K3s HA — `k3s_installer_complete.sh` (orquesta 3 masters con kube-vip para IP flotante + MetalLB para balanceo), `scripts/utils/` (health-check.sh, backup-cluster.sh), `provisioning/proxmox/` (deploy vía Ansible/scripts interactivos). Complementa a `proxmox-vm-creator` (éste crea las VMs, aquél instala y configura K3s sobre ellas).
- **Corrección 2026-07-29:** el "duplicado idéntico" en `GitProjects/k3s-ha-cluster` que se había anotado antes **no era un duplicado** — al revisarlo resultó ser un repo sin relación de historial, un solo commit de **marzo de 2025** (10 meses antes de que empezara este repo), con K3s en una versión vieja fijada y scripts mucho más simples sin kube-vip/MetalLB/Ansible: el **prototipo original**, superado por este repo. **Archivado** a `/Volumes/Externo/archive/old-projects/k3s-ha-cluster-prototipo-2025-03` (movido, no borrado).
- **Estado:** Activo — cambio pendiente en el README ya comiteado y pusheado.

### 6. **bg-pdf-excel** (baja prioridad — desactualizado, confirmado por Ricardo)
- **Ubicación:** `/Volumes/Externo/skills/consulting/clientes/bg-pdf-excel`
- **Remoto:** `github.com/Ricardowec51/bg-pdf-excel`
- **Último commit:** 2025-10-24
- **Descripción:** App Streamlit + script de consola que convierte Estados de Cuenta del **Banco Guayaquil** (PDF) a Excel (movimientos + resumen). Explica los PDFs "00-Mov...BG" encontrados en `Downloads` — es una herramienta para un cliente/contabilidad propia.
- **Revisado 2026-07-29:** hay un cambio grande sin comitear en `app.py` desde el 27 de octubre de 2025 (615 líneas, 9 meses sin comitear) — agrega soporte para un formato nuevo de estado de cuenta del banco, con pinta de estar terminado, no a medias. **Ricardo confirmó que el proyecto es de poca importancia y está desactualizado — no se comiteó ni se tocó nada.**
- **Estado:** Baja prioridad, sin acción pendiente.

### 7. **Agentes SRI Ecuador (facturación electrónica)** — 3 líneas de desarrollo para el mismo problema, NO todas duplicadas
- **`codex-sri-v1`** (`/Volumes/Externo/codex-sri-v1`, sin remoto/solo local) — **el más avanzado y activo** (última actividad 2026-05-10). Su `DOCUMENTATION_LOG.md` documenta que llegó a **"AGENTE FUNCIONAL END-TO-END"** el 2026-02-21: automatiza login Keycloak + navegación del portal SRI en Línea, y **resolvió el bloqueo de reCAPTCHA Enterprise** haciendo clic directo en "Descargar reporte" sin pasar por el botón "Consultar" (que sí tiene CAPTCHA). Herramienta de descarga, no de gestión.
- **`documento-sri-v1a`** y **`sri-document-mgr`** — comparten el mismo remoto (`Ricardowec51/Agente_Documentos_SRI_v2`) desde un commit de origen común (`973e306`), pero **NO son duplicados**: cada uno tenía trabajo real sin comitear en direcciones distintas. **Ambos comiteados y pusheados el 2026-07-29:**
  - `documento-sri-v1a`: contiene **~150 comprobantes reales del SRI ya escaneados** (PDF+XML) en `documents/`. Se comiteó el trabajo de empaquetado para Windows y migración a SQLite (commit `c967f8f`) y se pusheó a **`main`** — es la rama principal del repo en GitHub.
  - `sri-document-mgr`: mitad de una **reescritura del backend de Python/FastAPI a Go**. Se comiteó (commit `77a123d`) y se pusheó a una **rama nueva `go-rewrite`** (no a `main`, para no pisar el trabajo de `documento-sri-v1a` que ya estaba ahí — ambos apuntan al mismo repo remoto). PR abierto para revisar: `github.com/Ricardowec51/Agente_Documentos_SRI_v2/pull/new/go-rewrite`.
  - Quedó sin comitear (build artifacts, no código fuente): `bin/server` y `server` (binarios Go compilados) en `sri-document-mgr`; `windows-package/`, `claude-windows-package/`+`.zip`, `backend/static/` en `documento-sri-v1a`.
  - **`sri-dashboard-revamp/`** (55MB, dentro de `documento-sri-v1a`, nunca comiteado) resultó ser un **cuarto intento de dashboard** (FastAPI+SQLite+Vite/React, sin Docker) pero **solo un prototipo abandonado**: `backend/data/` vacío, arranca con datos ficticios (no reales), sin actividad desde el 16 de febrero de 2026, y el 90% de su peso era `node_modules/`+`.venv/` reinstalables. **Archivado el 2026-07-29** junto con la carpeta basura `cd sri-dashboard-revamp` (nombre de un comando mal ejecutado que quedó como directorio) a `/Volumes/Externo/archive/old-projects/` (movidos, no borrados).
  - **Pendiente de decisión de Ricardo:** ¿cuál rama se vuelve la definitiva — `main` (Python, con datos reales) o `go-rewrite` (Go)? No es una decisión técnica que deba tomar unilateralmente.
  - **Seguridad (2026-08-04):** `backend/inject_credentials.py` (idéntico en ambos repos) tenía un Google OAuth `client_secret` real hardcodeado, ya pusheado a `origin/main` (repo privado). Corregido para leer de variables de entorno; **credencial rotada en Google Cloud Console** y `.env` de ambos repos actualizado. El fix de `sri-document-mgr` se pusheó a `go-rewrite` (no a `main`, que es la línea de trabajo de `documento-sri-v1a` — mismo remoto, ramas distintas) — tracking local reapuntado para evitar un push accidental a `main`. Detalle en memoria `project_sri_agents.md`.
- **`documento-sri`** (sin sufijo) — era el ancestro común original de los dos anteriores, sin datos (`documents/` vacío) y sin trabajo único. **Archivado el 2026-07-29** a `/Volumes/Externo/archive/old-projects/documento-sri` (movido, no borrado).
- **`factuscan-ec/worker`** — enfoque distinto (Node.js): monitoreo de correo (IMAP) para extraer XML/PDF de comprobantes y centralizarlos en Google Sheets/Drive. **Revisado y archivado 2026-07-29** (decisión de Ricardo): su propio `CONTINUITY_MEMO.md` decía que el plan siempre fue migrar el almacenamiento de Google Sheets a Postgres/K8s — exactamente lo que ya es `factuscan` en producción (ver sección propia abajo, proyecto distinto en código). Había 2 días de trabajo real sin comitear después del último commit (Dockerfile, ~20 scripts de depuración, log de un escaneo de 20,011 correos con fallos de sincronización a Google Sheets/Drive) que quedó sin resolver. **Hallazgo de seguridad:** tenía `google-key.json` (clave de cuenta de servicio de Google real) y `accounts.json` (Gmail real + contraseña de aplicación) sin protección en `.gitignore` — nunca se comitearon ni pushearon, pero corregí el `.gitignore` (agregado `google-key.json`, `accounts.json`, `*.key.json`) antes de archivar. **Archivado** a `/Volumes/Externo/archive/old-projects/factuscan-ec` (movido, no borrado) — las credenciales siguen ahí en disco; considerar rotarlas si ya no se usan.

### 8. **factuscan** ⭐ (en producción — no es un experimento, sirve a EMPRENDEDORES.LTD ahora mismo)
- **Ubicación:** `/Volumes/Externo/factuscan`
- **Remoto:** ninguno (solo local — recomendable crear uno y respaldarlo en GitHub)
- **Último commit:** 2026-07-29 — "Add invoice status tracking (RECIBIDO/VISTO/APROBADO/CONTABILIZADO)" (`d564900`, sin pushear por no haber remoto)
- **Descripción:** Backend FastAPI + frontend React/Vite que escanea Gmail por IMAP, detecta comprobantes electrónicos del SRI en los adjuntos, los parsea (facturas, NC, ND, retenciones, guías) y los almacena en PostgreSQL. **Desplegado en el cluster K3s**: frontend `http://192.168.1.59`, backend `http://192.168.1.61:8000`, BD en `192.168.1.55:5432`. Verificado funcionando con datos reales (1816 correos escaneados, 14 comprobantes SRI detectados de proveedores reales).
- **Corresponde a** la entrada "factuscan-backend" ya anotada en la memoria del K3s Cluster — es el mismo servicio.
- **Revisado y comiteado 2026-07-29:** había 6 meses de trabajo sin comitear (sistema de estados de comprobantes: RECIBIDO→VISTO→APROBADO→CONTABILIZADO). Se comiteó el código (`d564900`), **pero deliberadamente no se tocó la base de datos ni se redesplegó nada** — según decisión de Ricardo, dado que falta un paso crítico documentado en el propio `PROGRESS.md` del proyecto: generar y aplicar una migración de Alembic para la nueva columna `estado` contra el Postgres de producción antes de reconstruir/redesplegar las imágenes Docker.
- **Pendiente (requiere acción manual de Ricardo, no automatizable sin supervisión):** generar la migración Alembic, aplicarla contra `192.168.1.55`, reconstruir imágenes Docker (`ricardowec/factuscan-backend`/`-frontend`), pushear a Docker Hub, redesplegar en K3s.
- **Seguridad (2026-08-04):** `k8s/secret.yaml` tenía el password real de Postgres y el app-password real de Gmail en texto plano desde el primer commit (repo sin remoto, nunca salió del disco). Convertido en plantilla; valores reales movidos a `k8s/secret.local.yaml` (gitignorado). `CLAUDE.md` actualizado para que los comandos de deploy documentados usen el archivo correcto.
- **Estado:** Producción activa, con una mejora lista pero sin desplegar.

---

## 🗂️ Repos de Terceros Clonados/Forkeados (uso o customización personal)

### 9. **Supacode**
- **Ubicación:** `/Users/rwagner/SUPACODE`
- **Remotos:** `origin` → `github.com/supabitapp/supacode` (upstream), `personal` → `github.com/ricardowec51/supacode` (fork propio)
- **Último commit:** 2026-06-23 — "Fix build-ghostty-xcframework to exit 0 when xcframework is produced"
- **Descripción:** Terminal/entorno de desarrollo tipo Claude Code que Ricardo usa a diario y sobre el cual tiene un fork propio para cambios. Ver skill `supacode-cli` y memoria `env_supacode_local_network_bug.md` (bug de red LAN dentro de Supacode).
- **Estado:** Activo, en desarrollo.

### 10. **ghostty-config**
- **Ubicación:** `/Users/rwagner/ghostty-config`
- **Remoto:** `github.com/zerebos/ghostty-config` (solo clon, sin fork propio)
- **Último commit:** 2026-07-11
- **Descripción:** Configuración del terminal Ghostty. Relacionado con el plan de "Red Thunderbolt en anillo" y su setup de terminal.

### 11. **worldmonitor**
- **Ubicación:** `/Users/rwagner/worldmonitor`
- **Remoto:** `github.com/koala73/worldmonitor` (solo clon)
- **Último commit:** 2026-07-14 (autor upstream, no Ricardo)
- **Descripción:** Dashboard de monitoreo de eventos globales/geopolíticos.
- **Revisado 2026-07-29 (solo lectura, por pedido explícito de Ricardo de no tocarlo):** working tree limpio, sin commits propios — se mantiene sincronizado vía `git pull`. `node_modules` instalado el mismo día del último pull. No hay `.env` real (solo `.env.example`), no hay procesos ni contenedores corriendo. Sin conclusiones ni acciones sugeridas sobre este proyecto — Ricardo pidió respetarlo tal cual.

~~### 12. AI Image Head Corrector~~ y ~~13. imap-smtp-email-skill / clawddocs~~ — **borrados el 2026-07-30** (housekeeping de disco, confirmado por Ricardo). Ninguno tenía actividad ni valor: sin git, sin cambios recientes, o paquetes de terceros sin relación con desarrollo propio.

---

## 🗑️ Proyectos que ya NO están (vs. mapa anterior)

- **Agent Zero** (`~/Desktop/agent-zero`) y **Agent Zero 1** (`~/Desktop/agent-zero1`) — ya no existían en Desktop. **2026-07-30 (housekeeping, confirmado por Ricardo):** se borró también el remanente `~/Downloads/..agent-zero-0.7.1/` y una caché huérfana de GitKraken (`~/.gitkraken/repohooks/agent-zero-*`) vinculada al repo viejo — no queda nada de Agent Zero en el disco principal (siguen 2 clones de referencia en el disco externo, ver sección de "ruido").
- **Housekeeping de disco 2026-07-30:** también se borraron, todos vacíos/sin actividad y confirmados por Ricardo: `~/Desktop/carpeta sin título` y `carpeta sin título 2` (vacías), `~/Documents/New project` (repo git sin ningún commit), `~/email-manager` (cáscara sin código real), `pulso-final 2/3` y `pulso-ubuntu` (duplicados de PULSO a la IA), `ai-image-head-corrector`, `imap-smtp-email-0.0.10` y `clawddocs-1.2.2` (paquetes de terceros sin relación con desarrollo propio).
- **openclaw-mission-control** — archivado el 2026-07-29 a `/Users/rwagner/Archive/openclaw-mission-control` (decisión: nunca se desplegó en 5 meses, y su `services/news-bot` duplicaba lo que ya hace **PULSO a la IA**, activo y en producción). No se borró nada — el código, incluyendo `services/news-bot` sin comitear, queda intacto ahí por si se quiere rescatar el bot de Telegram más adelante.
- **factuscan-ec/worker** — archivado el 2026-07-29 a `/Volumes/Externo/archive/old-projects/factuscan-ec` (prototipo abandonado cuyo plan siempre fue convertirse en `factuscan`, que ya está en producción; tenía credenciales reales de Google/Gmail expuestas sin protección de `.gitignore` — corregido antes de archivar).
- **`documento-sri`** (sin sufijo) y **`sri-dashboard-revamp`** — archivados a `/Volumes/Externo/archive/old-projects/` (ver sección de Agentes SRI).
- **`k3s-ha-cluster` prototipo de marzo 2025** (antes en `GitProjects/`) — archivado a `/Volumes/Externo/archive/old-projects/k3s-ha-cluster-prototipo-2025-03` (ver sección de k3s-ha-cluster).

---

## 🧹 Ruido en el disco externo (clones de referencia/tutoriales, NO desarrollo propio)

Encontrados en la revisión del 2026-07-29 — no requieren entrada individual, solo ocupan espacio y confunden el inventario:

- `my_zsh_install.sh`, `Wireguard Install` — repos de referencia de un solo script.
- `JimsGarage` — tutorial/repo de referencia, **duplicado 3 veces** (`/Volumes/Externo/JimsGarage`, `scripts/Initial/JimsGarage`, `GitHub/Jim Garage/JimsGarage`).
- `Initial` — repo de referencia, **duplicado 4+ veces** en distintas carpetas (`scripts/Initial`, `GitHub/Initial`, `archive/old-projects/Initial-repo`, `scripts/Initial/Sin título`, `GitHub/Jim Garage/Sin título.jpg`).
- Otro clon de **Agent Zero** en `GitHub/Initial/Agent-Zero/agent-zero` y `skills/ai/agents/agent-zero` — van 3 copias contando las que ya no están en el home.
- `postgres-operator` / `postgres-operator-examples` — duplicados en `skills/infra/kubernetes/` y `skills/infra/docs/...` (material de referencia).
- `self-hosted-ai-starter-kit`, `Wan2.2` — clones de herramientas de terceros para referencia/pruebas.
- `archive/old-projects/my-skills-repo`, `archive/old-projects/Initial-repo` — ya archivados por Ricardo mismo, sin acción necesaria.

---

## 📦 Repositorios Git Detectados (resumen)

| Repo | Ruta | Remoto | Último commit |
|---|---|---|---|
| Home dotfiles | `/Users/rwagner` | `Ricardowec51/DevOps` (⚠️ **público** — confirmado 2026-08-04) | 2026-08-04 |
| Documents | `/Users/rwagner/Documents` | — | — |
| Documents/New project | `/Users/rwagner/Documents/New project` | — | — |
| Supacode | `/Users/rwagner/SUPACODE` | supabitapp + fork personal | 2026-06-23 |
| ghostty-config | `/Users/rwagner/ghostty-config` | zerebos/ghostty-config | 2026-07-11 |
| worldmonitor | `/Users/rwagner/worldmonitor` | koala73/worldmonitor | 2026-07-14 |
| pulso-final | `/Users/rwagner/Downloads/pulso-final` | Ricardowec51/pulso-ia | 2026-05-28 |
| proxmox-vm-creator | `/Volumes/Externo/skills/infra/proxmox/proxmox-vm-creator` | Ricardowec51/DevOps | 2026-01-20 |
| **emprendedores-ltda** ⭐ | `/Volumes/Externo/skills/consulting/emprendedores-ltda` | Ricardowec51/emprendedores-ltda | 2026-07-29 (`2e118a5`, pusheado) |
| **MiERP** | `/Volumes/Externo/MiERP` | Ricardowec51/MiERP | 2026-05-11 |
| **k3s-ha-cluster** (externo) | `/Volumes/Externo/k3s-ha-cluster` | Ricardowec51/k3s-ha-cluster | 2026-07-29 (`9de3625`, pusheado) |
| **bg-pdf-excel** | `/Volumes/Externo/skills/consulting/clientes/bg-pdf-excel` | Ricardowec51/bg-pdf-excel | 2025-10-24 |
| **codex-sri-v1** | `/Volumes/Externo/codex-sri-v1` | (local, sin remoto) | 2026-05-10 (última actividad) |
| **documento-sri-v1a** (con datos reales, empaquetado Windows) | `/Volumes/Externo/documento-sri-v1a` | Ricardowec51/Agente_Documentos_SRI_v2 (privado) — rama `main` | 2026-08-04 (`4040509`, pusheado — fix de seguridad OAuth) |
| **sri-document-mgr** (reescritura en Go) | `/Volumes/Externo/sri-document-mgr` | Ricardowec51/Agente_Documentos_SRI_v2 (privado) — rama `go-rewrite` | 2026-08-04 (`61676ab`, pusheado — mismo fix) |
| ~~documento-sri (sin sufijo)~~ | archivado 2026-07-29 → `/Volumes/Externo/archive/old-projects/documento-sri` | (sin git) | — |
| **factuscan** ⭐ (en producción) | `/Volumes/Externo/factuscan` | (local, sin remoto) | 2026-07-29 (`d564900`) |
| ~~factuscan-ec/worker~~ | archivado 2026-07-29 → `/Volumes/Externo/archive/old-projects/factuscan-ec` | Ricardowec51/Facturacion-Electronica | 2026-01-26 |
| oh-my-zsh | `/Users/rwagner/.oh-my-zsh` | (framework, no es proyecto propio) | — |
| bash-it | `/Users/rwagner/.bash_it` | (framework, no es proyecto propio) | — |
| nvm | `/Users/rwagner/.nvm` | (herramienta, no es proyecto propio) | — |

---

## 🔌 Infraestructura y Automatización (ver memoria para detalle)

- **K3s Cluster (EMPRENDEDORES.LTD)** — 3 masters + 5 workers, storage TrueNAS. Ver memoria `project_k3s_cluster.md` para estado detallado (worker-03 cordoned, admin-panel con imagen propia, etc.).
- **n8n** — Instancia remota en `https://n8n.rwagnerit.com` (v1.122.4). Datos locales de una instancia anterior en `~/n8n-data/` (sqlite, posiblemente legado/local). MCP servers configurados: `n8n-remote` (OAuth) y `n8n-mcp` (docs). Ver skill `n8n-mcp-setup`.
- **OpsCenter/ollama** — `/Users/rwagner/OpsCenter/ollama`, config de Ollama local.
- **Home Assistant (HA)** — secundario; control real de casa vía Alexa. Ver `project_haos.md`.
- **Red y servidores** — pendiente revisión mayor (prioridad alta). Ver `project_revision_red.md`.

---

## 🔧 Herramientas de Desarrollo Configuradas

### Editores / CLIs de IA:
- **Claude Code** — `.claude/` (proyectos rastreados: home, Downloads, SUPACODE, `/Volumes/Externo` y subcarpetas — incluye proxmox-vm-creator, aunque el registro antiguo en `~/.claude/projects/` aún apunta a su ruta previa en el home)
- **Codex** — `.codex/`, y `Documents/Codex/`
- **Cursor** — `.cursor/`
- **Antigravity**, **Codegpt**, **Gemini CLI** (`.gemini/`), **cagent** (`.cagent/`)

### Contenedorización:
- **Docker**, **Colima**, **OrbStack** — `.docker/`, `.colima/`, `OrbStack/`
- **Kubernetes** — `.kube/`, `.kuberlr/`, `.minikube/`, cluster K3s remoto

### Control de versiones:
- **Git**, **GitHub CLI (gh)**, **GitKraken** (`.gk/`, `.gitkraken/`)

### Terminal:
- **Ghostty** (`.config/ghostty/`, `.config/ghostty-config/`, `~/ghostty-config`), **iTerm2**, **WezTerm** (`.wezterm.lua`), **Warp** (`.warp/`)

---

## 💾 Almacenamiento Externo

### Skills Directory (Symlink)
- **Ruta Local:** `/Users/rwagner/skills` → **Real:** `/Volumes/Externo/skills`
- **Contenido:** `ai/`, `automation/`, `consulting/`, `infra/`, `web/`

### /Volumes/Externo
- Contiene mucho almacenamiento personal (PDFs, imágenes, ISOs, backups), **pero también la mayoría de los proyectos de negocio activos de Ricardo** (`emprendedores-ltda`, `MiERP`, `bg-pdf-excel`, `codex-sri-v1`, `proxmox-vm-creator`, `k3s-ha-cluster`) — no es solo un disco de respaldo. Tiene su propio `.claude/` (proyectos de Claude Code abiertos desde ahí) y estructura `skills/{ai,automation,consulting,infra,web}/` donde vive buena parte de este código.

---

## 🛠️ Stack Tecnológico

- **Python** — Conda/Miniconda3, Ollama, scripts de PULSO a la IA
- **JavaScript/TypeScript** — npm, nvm, bun (`.bun/`)
- **Bash/Zsh** — dotfiles propios en el repo home, oh-my-zsh, bash-it
- **Go, Rust, PHP, Java** — soporte vía IDEs/toolchains instalados (rustup, extensiones VS Code), sin proyecto propio identificado actualmente

---

## 📊 Estadísticas

| Concepto | Cantidad |
|----------|----------|
| Repositorios Git detectados (total, ambos discos) | 21 |
| Proyectos propios activos (remoto propio) | 10 (Supacode fork, PULSO a la IA, proxmox-vm-creator, emprendedores-ltda, MiERP, k3s-ha-cluster, bg-pdf-excel, codex-sri-v1, factuscan, factuscan-ec/worker) |
| Repos de terceros clonados sin fork | 2 (ghostty-config, worldmonitor) |
| Duplicados/copias del mismo repo a limpiar | JimsGarage x3, Initial x4+, agent-zero x2 (quedan en disco externo, referencia) — todos los duplicados del disco principal ya se limpiaron el 2026-07-30 (sri-document-mgr/documento-sri-v1a resultaron NO ser duplicados, ver sección SRI) |
| Proyectos retirados/archivados/borrados desde el mapa anterior | 4 archivados (Agent Zero, Agent Zero 1, openclaw-mission-control, documento-sri sin sufijo) + 12 borrados en housekeeping de disco 2026-07-30 |
| Volúmenes externos | 1 (`/Volumes/Externo`) — resultó tener más proyectos propios activos que el disco principal |

---

## 🎯 Próximos Pasos Recomendados

1. **Agentes SRI:** seguridad resuelta (2026-08-04) — OAuth `client_secret` rotado y código corregido en ambos repos, push de `sri-document-mgr` resuelto a `go-rewrite` sin tocar `main`. Sigue pendiente la decisión de fondo: ¿cuál rama se vuelve la definitiva, `main` (Python, con datos reales) o `go-rewrite`? `codex-sri-v1` (descarga vía portal) sigue intacto como herramienta separada.
2. **factuscan (PRODUCCIÓN):** seguridad de `k8s/secret.yaml` resuelta (2026-08-04, ver sección propia). Sigue pendiente el paso crítico manual — generar y aplicar la migración Alembic contra el Postgres real (`192.168.1.55`), reconstruir imágenes Docker y redesplegar en K3s. No automatizar esto sin supervisión directa de Ricardo. También sería buena idea crear un remoto en GitHub para este repo (hoy solo existe local).
3. **emprendedores-ltda:** verificar si la migración `k8s/migration-pdf-ediciones.sql` ya se aplicó contra la BD real del cluster, y si hace falta reconstruir/redesplegar la imagen del admin-panel con LibreOffice incluido para que la conversión .docx→PDF funcione en producción.
4. **PULSO a la IA:** corregida la ubicación real en este documento (era `Downloads/pulso-final`, la activa es `.gemini/antigravity/scratch/pulso-ia-gemini`) y el bug del retry de email (2026-08-04, ver sección propia). Verificación del cron programada para el 10-ago.
5. Quedan copias de referencia de Agent Zero / JimsGarage / Initial en el disco externo (`skills/ai/agents/agent-zero`, `GitHub/Initial/Agent-Zero`, etc.) — no se tocaron, son del disco externo, fuera del housekeeping del disco principal del 2026-07-30.
6. `proxmox-vm-creator`: al día, sin pendientes (ver commit `4a8190c` del 2026-07-29).
7. **MiERP** (prioridad futura alta): setup local completo, servidor corriendo, 8/9 módulos instalados, todo comiteado y pusheado (`97989c58`). Ver `/Volumes/Externo/MiERP/ESTADO-Y-PLAN-2026-07-29.md` para el plan completo: decidir estrategia de `mierp_hr`/nómina, evaluar módulos OCA (`helpdesk`, `account-invoicing`, etc. — todos con rama 19.0 verificada) antes de seguir construyendo funcionalidad propia.
8. Atender la revisión mayor de red/servidores pendiente (prioridad alta, ver memoria).
9. Si en algún momento se quiere un canal de noticias por Telegram, revisar `~/Archive/openclaw-mission-control/services/news-bot` antes de construir uno nuevo desde cero.
10. **Seguridad (2026-08-04):** auditoría completa de secretos sueltos en home + disco externo — ver `project_home_secrets_audit_2026_08_04.md` y `project_disco_externo_secrets_audit_2026_08_04.md` en memoria. Nota importante descubierta de paso: el repo `Ricardowec51/DevOps` (este mismo repo de dotfiles del home) es **público** en GitHub, no privado — tenerlo presente antes de comitear cualquier cosa nueva ahí.

---

## 📞 Información del Sistema

- **Usuario:** rwagner
- **Sistema Operativo:** macOS (Darwin), ProductVersion 26.5.2 (Build 25F84)
- **Kernel Darwin:** 25.5.0
- **Procesador:** Apple Silicon (arm64)
- **Shell:** zsh/bash con oh-my-zsh

---

**Nota:** Este documento fue actualizado a partir de un escaneo del sistema en vivo (git remotes, últimos commits, estructura de directorios) el 29 de julio de 2026. Se recomienda regenerarlo periódicamente en lugar de mantenerlo a mano.
