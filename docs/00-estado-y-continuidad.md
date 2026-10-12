# NETLAB360 — Registro de inicialización de GitHub

## ESTADO VIGENTE — 2026-10-12, 18:16 Panamá: B2-L2 DEMOSTRADO

**Priorizar este bloque cuando se retome el proyecto o se abra otra conversación.** El hito B1 concluyó satisfactoriamente, la **primera prueba VLAN B2-L2 está ejecutada y validada**, y está preparado el **preflight B2-L3/OSPF**. **La fase S01 sigue abierta** porque aún faltan WAN/OSPF, telemetría, API/dashboard, analítica y entregables.

### Último trabajo confirmado

- **VM:** Ubuntu 26.04.1 LTS en VMware Workstation 26H1u1, hostname `netlab360-lab`, usuario `rc-aa-ec`, 8 vCPU/16 GB RAM/160 GB disco, SSH desde PowerShell `ssh netlab360` con llave Ed25519. Gestión `ens33=192.168.47.40/24`, gateway `.2`, VMnet8 aislada de laboratorio.
- **B0/B1:** APT actualizado, Docker/SSH/VMware Tools activos; IPAM B1 validado (3 sedes, 9 VLAN y 2 WAN propuestas, S2 reservada), sin colisiones con rutas/redes activas del host; kernel soporta módulos 8021q/bonding/openvswitch/veth/bridge.
- **Ejecución B2-L2 2026-10-12 18:16:01:** `bash scripts/laboratorio/b2-l2-aislado.sh --snapshot-confirmado`. Prueba positiva VLAN 110 (3/3, 0.068ms RTT medio); cambio del puerto sw-b a VLAN 120 impide respuesta ICMP; restauración a VLAN 110 (3/3, 0.044ms RTT medio). `PRUEBA B2-L2: OK`, `CODIGO_FINAL: 0`, `RESULTADO_B2=0`. Namespaces eliminados, rutas/IP de ens33 intactas y ningún contenedor Docker. Local Git `## main...origin/main` limpio inmediatamente después de la prueba, **antes de nuevos commits remotos**.
- **Reinicio intermedio:** se ejecutó `sync; sudo systemctl poweroff`, SSH se desconectó normalmente. Un SSH inmediato agotó el tiempo durante VM apagada; siguiente SSH exitoso tras encenderla. **La existencia de snapshot `NETLAB360-BASE-HERRAMIENTAS` no se observó directamente en VMware**. El argumento `--snapshot-confirmado` declara confirmación del operador, no un chequeo programático; pedir al usuario confirmación de Snapshot Manager antes de enrutamiento.
- **Evidencias B1:** el usuario dijo haber tomado dos capturas PNG (no subidas a GitHub). No ha indicado todavía captura B2. Log B2 local `~/netlab360-bootstrap/evidencias/05-b2-l2-20261012-181601.log` (~1.6KiB); bitácora GitHub `docs/sesiones/2026-10-12-prueba-vlan-l2-b2.md` (no contiene secretos).
- **GitHub:** issue #12 actualizada, permanece abierta; #11 y #41 también abiertas. Diseño preliminar para siguiente paso: `docs/arquitectura/03-frr-ospf-dual-wan-b2-plan.md`, diagnóstico `scripts/diagnostico/precheck-frr-b2.sh`. Imagen candidata oficial `quay.io/frrouting/frr:10.7.1` **NO descargada ni verificada**.
- **Próximas instrucciones para Ubuntu, SOLO LECTURA:**
  ```bash
  cd ~/proyectos/netlab360
  GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
  bash -n scripts/diagnostico/precheck-frr-b2.sh
  bash scripts/diagnostico/precheck-frr-b2.sh
  echo "RESULTADO_PREFLIGHT_FRR=$?"
  ls -lh ~/netlab360-bootstrap/evidencias/06-b2-frr-precheck-*.log
  ```
  El diagnóstico lee host/Docker/IPAM y consulta el manifiesto de imagen oficial. **No descarga, instala ni ejecuta FRR ni toca interfaces**.
- **Después del preflight:** revisar compatibilidad del tag/arquitectura, confirmar snapshot, decidir descarga versionada de imagen FRR y generar ensayo WAN dual OSPF aislado con corte/restauración y rollback. No afirmar rutas ni adyacencias antes de pruebas. Diferenciar doble WAN OSPF, LACP, redundancia de equipo y trunks 802.1Q.
- **Regla de trazabilidad:** actualizar este encabezado, issues y bitácoras al completar un hito sustancial o antes de la próxima pausa; usuario prefiere varios comandos agrupados. No almacenar token OAuth (ubicado en `~/.config/gh/hosts.yml`) en repositorio/OVA; permisos 600 y directorio GH 700.

---

## HITO DE REANUDACIÓN — B1 validado; primer ensayo L2 B2 PREPARADO, no ejecutado

**Fecha:** 2026-10-12, después de 18:03 Panamá. **Estado actual:** B1 IPAM y capacidades del kernel verificados; no hay infraestructura empresarial desplegada, no hay VLAN real, OSPF, LACP, FRR ni OVS instalados.

- El usuario aportó `RESULTADO_L2=0` del script `precheck-l2-b1.sh`: módulos `8021q`, `bonding`, `openvswitch`, `veth` y `bridge` disponibles (solo bridge cargado). `ip_forward=1`, `ens33 192.168.47.40/24`, gateway `.2`, `docker0 172.17.0.0/16`, cero namespaces y contenedores. Servicios activos, 8 vCPU y aproximadamente 13 GiB disponibles. `VALIDACIÓN B1: OK` reiterada y Git limpio al final de la comprobación anterior a nuevos commits.
- El usuario **ya tomó dos capturas**: `B1_01_Validacion_IPAM_y_Redes.png` y `B1_02_Compatibilidad_Capa2.png`. **No están incorporadas al repositorio**, no pedir repetirlas. Logs locales `03-b1-preflight-20261012-173813.log` y `04-b1-compatibilidad-l2-20261012-180335.log`, en `~/netlab360-bootstrap/evidencias/`.
- Bitácoras GitHub: `docs/sesiones/2026-10-12-validacion-ipam-b1.md` y `docs/sesiones/2026-10-12-compatibilidad-l2-b1.md`; issue #11 comentada/actualizada.
- Nueva decisión propuesta `docs/decisiones/ADR-003-redes-virtuales-aisladas.md`: utilizar inicialmente Linux network namespaces, veth y Linux bridge para ensayo L2; FRRouting/OSPF después, con OVS/Faucet y LACP tratados separadamente. **Propuesta, no validación operativa**.
- Nuevo script preparatorio `scripts/laboratorio/b2-l2-aislado.sh`: test aislado con dos endpoints VLAN 110, separación de puerto VLAN 120 y restauración, con limpieza al terminar; **NO se ha ejecutado**. Requiere argumento `--snapshot-confirmado` y comprobaciones previas; no se modifica ens33. Versionado para revisión, no sustituye inspección y `bash -n`.
- **BLOQUEO ANTES DE EJECUTAR PRUEBA:** confirmar la instantánea VMware `NETLAB360-BASE-HERRAMIENTAS`. Ninguna salida de usuario ha confirmado todavía su creación. Si existe, verificar desde VMware; si no, apagar VM ordenadamente, crear snapshot con VM apagada, encender de nuevo y verificar `ssh netlab360`.
- **PRÓXIMA SECUENCIA:** `cd ~/proyectos/netlab360 && GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`; `bash -n scripts/laboratorio/b2-l2-aislado.sh`; verificar snapshot; si está confirmado, ejecutar `bash scripts/laboratorio/b2-l2-aislado.sh --snapshot-confirmado` y revisar su salida y `sudo ip netns list`, ruta/IP, Docker y log `05-b2-l2-*.log`. Si falla, detenerse y revisar salida, sin repetir ni agregar otras redes.
- Al obtener pruebas funcionales, actualizar issue #12, bitácora, evidencias y esta ancla; no cerrar S01 ni declarar failover OSPF hasta demostración.

---

## ANCLA DE REANUDACIÓN — Estado vigente 2026-10-12, 18:03 Panamá

**Lee esta sección antes que los registros históricos situados más abajo.** NETLAB360 sigue en S01, B1: IPAM y **compatibilidad L2/L3 del kernel ya verificados**. La matriz de conexiones es propuesta, todavía no implementada. **No hay red empresarial desplegada ni Fase 1 cerrada**.

1. **VM:** Ubuntu Desktop 26.04.1 LTS, host `netlab360-lab`, usuario `rc-aa-ec`, VMware Workstation Pro 26H1u1, 8 vCPU, 16 GB RAM, disco virtual 160 GB. Gestión exclusiva por `ens33=192.168.47.40/24` y NAT `192.168.47.2`; Windows PowerShell `ssh netlab360` con llave ED25519.
2. **Post-reinicio validado:** `docker`, `ssh`, `open-vm-tools` activos, 0 unidades fallidas; GitHub CLI autenticado como `recm0708`, `git pull` exitoso y rama limpia en revisión de las 16:58; APT actualizado, `dpkg --audit` sin salida.
3. **Toolchain:** Docker Engine 29.9.0, Compose 5.6.0, Buildx 0.38.0, containerd 2.4.1, OpenTofu 1.13.1, Ansible Core 2.20.1, Python 3.14.4, Node.js 24.21.0, npm 11.19.0, gh 2.102.0; Docker hello-world OK; 136 GB disponibles según inventario anterior.
4. **Checkpoint:** base B0 sana técnicamente. **Snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` aún no confirmado**, pendiente issue #41. No reiniciar instalador.
5. **B1 IPAM YA VERIFICADO (2026-10-12, 17:38):** Git pull exitoso; validador IPAM **OK** (3 sedes, 9 VLAN, 2 WAN y 15 redes incluida VMnet8), preflight de host/Docker **RESULTADO_B1=0** (14 redes virtuales sin choque con 3 rutas/redes activas), PyYAML 6.0.3, 8 vCPU/13Gi disponibles/136GB libres, servicios activos, sin contenedores. Evidencia local: `~/netlab360-bootstrap/evidencias/03-b1-preflight-20261012-173813.log`. Bitácora: [validación B1](sesiones/2026-10-12-validacion-ipam-b1.md). Diseño **aún no desplegado**. Ver issue #11.
6. **PRECHECK L2/L3 YA VERIFICADO 18:03:35**: `bash -n` correcto, `bash scripts/diagnostico/precheck-l2-b1.sh` **RESULTADO_L2=0**, evidencia `~/netlab360-bootstrap/evidencias/04-b1-compatibilidad-l2-20261012-180335.log`. Módulos disponibles `8021q`, `bonding`, `openvswitch`, `veth`, `bridge` (solo `bridge` cargado). `ip/tc/bridge/docker` presentes; `ovs-vsctl`, `vtysh`, `containerlab` no instalados. Rutas y ens33 sin cambios, Docker sin contenedores, IPAM validado OK. Bitácora [L2](sesiones/2026-10-12-compatibilidad-l2-b1.md). **SIGUIENTE:** elegir aislamiento de switches/FRR, verificar snapshot VMware y luego planificar pruebas B2; no instalar o crear recursos aún.
7. **Trazabilidad:** issue #11 actualizada con IPAM y L2 exitosos. El usuario **ya capturó dos evidencias** `B1_01_Validacion_IPAM_y_Redes.png` y `B1_02_Compatibilidad_Capa2.png` (archivos de imagen no localizados/subidos al repo todavía). Logs originales solo locales. Bitácoras: [IPAM](sesiones/2026-10-12-validacion-ipam-b1.md) y [L2](sesiones/2026-10-12-compatibilidad-l2-b1.md). Política de pausas en `docs/05-plan-operativo-y-pausas.md`.
8. **Seguridad y bloqueo B2:** GH CLI guarda credenciales en `~/.config/gh/hosts.yml` con permisos 600; no compartir token ni empaquetarlo en OVA. No usar `ens33` como switch emulado. **Snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` sin confirmación; no crear bridges, redes virtuales ni topología B2 hasta tenerlo**. El paquete v0.2 de planificación NO se ha importado.

---


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
1. Antes de continuar, leer este registro, `README.md`, `docs/05-plan-operativo-y-pausas.md` y las issues abiertas del hito correspondiente.
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

## Pausa operativa: resultado final registrado (2026-10-09, 15:06–15:10 EST)

**La preparación no terminó. NO declarar Docker, OpenTofu, Ansible ni Node.js instalados por este script.**

- `git pull --ff-only origin main` completó fast-forward a commit `7644cf5`, se revisó script y `bash -n` no mostró errores.
- Al ejecutar `scripts/bootstrap/preparar-entorno-ubuntu.sh`, creó el archivo `~/netlab360-bootstrap/evidencias/02-preparacion-herramientas-20261009-150619.log` y **abortó en `sudo -v`** tras tres intentos de autenticación incorrecta. Por `set -e`, ningún paquete del script llegó a instalarse.
- Verificación posterior: `sudo docker` → `command not found`; servicio docker inactivo. `ssh` y `open-vm-tools` activos, IPv4 `192.168.47.40/24`, raíz 157G/137G disponibles, sin reinicio requerido. Git limpio (`## main...origin/main`).
- Se ejecutaron `sync` y `sudo systemctl poweroff`. El enlace SSH se cerró con `Connection reset`; es compatible con apagado, pero la confirmación visual de VMware sigue pendiente.
- Issue #41 **permanece abierta**. No se activaron simulaciones, redes, containers ni aplicaciones del proyecto.
- La contraseña de sudo en Ubuntu corresponde al usuario **rc-aa-ec**, no a la frase de contraseña de la llave SSH privada de Windows. No enviar ni almacenar ningún secreto. Verificar distribución teclado y Caps Lock desde consola VMware si falla.

## Próxima acción cuando el usuario solicite reanudar

1. Confirmar desde VMware que la VM está apagada; si es así, no es necesario hacer nada hasta el siguiente día de trabajo.
2. Al regresar, encender VM en VMware y desde PowerShell abrir `ssh netlab360`.
3. En Ubuntu, ejecutar **primero** `sudo -k && sudo -v` introduciendo la contraseña actual del usuario Ubuntu (no la passphrase SSH) y verificar que retorna sin error. Si falla, detenerse y revisar desde consola VMware. No insistir con el instalador.
4. Desde Ubuntu, `cd ~/proyectos/netlab360 && git pull --ff-only origin main`. El remoto habrá avanzado debido a esta actualización documental.
5. Ejecutar `bash -n scripts/bootstrap/preparar-entorno-ubuntu.sh`; luego `bash scripts/bootstrap/preparar-entorno-ubuntu.sh`. Corregir errores de compatibilidad repositorio/paquete en el paso específico; no instalar servicios de topología.
6. Validar versiones, `sudo docker run --rm hello-world`, Docker/SSH/open-vm-tools activos, IP, Git limpio y evidencias. Actualizar #41.
7. Solo después de comprobar que la preparación terminó, crear instantánea de recuperación y apagar ordenadamente.


## Reanudación 2026-10-12 — sudo restaurado, Git HTTPS solicita credenciales

- `whoami` identifica `rc-aa-ec`; `sudo -k` y `sudo -v` funcionaron. Problema de autenticación local Ubuntu **resuelto**.
- Antes de iniciar el instalador, `git pull --ff-only origin main` detuvo el flujo solicitando usuario y contraseña de GitHub. **No hay constancia de pull completado ni de instalación de dependencias en esta sesión**.
- No introducir contraseña de GitHub por HTTPS. Verificar `gh auth status -h github.com` y `gh api user --jq .login`; luego `gh auth setup-git --hostname github.com` para configurar el helper oficial. Reintentar con `GIT_TERMINAL_PROMPT=0 git ls-remote --heads origin main`, después `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`. Si falla, inspeccionar el helper sin exponer tokens.
- Si `gh auth status` indica que OAuth ha caducado, autorizar desde navegador Windows mediante `GH_BROWSER=/bin/true gh auth login -h github.com -p https -w` con código temporal (no compartir código).
- Tras Git: hacer mantenimiento preventivo `sudo apt update`, consultar actualizaciones con `apt list --upgradable`, ejecutar `sudo apt upgrade -y`; reiniciar si `/var/run/reboot-required` aparece y verificar SSH/IP/servicios. No forzar phased updates.
- Ejecutar instalador `scripts/bootstrap/preparar-entorno-ubuntu.sh` solo tras volver a verificar `sudo`, Git y versión del script.
- Issue #41 continúa abierta hasta versiones y pruebas confirmadas. No declarar Docker/OpenTofu/Ansible/Node instalados.

## Estado vigente — 2026-10-12, instalación base completada

El segundo intento de preparación **sí completó** todas las etapas del script. Tras cancelar el prompt de Git, Bash ejecutó las siguientes órdenes ya suministradas. Actualizó 19 paquetes, instaló herramientas base y verificó Docker `hello-world`, OpenTofu, Ansible, GitHub CLI y Node.js. Ver registro `docs/sesiones/2026-10-12-preparacion-base-validada.md`.

- Docker Engine 29.9.0; Compose 5.6.0; Buildx 0.38.0; containerd 2.4.1.
- OpenTofu 1.13.1, Ansible Core 2.20.1, Python 3.14.4.
- Node 24.21.0, npm 11.19.0, gh 2.102.0.
- Servicios `docker`, `ssh`, `open-vm-tools` activos; IP fija .40; 136 GB libres; sin reboot requerido.
- GH CLI informó que la sesión local no está autenticada y la llamada `gh api user` devolvió HTTP 401. El `git pull` inicial **no se completó**.
- No ejecutar de nuevo script bootstrap. Reautorizar GH CLI desde navegador Windows, ejecutar `gh auth setup-git --hostname github.com`, verificar con `GIT_TERMINAL_PROMPT=0 git ls-remote --heads origin main`, luego `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`.
- Tras confirmar Git, registrar snapshot y apagar; las fases de red aún no se iniciaron.

## Bloques y checkpoints incorporados — 2026-10-12

- Se acordó avanzar por **bloques funcionales sustanciales** (B0 base, B1 IPAM, B2 red y failover, B3 telemetría y dashboard, B4 diagnóstico, B5 documentación), no por pausas a cada subpaso.
- Conservar evidencia, prueba y commits antes de pausas largas. Ofrecer pausa tras completar uno o varios bloques útiles o aproximadamente 2–4h de trabajo concentrado; **no ejecutar apagados sin decisión del usuario**.
- La fase S01 planificada para 5–11 de octubre está abierta el 12; no reprogramar fechas ni declarar cumplida sin pruebas. La meta inicial ahora es consolidar B0 y empezar B1 en esta sesión.
- **Plan maestro operativo:** `docs/05-plan-operativo-y-pausas.md` (creado). README enlaza la guía.
- **Confirmado en esta conversación:** GH CLI autenticado como `recm0708`; `gh auth setup-git --hostname github.com`, `git ls-remote --exit-code origin refs/heads/main` y `git pull --ff-only origin main` exitosos. Rama local `main...origin/main` limpia al concluir, antes de nuestros commits posteriores de planificación.
- **Siguiente comando en Ubuntu:** `cd ~/proyectos/netlab360 && GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main` para incorporar estos nuevos documentos; después salud de red, dpkg, APT, Docker, disco, SSH y token protegido. NO volver a ejecutar script instalador ya terminado.
- **Pendiente:** instantánea base `NETLAB360-BASE-HERRAMIENTAS`, inicio arquitectura IPAM #11; OAuth de GH en `~/.config/gh/hosts.yml` sin cifrar: asegurar permisos y sanitizar antes de exportar VM.

## Precheck final B0 y reinicio de Windows solicitado — 2026-10-12, 11:20 Panamá

- Git: `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main` exitoso; `git status --short --branch` mostró `## main...origin/main`, sin cambios locales en ese momento. Se hicieron commits remotos posteriores a la revisión: al retomar debe ejecutarse otro pull.
- Credenciales GH CLI: carpeta `~/.config/gh` permisos `700`, archivo `hosts.yml` permisos `600`; siguen sin cifrar; no difundir ni incluir en una OVA.
- APT: `sudo apt update` informó todos los paquetes al día; `sudo apt upgrade -y` registró **0 actualizados, 0 instalados, 0 eliminados, 0 pendientes**. `sudo dpkg --audit` vacío, `systemctl --failed` **0 unidades**. Aviso Ubuntu Pro ESM Apps informativo sin impedir el mantenimiento.
- Los servicios `docker`, `ssh`, `open-vm-tools` mostraron `active`; sin contenedores Docker. Docker Compose **v5.6.0**.
- `ens33` `192.168.47.40/24`, puerta de enlace `192.168.47.2`; raíz 157G con **136G libres**; **NO SE REQUIERE REINICIO** del invitado por actualizaciones.
- El usuario **decidió reiniciar Windows anfitrión**, no terminar todavía S01. Se aconseja apagar **antes** la VM desde SSH con `git status --short --branch; sync; sudo systemctl poweroff`, verificar visualmente que aparece apagada en VMware, tomar snapshot `NETLAB360-BASE-HERRAMIENTAS` con VM apagada y después reiniciar Windows. **Ejecución/confirmación del apagado y snapshot aún no recibidas**.
- No hay más dependencias base por instalar ahora. FRR/OVS/Faucet/Containerlab/Prometheus/backend frontend/IA quedarán para fases del diseño.
- Tras reiniciar Windows: abrir VMware, arrancar `NETLAB360-Ubuntu-Desktop` solamente si se continúa; en PowerShell `ssh netlab360`; en Ubuntu comprobar red, servicios, `gh auth status -h github.com`, `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`, `sudo apt update` y `sudo dpkg --audit`. No repetir instalador.
- Issue #41 permanece abierta únicamente por snapshot/apagado y confirmación de restauración cuando corresponda. Próximo bloque sustantivo de S01: B1 diseño e IPAM, issue #11, antes de desplegar topologías.
