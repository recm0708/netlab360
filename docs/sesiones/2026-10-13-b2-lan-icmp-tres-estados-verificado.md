# NETLAB360 — B2-L3: conectividad LAN bidireccional en tres estados WAN (verificada)

**Fecha:** 13 de octubre de 2026, 11:22:21–11:24:09, hora Panamá (UTC−05).  
**Entorno:** `netlab360-lab`, Ubuntu Desktop 26.04.1 LTS, Docker FRRouting 10.7.1.  
**Estado:** **PRUEBA FUNCIONAL EXITOSA Y RECURSOS RETIRADOS.**  
**Issues:** [#42](https://github.com/recm0708/netlab360/issues/42) plano de enrutamiento; [#12](https://github.com/recm0708/netlab360/issues/12) futuro incidente observable; [#43](https://github.com/recm0708/netlab360/issues/43) auditoría posterior de PNG.

## Verificaciones y resultados observados

A las 11:22, `git pull --ff-only origin main` adelantó el checkout local `20cb1f8..0f334dc`; `bash -n` de `scripts/laboratorio/b2-dualwan-ospf.sh` y `scripts/laboratorio/b2-dualwan-ping-lan.sh` terminaron ambos con `0` y `git status` reportó `## main...origin/main`. IPAM B1 aprobado por validador; `precheck` con `RESULTADO_PRECHECK=0`; imagen FRR 10.7.1 amd64 en caché.

El comando `bash scripts/laboratorio/b2-dualwan-ospf.sh up --snapshot-confirmado` (11:22:26) levantó dos contenedores FRR sobre `--network none`, con dos enlaces WAN veth independientes, identificadores loopback, interfaces LAN `dummy` y dos vecinos OSPF `Full/-` por router. `OSPF_DUAL_FULL: SI`, `RESULTADO_UP=0`. `wan-p` fue elegida por menor costo (10 frente a 100).

### Ping comprobado en los tres estados

| Fase | Hora prueba (Panamá) | Rutas simétricas comprobadas | HQ 10.70.10.1 → S1 10.71.10.1 | S1 10.71.10.1 → HQ 10.70.10.1 | Código |
|---|---|---|---|---|---|
| **Normal** | 11:23:07 | `wan-p`: HQ vía `10.78.0.2`, S1 vía `10.78.0.1` | 5 enviados / 5 recibidos, **0% pérdida**, RTT medio 0.038 ms | 5/5, **0% pérdida**, RTT medio 0.032 ms | `RESULTADO_PING_LAN_normal=0` y `RESULTADO_ICMP_NORMAL=0` |
| **Respaldo** | 11:23:17 | `wan-b`: HQ vía `10.78.0.6`, S1 vía `10.78.0.5` | 5/5, **0% pérdida**, RTT medio 0.040 ms | 5/5, **0% pérdida**, RTT medio 0.043 ms | `RESULTADO_PING_LAN_respaldo=0` y `RESULTADO_ICMP_RESPALDO=0` |
| **Restaurada** | 11:23:46 | `wan-p`: HQ vía `10.78.0.2`, S1 vía `10.78.0.1` | 5/5, **0% pérdida**, RTT medio 0.031 ms | 5/5, **0% pérdida**, RTT medio 0.040 ms | `RESULTADO_PING_LAN_restaurada=0` y `RESULTADO_ICMP_RESTAURADA=0` |

**Suma observada:** **30/30** ICMP entregados en seis sondeos de cinco paquetes (dos direcciones × tres estados), una vez que la FIB había convergido a su ruta esperada. Esto **no** significa que haya cero pérdida **durante el evento instantáneo de conmutación**: no se ejecutó un flujo ICMP continuo durante la transición.

### Falla y restauración verificadas

- A las **11:23:13**, `b2-dualwan-ospf.sh fail` bajó solo `wan-p` en R-HQ. `CONMUTACION_WAN_B: OK (sondeo 1)`, `RESULTADO_FAIL=0`. R-HQ aprendió `10.71.10.0/24` con OSPF `[110/110]` vía `10.78.0.6 dev wan-b` y retuvo vecino `Full/-` de respaldo.
- A las **11:23:24**, `restore` subió `wan-p`; `RESTAURACION_WAN_P: OK (sondeo 11)`, `RESULTADO_RESTORE=0`, R-HQ recuperó prefijo `[110/20]` vía `10.78.0.2 dev wan-p` y dos vecinos `Full/-`. Número de sondeo ≠ medición temporal precisa.
- A las **11:23:52**, `down` produjo `RESULTADO_B2_LIMPIEZA=0` y `RESULTADO_DOWN=0`.
- Posvalidación: `docker ps -a` vacío, `ip netns list` vacío; `ens33=192.168.47.40/24`, gateway `192.168.47.2`, `docker`, `ssh`, `open-vm-tools` activos, `git status` limpio **antes de los commits remotos de esta bitácora**.

## Ubicación de las evidencias originales en la VM (no incluidas automáticamente en Git)

- `~/netlab360-bootstrap/evidencias/15-b2-dualwan-precheck-20261013-112221.log`
- `~/netlab360-bootstrap/evidencias/15-b2-dualwan-up-20261013-112226.log`
- `~/netlab360-bootstrap/evidencias/16-b2-lan-ping-normal-20261013-112307.log`
- `~/netlab360-bootstrap/evidencias/15-b2-dualwan-fail-20261013-112313.log`
- `~/netlab360-bootstrap/evidencias/16-b2-lan-ping-respaldo-20261013-112317.log`
- `~/netlab360-bootstrap/evidencias/15-b2-dualwan-restore-20261013-112324.log`
- `~/netlab360-bootstrap/evidencias/16-b2-lan-ping-restaurada-20261013-112346.log`
- `~/netlab360-bootstrap/evidencias/15-b2-dualwan-down-20261013-112352.log`

Se considera **tomada por indicación previa del usuario** la captura consolidada `B2_15_Conectividad_ICMP_DualWAN_Tres_Estados.png`, delimitada `INICIO CAPTURA B2_15` a `FIN CAPTURA B2_15`, hora de **consulta** del log 11:24:09. **Los PNG aún no han sido recibidos para inspección visual ni subidos a GitHub.** La captura B2_15 refiere los tres logs originales, y en ella aparecen 5/5 y código 0 para cada dirección y fase.

## Alcance logrado y límites pendientes

**Completado:** conectividad bidireccional entre **IPs LAN de dos routers**, bajo WAN preferida y respaldo, con OSPF Full, selección FIB, transición y limpieza aislada. Los extremos de los ping son interfaces `dummy` **de los routers**, no estaciones o servidores independientes.

**Pendiente de aceptación integral:** (1) flujos ICMP continuos cruzando la caída para **medir tiempo real de reconvergencia y pérdidas transitorias**; (2) clientes/servicios LAN reales; (3) telemetría y eventos con timestamp, exporter/Prometheus, alarmas y dashboard; (4) LACP, redundancia de equipos y doble NIC, IaC/Ansible, IA, integración y entregables académicos. No declarar S01 ni #12 finalizados.

**Próxima sesión de trabajo:** diseñar instrumentación del evento con retención y regresión sin alterar `ens33`. Si hay margen, completar medición continua de pérdida y decidir cierre técnico de #42; sino priorizar observabilidad #12. Mantener 12:00 inicio de cierre para apagar Ubuntu/Windows a más tardar 12:15 el 13/10.
