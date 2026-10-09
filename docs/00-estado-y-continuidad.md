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
- **Ubuntu Desktop 26.04.1 LTS instalado y reiniciado**; usuario `rc-aa-ec`, hostname `netlab360-lab`, `nproc=8`, RAM 15 GiB detectados, `/dev/sda2` 157 GB, kernel `7.0.0-38-generic`, IPv4 `192.168.47.130/24`, gateway `192.168.47.2`, SSH y VMware Tools activos.
- Se abrió la issue **#38** para Ubuntu Desktop + SSH. Guía versionada: `docs/infraestructura/02-ubuntu-desktop-instalacion-ssh.md`.
- **Conexión SSH Windows pendiente:** IP usada anteriormente tiene entrada distinta en `known_hosts`; verificar huella ED25519 local de nueva VM y reemplazar solo esa entrada. Usuario correcto `rc-aa-ec` (no `root`).
- Se ha recomendado **rotar la contraseña compartida en chat** y no documentarla ni reutilizarla en otros servicios. No almacenar secretos.
- Issue #38 y guía `docs/infraestructura/02-ubuntu-desktop-instalacion-ssh.md` actualizadas.

## Próxima sesión
1. Desde Ubuntu obtener fingerprint: `sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256` y comprobar que coincide con la huella reportada por Windows.
2. En Windows `Test-NetConnection 192.168.47.130 -Port 22`; solo tras comparar huella, `ssh-keygen -R 192.168.47.130` y `ssh rc-aa-ec@192.168.47.130`.
3. Instalar/verificar llave Ed25519 para acceso seguro, actualizar #38, evidencias y bitácora.
4. Importar plantilla v0.2 al repositorio ya existente, sin recrear las 38 issues.
