# NETLAB360 — REANUDAR AQUÍ (checkpoint operativo)

**Última comprobación del usuario:** **2026-10-13 11:24:09, América/Panamá**.  
**Estado real observado:** **B2-L3 DUAL-WAN y tráfico ICMP bidireccional verificados, topología retirada correctamente.**  
**Fase general:** S01 **ABIERTA, 42% estimado y documentado** — no es nota oficial.  
**Plan del usuario:** debe salir y **apagar VM Ubuntu y Windows a más tardar 12:15 p. m. del 13/10/2026**. **A las 12:00 dejar de iniciar pruebas y comenzar el cierre GitHub/postcheck**. El apagado **NO está confirmado** hasta que el usuario lo ejecute.

> Si una conversación se corta, **leer ESTE archivo primero**, luego `docs/00-estado-y-continuidad.md`, `docs/control/01-avance-s01.md`, issues [#1](https://github.com/recm0708/netlab360/issues/1), [#42](https://github.com/recm0708/netlab360/issues/42), [#12](https://github.com/recm0708/netlab360/issues/12), [#43](https://github.com/recm0708/netlab360/issues/43). Los apartados cronológicos antiguos que dicen “FRR no ejecutado” o “ping pendiente” son históricos y han quedado superados.

## Infraestructura esencial que NO debe modificarse

- Host Windows 11 / VMware Workstation Pro 26.0.1; VM `NETLAB360-Ubuntu-Desktop`, hostname `netlab360-lab`, cuenta Ubuntu `rc-aa-ec`; acceso Windows: `ssh netlab360` con clave Ed25519 y passphrase local.
- Ubuntu Desktop **26.04.1 LTS**, kernel `7.0.0-38-generic`, 8 vCPU, 16 GB RAM, disco 160 GB.
- NIC de administración **`ens33=192.168.47.40/24`, default `192.168.47.2`, VMware VMnet8 NAT**. NO cambiar ens33, default route, NetworkManager, firewall host ni redes existentes Docker.
- Docker 29.9.0, Compose 5.6.0, FRRouting 10.7.1, Python 3.14, OpenTofu 1.13.1, Ansible 2.20.1, Node 24, GitHub CLI autenticado.
- Snapshot VMware **`NETLAB360-BASE-HERRAMIENTAS`** fue confirmado por el usuario. No solicitar ni regenerar el snapshot por costumbre. Nunca publicar tokens GitHub ni `~/.config/gh/hosts.yml`, clave SSH privada u OVA sin sanitizar.
- Git privado [`recm0708/netlab360`](https://github.com/recm0708/netlab360), checkout local `~/proyectos/netlab360`, rama `main`. Tras las actualizaciones remotas actuales, **debe ejecutarse un nuevo `git pull --ff-only` en Ubuntu**; `## main...origin/main` del usuario correspondía al checkout anterior a estos commits de documentación. No declarar sincronización local posterior sin salida.

## Qué quedó confirmado (no repetir salvo necesidad concreta)

1. Base Ubuntu y mantenimiento preventivo 13/10 10:47 OK: `apt update` sin paquetes pendientes, `dpkg --audit` vacío, no reboot-required; docker, ssh, open-vm-tools activos.
2. B1 IPAM `inventario/ipam/topologia-b1.yaml`: validación correcta; 3 sedes, 9 VLAN, 2 WAN previstas; todavía `draft`.
3. B2-L2: VLAN 110 conectividad, aislamiento VLAN 120 y recuperación (log previo).
4. FRRouting v5 en contenedor aislado: `FRR_MOUNT_READABLE: SI`, `FRR_DAEMONS_ACTIVOS: SI`, `OSPF_CONTROL_PLANE: OK`, `RESULTADO_SMOKE_FRR_V5=0`. **No repetir ensayos fallidos v1–v4**.
5. **B2-L3 doble WAN — primer ensayo 13/10 11:03–11:11:** script `scripts/laboratorio/b2-dualwan-ospf.sh` con `up/status/fail/restore/down`. Dos routers Docker `--network none` `nl360-b2-r-hq`/`nl360-b2-r-s1`; WAN primaria `10.78.0.0/30`, costo10, backup `10.78.0.4/30`, costo100; loopbacks `10.79.0.1/.2`, LAN dummy HQ `10.70.10.1/24` y S1 `10.71.10.1/24`. **Dos vecinos OSPF Full por router**, FIB normal `via 10.78.0.2 dev wan-p`, failover `via 10.78.0.6 dev wan-b`, retorno `wan-p`, códigos up/status/fail/restore/down=0. Logs `15-b2-dualwan-*.log`; bitácora `docs/sesiones/2026-10-13-b2-dualwan-ospf-failover-resultado.md`.
6. **B2-L3 tráfico ICMP de LAN — segundo ensayo 13/10 11:22–11:24:** script `scripts/laboratorio/b2-dualwan-ping-lan.sh`:
   - NORMAL, ruta `wan-p` simétrica: 5/5 HQ→S1 + 5/5 S1→HQ, **0% pérdida**.
   - RESPALDO tras `fail`, ruta `wan-b` simétrica: 5/5 + 5/5, **0% pérdida**.
   - RESTAURADA tras `restore`, ruta `wan-p` simétrica: 5/5 + 5/5, **0% pérdida**.
   - **30/30 ICMP** entre **IPs dummy de los routers** en tres estados, *después de estabilizar cada fase*, no tráfico continuo durante instante de falla. `RESULTADO_PING_LAN_normal/respaldo/restaurada=0`. `fail=0`, `restore=0`; `RESULTADO_DOWN=0`, `RESULTADO_B2_LIMPIEZA=0`. `sudo docker ps -a` y `sudo ip netns list` vacíos, `ens33` y GW intactos, servicios activos; Git limpio antes de nuevos commits. Bitácora `docs/sesiones/2026-10-13-b2-lan-icmp-tres-estados-verificado.md`.

**Logs originales LOCALES, no subidos automáticamente a GitHub:**
```text
~/netlab360-bootstrap/evidencias/15-b2-dualwan-precheck-20261013-112221.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-up-20261013-112226.log
~/netlab360-bootstrap/evidencias/16-b2-lan-ping-normal-20261013-112307.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-fail-20261013-112313.log
~/netlab360-bootstrap/evidencias/16-b2-lan-ping-respaldo-20261013-112317.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-restore-20261013-112324.log
~/netlab360-bootstrap/evidencias/16-b2-lan-ping-restaurada-20261013-112346.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-down-20261013-112352.log
```

**Capturas:** el usuario estableció que TODAS las capturas solicitadas se **consideran tomadas salvo aviso contrario**. B2_11 precheck, B2_12 vecinos/rutas Full, B2_13 failover, B2_14 restauración, B2_15 **30/30 ICMP**; no se han recibido los PNG para revisión gráfica ni subido archivos al repo. No solicitar que repita pruebas solo para fotografiar una terminal. Indicar siempre nombre PNG y marcador textual exacto **INICIO CAPTURA** hasta **FIN CAPTURA** con comando de consulta a logs, nunca `clear`.

## Control del proyecto e issues

- S01 **42% técnico ponderado**, frente a 40% previo, por dos puntos nuevos de B2-L3. Desglose `docs/control/01-avance-s01.md`: B0 12/12, B1 8/10, B2-L2 3/10, B2-L3 16/18, LACP 0/10, IaC 1/10, B3 0/15, B4 0/5, documentación 2/5, B5 0/5 = **42/100**. No es % oficial de docente.
- Hasta este corte: **43 issues, 3 cerradas** (#39 IP fija, #40 GitHub CLI, #41 herramientas/snapshot), 40 abiertas. #1 S01 **ABIERTA**, #42 dual-WAN **ABIERTA** pese a subhitos aprobados, #12 alerta/dashboard **ABIERTA**, #43 auditoría PNG **ABIERTA**, #35 documentos finales **ABIERTA**. No cerrar por adelantado.
- Pendiente **prioritario**: medir convergencia y pérdida durante caída con tráfico ICMP continuo/timestamps, y de ser necesario un cliente detrás de cada LAN; después B3 exporter/Prometheus, alarma y dashboard que muestren evento WAN. Otras áreas S01: VLAN trunks/ACL, LACP/dualNIC/redundancia, OpenTofu/Ansible, analítica, informe APA7/bitácora/manual, CI/tag/release, OVA sanitizada e importación/checksum, rúbrica docente.
- El éxito de 30/30 NO acredita cero paquetes perdidos **durante el instante de falla**, pues se hicieron pings después de la conmutación. Tampoco prueba hosts/servidores finales, solo las LAN `dummy` que residen en los routers.
- Estado S01 y futuros cierres deben mantenerse sincronizados en issue #1, #12, #42, #43 y matrices. No incrementar porcentaje solo por editar archivos.

## Pausa y comandos de cierre obligatorio (12:00–12:15, 13/10)

**A las 12:00 parar nuevos ensayos**. Para sincronizar `main` *después* de las actualizaciones del asistente:

```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
sudo docker ps -a
sudo ip netns list
ip -4 -br address show ens33
ip -4 route show default
systemctl is-active docker ssh open-vm-tools
```

Comprobar Git limpio, **ambos hashes idénticos**, docker/netns vacíos, IP/GW correctos, servicios activos. Los logs originales siguen en la VM fuera de Git; si se solicita respaldarlos/subirlos, revisar sensibilidad y agregarlos de modo explícito. **No afirmar apagado ejecutado hasta que el usuario reporte**. Tras verificaciones exitosas:

```bash
sync
sudo systemctl poweroff
```

Esperar VMware **Powered Off** y apagar Windows. Si aparece un contenedor B2, ejecutar exclusivamente `bash scripts/laboratorio/b2-dualwan-ospf.sh down` tras revisar marcador del estado, sin destruir recursos ajenos; no apagar con recursos no identificados. Si quedan problemas, capturar/loguear y detener proceso de apagado para resolver, sin correr experimentos nuevos.

**Preferencias operativas del usuario:** entregar paquetes de 6–10 pasos cuando sea útil, no microconfirmaciones; explicar de qué marca a cuál va cada captura; actualizar GitHub continuamente y preservar checkpoint para cambios de conversación; cada vez que VM arranca, mantenimiento preventivo antes de trabajo; al final apagar ordenadamente.
