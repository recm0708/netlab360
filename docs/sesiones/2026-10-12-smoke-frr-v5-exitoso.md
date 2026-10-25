# NETLAB360 — B2-L3: Smoke FRRouting v5 SUPERADO

**Ejecutado:** 2026-10-12 23:57:25, hora de Panamá (UTC−05:00).  
**Máquina:** Ubuntu Desktop 26.04.1 LTS, `netlab360-lab`.  
**Alcance certificado:** arranque de los procesos del plano de control FRR local en **un contenedor aislado**, sin WAN ni adyacencias.

## Evidencia constatada

1. `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`: fast-forward `e458944..afbd7f5`; `bash -n` sin errores, rama `main...origin/main` limpia.
2. Se ejecutó una sola vez `bash scripts/laboratorio/b2-frr-smoke-v5-demonios-verificados.sh --snapshot-confirmado` y el validador IPAM B1 devolvió **`VALIDACIÓN B1: OK`** (3 sedes, 9 VLAN y 2 WAN planificadas; red de gestión fuera del IPAM operativo).
3. Configuraciones `daemons`, `frr.conf`, `vtysh.conf` bajo `/etc/frr` en bind mount temporal: `daemons` UID100/GID101 modo0640 y `frr.conf/vtysh.conf` UID100/GID102 modo0660; `zebra=yes`, `ospfd=yes`.
4. Chequeos dentro de contenedor aislado superados: **`FRR_MOUNT_READABLE: SI`**, **`FRR_CRASHLOG_WRITABLE: SI`**, **`FRR_PID_DIR_WRITABLE: SI`**.
5. Contenedor FRR 10.7.1 `amd64`: **`FRR_DAEMONS_ACTIVOS: SI (zebra, ospfd; intento 1)`**. `vtysh -b` aplicó configuración a mgmtd/zebra/ospfd/staticd/watchfrr y devolvió “No changes found to be committed!” como nota no fatal.
6. `vtysh -c 'show ip ospf'`: **`OSPF Routing Process, Router ID: 10.79.0.254`**, `OSPF_CONTROL_PLANE: OK`. La salida indicó **`Number of areas attached to this router: 0`** y que SPF no se había ejecutado: normal porque este smoke NO crea interfaces WAN ni otros routers.
7. `docker top` confirmó `tini`, `docker-start`, `watchfrr`, `mgmtd`, `zebra`, `ospfd`, `staticd`. `watchfrr` registró conexiones “state -> up” para los cuatro demonios y “all daemons up”.
8. Los logs de zebra incluyeron avisos “Extended Error: failed to retrieve link settings”, “generic-netlink ... Not supported” y “Disabling MPLS support”: el control plane OSPF local funcionó; no atribuir a esos avisos un fallo de WAN ni afirmar capacidad MPLS.
9. **`PRUEBA_SMOKE_FRR_V5: OK`**, **`RESULTADO_SMOKE_FRR_V5=0`**, **`RESULTADO_EJECUCION_FRR_V5=0`**.
10. Postcheck: `sudo docker ps -a` vacío, `sudo ip netns list` vacío; `ens33=192.168.47.40/24`, gateway `192.168.47.2`; `docker`, `ssh`, `open-vm-tools` activos; Git limpio.

**Log original local:** `~/netlab360-bootstrap/evidencias/14-b2-frr-smoke-v5-20261012-235725.log`.  
**Evidencia gráfica tomada según la convención definida:** `B2_10_Arranque_FRR_V5_Verificado.png`, delimitada desde `INICIO CAPTURA B2_10` hasta `FIN CAPTURA B2_10`. PNG aún NO revisado visualmente ni subido al repositorio. Hora de consulta del log 23:57:37 (diferente de la hora del ensayo).

## Alcance y límites

**Hito cerrado: preparación/arranque FRR local y rollback controlado.** El smoke v5 **NO demuestra**:
- Routers `R-HQ` y `R-S1` desplegados y direccionados, ni OSPF área 0 operativa en WAN.
- Vecindades OSPF, anuncios de LAN, selección de rutas, conmutación/restauración o latencia de convergencia.
- VLAN trunks 802.1Q reales, ACL, LACP, servidor dual-NIC, redundancia física/virtual de dispositivos.
- API/dashboard, Prometheus, alertas, prototipo IA, prueba OpenTofu/Ansible de esta topología, exportación OVA.

Los cambios posteriores requieren diseñar y validar `up/status/down` con aislamiento, limpieza, sin alterar `ens33` o VMnet8. Guardar evidencia antes y después. El snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` fue confirmado por el operador.

**Issue principal:** [#42](https://github.com/recm0708/netlab360/issues/42). **Fase:** [#1](https://github.com/recm0708/netlab360/issues/1), abierta.
