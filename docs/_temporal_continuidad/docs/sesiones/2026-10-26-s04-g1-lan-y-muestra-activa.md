# NETLAB360 — S04: G1 completa (WAN/LAN/OSPF) y primer muestreo activo

**Corte local: 26/10/2026, 23:58:53 (America/Panama; 2026-10-27T04:58:53Z).**
**Origen:** salidas reales facilitadas por el operador para los pasos 4.27–4.29. Este documento continúa la [bitácora G1 WAN/OSPF](2026-10-26-s04-wan-ospf-activa.md). La fase 4 permanece abierta: G1 sí quedó validada, G2 tiene únicamente comprobación directa inicial del exporter; Prometheus y NOC aún no se han probado sobre la red desplegada.

## Verificación LAN previa y activación

- El clon Ubuntu sincronizó `main` por fast-forward `d1aa854`→`9197486`; repositorio limpio en el precheck.
- `s02-lan-vlan.py precheck`: 3 sedes/3 switches/9 VLAN/9 hosts esperados, rutas WAN principales disponibles, `S02_WAN_PRINCIPALES_PRELAN=OK`, `S02_LAN_PRECHECK=OK`, `S04_G1_LAN_PRECHECK=OK`.
- `s02-lan-vlan.py up --snapshot-confirmado`: nueve VLAN creadas (HQ 110/120/130, S1 210/220/230, S2 310/320/330), tres bridges `vlan_filtering`, nueve endpoints, `S02_SWITCHES=3 VLAN=9 HOSTS=9`, `S02_LAN_UP=OK`, gestión intacta.
- `validar-lan-s02.py`: las nueve pasarelas respondieron `9/9`, comunicaciones entre VLAN/sedes `6/6`, `S02_LAN_VALIDADA=OK`.
- `s02-lan-vlan.py status`: VLAN etiquetadas en `tr-sw`, hosts con direcciones correctas, `trunk0.<VID>` UP en routers, interfaces WAN primarias/respaldo aún UP; `S02_LAN_ESTADO=OK`.
- `ens33` quedó `192.168.47.40/24` y ruta predeterminada `192.168.47.2`; `S04_G1_LAN_VALIDADA=OK`.

## G2 — Observación inicial de topología activa

- `python3 servicios/observabilidad/s04_exporter_multisede.py --check`: `S04_PREFLIGHT=OK` y SoT `candidate` de 3 routers, 4 WAN, 9 VLAN.
- `--once`: `errors=[]`, `source_ok=true`, `topology=active`; routers R-HQ/R-S1/R-S2 todos `1`. Los ocho extremos WAN y nueve `trunk0.<VID>` observados con `admin_up=1` (17 interfaces declaradas). Resultado `S04_RESULTADO_OBSERVACION=OK` y `S04 MUESTRA_COMPLETADA=OK`.
- Semántica obligatoria: `topology=active` certifica los tres contenedores, `admin_up=1` certifica banderas administrativas. El OSPF FULL 4/2/2, FIB 6/6 e ICMP de G1 se acreditaron separadamente. Este muestreo **no** prueba scrape Prometheus actual ni visualización NOC viva.

## Estado actual y siguiente operación

- **G1 COMPLETA:** 3 routers FRR, 4 WAN, OSPF FULL 4/2/2, FIB 6/6, 3 switches, 9 VLAN/9 hosts, gateways 9/9, ICMP LAN 6/6, sin modificar ens33.
- **G2 PARCIAL:** `--once` del exporter validado; aún falta `--serve` 9110, Prometheus 9091 y NOC 9120, métricas frescas y screenshots nuevos S04_07–S04_09.
- **G3–G6 PENDIENTES:** falla controlada, alerta `pending/firing/resolved` con recuperación y rutas, fuente/histórico, SLI/SLO y decisión de notificación, postcheck/registro e informe académico.
- **No desmontar**: mantener routers, WAN, LAN y states activos para ensayos G2/G3. No usar `docker compose down`, `wan-links.py down`, `lan-vlan.py down` ni `tofu apply` durante observabilidad.
- S01, S03 y S04 se administran por criterios propios. Puede avanzarse S04→S08 dejando pendientes legítimos de S01/S03 o elementos de integración transversal; revisar periódicamente sin atribuir porcentajes automáticos. S01 72 % **histórico** y S03 ~90 % permanecen vigentes hasta contar con criterios concretos aprobados. No exigir cerrar S01/S03 para iniciar S05.

**Capturas:** no se han comunicado PNG adicionales en este corte; el repositorio sigue con 114 PNG totales, siete de S04. Reservados S04_07–S04_09 para verificación sobre topología activa.
