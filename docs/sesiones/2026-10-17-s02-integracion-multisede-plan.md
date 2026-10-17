# NETLAB360 — S02: inicio y plan de integración multisede (17/10/2026)

**Estado:** diseño candidato y preflight pendiente; **NO se ha desplegado topología S02 ni modificado la VM por este registro**. La máquina Ubuntu fue encendida por el usuario y `git pull --ff-only origin main` se completó correctamente sobre commit `94339de` sin cambios locales visibles al cierre de esa operación.

## Confirmación académica relevante
- El estudiante confirmó que envió a Teams el título **«Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede»**. **Aprobación docente pendiente**, issue #46.
- Revisión 30/10: Introducción, Objetivos y Planteamiento del problema; 13/11 Fundamento técnico y Diseño. Se muestra el Word en Teams por representante; no PPT de corte.
- Demostración final EN VIVO con datos reales; ZIP externo de anexos autorizado, manual técnico posentrega.
- No guardar aquí archivos de clase/guías o transcripciones.

## Observaciones técnicas de S01 (comprobadas, NO S02)
- Archivo `inventario/ipam/topologia-b1.yaml` sigue `status: draft`, tres sedes en inventario pero **HQ y S1 proposed, S2 reserved**.
- Validador `scripts/validacion/validar-ipam.py` obliga que S2 permanezca `reserved`, por compatibilidad con IPAM B1 original. **No modificar silenciosamente el validador ni reescribir el inventario histórico**: para S02 introducir una revisión/nuevo esquema y prueba correspondiente.
- B2 VLAN/ACL de HQ y FRRouting/OSPF WAN HQ–S1 han sido validados **en ensayos diferentes**. El HTTP WAN previo utiliza interfaces veth P2P y rutas /32, no la misma troncal 802.1Q.
- Dos WAN existentes HQ–S1: `10.78.0.0/30` (cost 10), `10.78.0.4/30` (cost 100).
- VM gestión protegida: `ens33 192.168.47.40/24`, puerta de enlace `192.168.47.2`. No tocar IP del anfitrión, routing host, NetworkManager, nftables host ni VMnet8.

## Topología CANDIDATA S02 — sujeta a precheck y acuerdo antes de activar

- Tres routers FRRouting: `R-HQ`, `R-S1`, `R-S2`, ejecutados en contenedores con red NONE, no en `--network host`.
- VLAN por sede de IPAM B1 (HQ 110/120/130, S1 210/220/230, S2 310/320/330) con switches Linux/bridge VLAN aware y enlaces trunk 802.1Q hacia subinterfaces del router.
- Rutas WAN con **dos enlaces entre HQ y S1** ya contemplados: principal `10.78.0.0/30`, respaldo `10.78.0.4/30`.
- **Propuesta adicional, todavía NO asignada:** HQ↔S2 WAN principal `10.78.0.8/30`, extremos HQ `10.78.0.9` / S2 `10.78.0.10`, costo OSPF 10; WAN respaldo `10.78.0.12/30`, extremos HQ `10.78.0.13` / S2 `10.78.0.14`, costo 100.
- Loopbacks existentes `10.79.0.1/32`, `10.79.0.2/32`, `10.79.0.3/32`. S1↔S2 inicialmente vía HQ (hub-and-spoke); **redundancia de router HQ NO queda cubierta**. Enlaces S1-S2/equipo alterno quedan para decisión posterior tras pruebas/recursos.
- Clientes y servidores representativos en VLAN reales en cada sede. Flujo mínimo `HQ VLAN110 -> S1 VLAN220 -> servicio HTTP` y `HQ VLAN110 -> S2 VLAN320 -> servicio HTTP` con ACL positiva/negativa, WAN-P→WAN-B→restauración.
- Las redes 10.78.0.8/30 y 10.78.0.12/30 son **reservas propuestas, NO verificadas contra rutas host/Docker/VPN**, y no aparecen todavía en IPAM B1.

## Etapas técnicas antes de despliegue

1. **PRECHECK solo lectura**: hostname, fecha, estado Git, ens33/gateway, servicios, Docker/netns, rutas IPv4 host, memoria/disco y subredes Docker/VPN.
2. **Revisar compatibilidad**: validar IPAM B1 `scripts/validacion/validar-ipam.py`; correr `bash scripts/diagnostico/precheck-b1.sh`, que escribe log en `~/netlab360-bootstrap/evidencias` pero no modifica redes/contendedores. **No ejecutar** scripts de laboratorio con `up`, `fail` o `down` en este paso.
3. **Diseñar S02** sin sobrescribir S01: nuevo inventario `topologia-s02.yaml`, validador S02 y scripts `s02-*` que validan prefijos, propiedad de recursos, snapshots y rollback.
4. Validación estática de IPAM actualizado; comprobar explícitamente colisiones con rutas y Docker reales.
5. Desplegar topología de forma controlada SOLO con precheck limpio y rollback, proteger `ens33`, mantener sesión SSH y acceso a consola VMware.
6. Evidenciar **baseline→falla→esperado vs. observado→recuperación→postcheck** con nombres de capturas por prueba; registrar logs y SHA256 de capturas reales.
7. Actualizar Informe ÚNICO (7 Implementación, 8 Pruebas, 9 Análisis) y issues técnicas. No cerrar S01/S02 ni afirmar integración S2 antes de éxito medido.

**Próximo paso exacto del usuario:** ejecutar la tanda de precheck (sin despliegue ni cambios de red) y remitir los resultados. Se decidirá entonces la asignación definitiva de nuevos enlaces y el diseño del script S02.


## Actualizacion de comprobaciones recibidas — 17/10/2026, 15:31 -05

El usuario ejecuto precheck por SSH, compartio salidas de terminal y confirmo captura `S02_01_Precheck_Inicial_Integracion_Multisede`.

- `git pull --ff-only`: commit `527ca35`, limpio `main...origin/main` al momento de la prueba.
- `ens33=192.168.47.40/24`; default via `192.168.47.2`; Docker 0 contenedores; 0 namespaces; docker/ssh/open-vm-tools activos; `systemctl --failed` 0.
- Recursos 15 GiB totales / ~13 GiB disponibles, disco ~135 GB disponible.
- `RESULTADO_PRECHECK_S02=0`, validador B1 `RESULTADO_IPAM=0`, sintaxis Bash `RESULTADO_SINTAXIS_LABS=0`, FRR imagen local `quay.io/frrouting/frr:10.7.1` amd64.
- Se intento una comprobacion manual de colisiones WAN S2, pero **fallo su propio codigo** con `TypeError: 'NoneType' object is not iterable` al recorrer `Docker IPAM.Config=null` para redes sin prefijos. **Esta comprobacion NO permite declarar aun libres las subredes S2**. La captura S02_01 es valida como precheck B1, **no acredita colisiones S02**.
- Se creo `inventario/ipam/topologia-s02.yaml` (candidato, esquema 0.2), `scripts/validacion/validar-ipam-s02.py` y `tests/test_s02_ipam.py` para corregir el manejo `null`, proteger VMnet8 y validar solapamientos de S02 con rutas Ubuntu/Docker. **No desplegado y sin resultados de ejecucion sobre Ubuntu en esta etapa**.
- **Proxima verificacion del usuario**: pull, compilacion Python, tests unitarios, validacion estatica y live del IPAM candidato; revisar rutas IPv4 Windows/VMware/VPN antes de aprobar los dos /30 de HQ-S2.

**Estado:** S02_01 CAPTURADA y precheck B1=OK; IPAM candidato S02 CREADO pero VALIDACION LIVE PENDIENTE. No se marcaran redes como activas ni se capturara evidencia falsamente exitosa.


## Segundo corte de evidencia S02_02 — 17/10/2026 15:38:58 -05

El usuario confirmo captura `S02_02_Validacion_IPAM_Tres_Sedes_Cuatro_WAN`; la captura fisica PNG aun NO se ha incorporado a GitHub. **Evidencia de terminal aceptada como predespliegue**:

- Ubuntu `git pull --ff-only` => `0f25aa9` limpio `main...origin/main`.
- `python3 -m py_compile` S02 y test => salida 0; `python3 -m unittest ... test_s02_ipam.py` => **4/4 OK**.
- B1 intacto `VALIDACION B1: OK`; S02 `S02_IPAM_ESTATICO=OK`, sedes 3, VLAN 9, WAN 4, redes 17 **incluyendo VMnet8**, sin solapamientos internos.
- `S02_REDES_HOST_DOCKER_REVISADAS=10`, `S02_COLISIONES_HOST_DOCKER=0`, `S02_VALIDACION_LIVE_UBUNTU=OK`, `RESULTADO_COLISIONES_S02=0`.
- Estado tras prueba: red ens33 `192.168.47.40/24`, GW `192.168.47.2`, Docker sin contenedores, netns vacios y Git limpio.
- Windows PowerShell `Get-NetRoute -AddressFamily IPv4`: las rutas activas informadas (`10.20.30.0/26`, `172.16.20.0/24`, `192.168.10.0/24`, `192.168.47.0/24`, `192.168.1.0/24`, `192.168.2.0/24`, mas rutas host) **NO incluyen solapamientos con 10.70–10.72, 10.78.0.0/28 ni 10.79.0.0/32**. La comprobacion aplica a rutas ACTIVAS del momento, no VPN futuras ni rutas fuera de Windows.
- Capturas `S02_01` y `S02_02` declaradas tomadas por el usuario pero aun NO auditadas como archivos PNG ni publicadas: no contar en el inventario GitHub de evidencias.
- No se ha creado ningun dispositivo S02 real: `S02_DESPLIEGUE_EJECUTADO=NO`.

## Preparacion predespliegue posterior a validacion

Archivos añadidos al repositorio: `scripts/automatizacion/render-frr-s02.py` y `tests/test_s02_render_frr.py`. El render genera tres archivos FRR desde el inventario candidato sin interfaces ni Docker. **Antes de ejecutar topologia integrada: pruebas unitarias/compilacion, salida de 3 configs y comprobacion de costos/interfaces y snapshot VMware actualizado confirmado**.

**No confundir** el éxito de IPAM con vecinos OSPF ni con conectividad inter-VLAN/WAN. La construccion y sus fallas controladas siguen pendientes.


## Tercer corte — render y predespliegue 17/10/2026 16:08 -05

**COMPROBADO POR SALIDAS DE USUARIO:** commit local `6db0fab` sincronizado; Python compila sin errores; cuatro tests de `test_s02_render_frr.py` `OK`; generador FRR produce R-HQ `1037` bytes, R-S1 `758`, R-S2 `758` en `~/netlab360-bootstrap/s02/rendered` (archivos candidatos, no red viva). Hashes SHA256: HQ `8fcc1e756c7ad026a5dfdbdf9fc0b65ec8841e9de494fe0fe543383ba2b2ac36`, S1 `345eb21fdf66c16b82c2e3b294b5c278553232907606468a02b776f8f82ad036`, S2 `7bfb8be5d642b9c52bc628af24eb238b7b445dfc0aa3ea898badfec484f4e917`. Auditoría estática: HQ 3 VLAN y 4 WAN, S1/S2 3 VLAN y 2 WAN cada una; costos OSPF principal 10/respaldo 100 verificados. S02 IPAM en Ubuntu sigue 3 sedes/9 VLAN/4 WAN/17 redes y cero solapamientos con rutas Ubuntu y Docker. `ens33=192.168.47.40/24`, gateway `.2`, cero contenedores/netns, Git limpio. **El usuario confirmó creación de instantánea VMware**; nombre y opciones no observados directamente.

**ATENCIÓN antes de redes reales:** `systemctl is-active docker ssh open-vm-tools` devolvió `active\ninactive\nactive` en 16:08, pese a sesión SSH preexistente funcional. Puede ser `ssh.socket` activo con `ssh.service` inactivo por systemd socket activation; **se debe probar, no asumir**. Primero consultar ssh.service/ssh.socket/listener/sshd -t y abrir segunda conexión nueva desde PowerShell manteniendo la actual abierta. No desplegar/ejecutar `up` hasta confirmar disponibilidad de acceso o recuperación vía consola VMware. **PasswordAuthentication yes** era pendiente histórico; no endurecerlo durante pruebas de integración.

**Próxima evidencia:** `S02_03_Configuraciones_FRR_Tres_Sedes_Candidatas` (salida compacta de hash/OSPF/VLAN/generador), únicamente al validar acceso SSH y resultado del precheck. Captura física no presente en repo.

 
## Cuarto corte — 17/10/2026 16:31 -05: SSH y precheck operativos

**Verificado mediante salidas aportadas:**
- `ssh.service=active` y `ssh.socket=active`. `/run/sshd` existe con propietario root:root y modo 0755; `ssh.service` declara `RuntimeDirectory=sshd` y `RuntimeDirectoryMode=0755`.
- `sudo /usr/sbin/sshd -t` terminó `0`.
- **SEGUNDA conexión SSH desde Windows** con clave Ed25519 completada: `SEGUNDA_CONEXION_SSH=OK` y `RESULTADO_SEGUNDA_CONEXION=0`.
- `bash -n scripts/diagnostico/precheck-s02.sh` terminó `0`, `python3 scripts/validacion/validar-ipam-s02.py` terminó `0`.
- `bash scripts/diagnostico/precheck-s02.sh` terminó `S02_PRECHECK_RESULTADO=0`. Gestión `ens33=192.168.47.40/24`, GW `.2`, imagen FRR 10.7.1 amd64 presente, 3 configuraciones con hashes esperados, IPAM 3 sedes/9 VLAN/4 WAN, colisiones 0 y Docker/netns vacíos.
- Captura `S02_04_Precheck_Seguridad_y_FRR_Multisede` respaldada por salida completa del usuario; **no se ha recibido archivo PNG ni publicado en Git**.
- En el momento del chequeo Git Ubuntu estaba limpio en `95e0848`. Esta documentación de GitHub se ha actualizado después.
- El bloqueo de disponibilidad de SSH se considera **resuelto para esta sesión**. La política de autenticación por contraseña/endurecimiento permanece pendiente en #38.
- **Despliegue de WAN S02 NO ejecutado.** El intento de publicar un orquestador nuevo en GitHub fue bloqueado por la herramienta; **NO hay un archivo `scripts/laboratorio/s02-wan-frr-multisede.sh` validado/publicado** y no debe invocarse `up`. Mantener S02 como `candidate`.
- **Próxima actividad:** verificación de garantías de rollback y capacidades del host; después implementar el orquestador mediante un método revisable, someterlo a `bash -n`, pruebas por etapa y aprobación expresa del operador antes del primer despliegue. Nunca modificar `ens33`, `VMnet8` ni borrar recursos ajenos.
