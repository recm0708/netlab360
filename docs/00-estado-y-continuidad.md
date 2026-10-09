# NETLAB360 — Registro de inicialización de GitHub

Fecha inicial: 2026-10-09 (Panamá, UTC−05:00).

## Repositorio
- Canonical: https://github.com/recm0708/netlab360
- Visibilidad: PRIVATE.
- Rama principal: `main`.
- Repositorio inicializado con README y workflow `.github/workflows/bootstrap-github.yml`.

## Trabajo registrado
- Ocho issues de fase: #1–#8, con checklist transversal y criterios de cierre.
- Veintinueve issues técnicas: #9–#37, correspondientes a los identificadores [001]–[029] de la plantilla.
- Todas las issues abiertas, asignadas a `recm0708`.
- Workflow de gestión para etiquetas `semana:01` a `semana:08`, tipos/prioridades y milestones `S01` a `S08`; verificar resultado del workflow antes de dar por habilitada la clasificación.

## Pendientes inmediatos
- [ ] Importar íntegramente la plantilla local `NETLAB360_Planificacion_v0.2.zip` a la raíz de este repositorio (sin anidar carpeta contenedora).
- [ ] Verificar etiquetas y milestones generados por GitHub Actions.
- [ ] Comparar cuerpos de las issues con los archivos de `backlog/`; sincronizar únicamente si no afecta checkboxes ya trabajados.
- [ ] Verificar que el pipeline CI inicial sea exitoso y no involucre operaciones de red privilegiadas.
- [ ] Confirmar versiones compatibles para Ubuntu Desktop y VMware (no instalar por ser «la última» sin verificación). Se revisaron referencias oficiales para 26H1u1; falta inspección local del equipo.
- [ ] Preparar laboratorio mínimo de F1 con segmentación, ruta de respaldo y evento realmente observable.
- [ ] Abrir tres entregables editables y comenzar evidencias desde F1.
- [ ] Registrar requisitos nuevos de la docente como cambios controlados.

## Reglas de continuidad
1. Antes de continuar, leer este registro, `README.md`, `docs/03-roadmap.md` y las issues abiertas del hito correspondiente.
2. El estado observado y los resultados de los comandos prevalecen sobre supuestos de configuración.
3. No cerrar issues por completar solamente comandos; deben existir evidencia, comprobación operacional, documentación y recuperación.
4. Los archivos de máquina virtual, credenciales y state sensible no se almacenan en Git.
5. Un issue o un comentario puede contener una decisión, pero una decisión arquitectónica duradera debe registrarse también en `docs/decisiones/`.

## Condición de entrega
Cada fase es un candidato demostrable independiente; el cumplimiento definitivo queda condicionado a los requisitos/rúbrica que publique la docente. No se declarará un SLO, failover, IA, streaming ni LAG «validado» sin prueba reproducible.

## Estado de preparación del entorno (2026-10-09)
- El usuario aprobó **crear VM nueva VMware Workstation sin ISO**; queda documentado en `docs/decisiones/ADR-001-vmware-vm-sin-iso.md`.
- Se iniciaron las tareas #10, #34, #1 y #29 mediante comentarios de seguimiento. Ningún criterio de creación o instalación de VM se declara completado.
- VMware Workstation Pro **26H1u1 (26.0.1 build 25688693)** ya está verificado, con i9-12900H (14 núcleos, 20 hilos), 63.70 GB RAM y espacio libre suficiente en C:.
- Tras ajuste del usuario, VMware muestra **8 vCPU**, 16 GB RAM, disco SCSI 160 GB y NIC NAT.
- **Ubuntu Desktop 26.04.1 LTS instalado**; usuario `rc-aa-ec`, hostname `netlab360-lab`, `nproc=8`, RAM 15 GiB, `/dev/sda2` 157 GB, kernel `7.0.0-38-generic`, SSH y VMware Tools activos.
- Se abrió la issue **#38** para Ubuntu Desktop + SSH. Guía versionada: `docs/infraestructura/02-ubuntu-desktop-instalacion-ssh.md`.
- **VMnet8/IP administrativa definitiva propuesta y aplicada:** `192.168.47.40/24`, fuera del pool DHCP `192.168.47.128–254` y reservas declaradas. Gateway `192.168.47.2`; DNS `.2` y `1.1.1.1`; perfil `netlab360-gestion`. Gateway e Internet 4/4 pings, DNS funcional. ADR-002 actualizado.
- **SSH Windows comprobado con clave:** credencial Ed25519 de cliente generada en `C:\\Users\\ruben\\.ssh\\netlab360_ed25519`, clave pública autorizada, login sin contraseña de Ubuntu validado, alias `ssh netlab360` probado. La llave requiere passphrase local. Entrada antigua `.130` no se eliminó.
- **Reinicio completo comprobado:** IP manual `192.168.47.40/24`, perfil `netlab360-gestion`, gateway `192.168.47.2`, servicio SSH y VMware Tools activos; DNS `github.com` operativo.
- **GitHub CLI:** `gh` versión 2.46.0 instalada desde Ubuntu; intento `gh auth login -h github.com -p https -w` falló al intentar abrir navegador Snap en sesión SSH sin variable `DISPLAY`. La autorización de GitHub no ha concluido.
- Se ha recomendado **rotar la contraseña compartida en chat** y no documentarla ni reutilizarla en otros servicios. No almacenar secretos.
- Issue #38 y guía `docs/infraestructura/02-ubuntu-desktop-instalacion-ssh.md` actualizadas.

## Pausa operativa solicitada — 2026-10-09
- **Objetivo actual:** instalar dependencias base y detenerse sin desplegar redes ni servicios del proyecto. Solo se realizará preparación de plataforma.
- **GitHub CLI autenticado:** `gh auth status` confirmó la cuenta `recm0708` en github.com, repo privado `recm0708/netlab360` visible, `gh auth setup-git` aplicado.
- **Git clonado:** `~/proyectos/netlab360`; `git status --short --branch` mostró `## main...origin/main`, sin cambios locales antes de esta actualización remota.
- **Issue #40:** autenticación y clonación completadas, cerrada. **Issue #41:** instalación de herramientas y pausa operativa, abierta.
- **Instalador pendiente de ejecución en VM:** `scripts/bootstrap/preparar-entorno-ubuntu.sh` (APT base, GitHub CLI oficial, Docker/Compose/Buildx, Ansible, OpenTofu, Node.js 24 LTS, herramientas de red). No declarar instalado ningún componente hasta recibir salidas.
- **Guía de ejecución/pausa:** `docs/infraestructura/04-preparacion-herramientas-pausa.md`.
- **Herramientas diferidas al inicio de implementación:** FRRouting/OVS/Faucet, Containerlab, Prometheus y servicios web/IA; se versionarán y probarán dentro de entornos aislados.
- **Template v0.2 pendiente:** se conserva y se importará solo con revisión para no sobrescribir documentos posteriores, sin duplicar issues.
- **Seguridad:** token GitHub y llave cliente SSH permanecen en el invitado/Windows; **sanitizar antes de exportar VM a docente**. Rotar la contraseña que fue compartida en conversación.

## Próxima acción
1. Abrir PowerShell `ssh netlab360`; `cd ~/proyectos/netlab360 && git pull --ff-only origin main`.
2. `bash -n scripts/bootstrap/preparar-entorno-ubuntu.sh` y, tras revisar el contenido, `bash scripts/bootstrap/preparar-entorno-ubuntu.sh`.
3. Verificar versiones Docker/Ansible/OpenTofu/Node/GitHub CLI, estado `docker/ssh/open-vm-tools`, IP, disco y logs de instalación.
4. Actualizar issues y registrar resultados; no cerrar #41 hasta confirmación.
5. Detener VM limpiamente con `sync; sudo systemctl poweroff`. Confirmar apagado en VMware.
6. Cuando el usuario regrese, iniciar VM, comprobar `ssh netlab360`, hacer mantenimiento de actualizaciones y retomar #41/S01 sin inventar nuevos estados.
