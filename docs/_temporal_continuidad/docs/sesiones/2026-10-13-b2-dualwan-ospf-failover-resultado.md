# B2-L3 — R-HQ ↔ R-S1 con OSPF dual-WAN: despliegue, failover, restauración y rollback VERIFICADOS

**Fecha de ejecución:** 2026-10-13, 11:03–11:11 Panamá (UTC−05:00).  
**Entorno:** `netlab360-lab`, Ubuntu Desktop 26.04.1 LTS en VMware; administración `ens33=192.168.47.40/24`, default `192.168.47.2`.  
**Resultado:** **ENRUTAMIENTO OSPF Y CONMUTACIÓN PROBADOS CON ÉXITO.** La prueba se completó sin residuos; fase S01 e issue #12 siguen abiertas por falta de observabilidad y validaciones integradas adicionales.

## Línea temporal y salidas observadas

| Hora Panamá | Acción | Evidencia observada |
|---|---|---|
| 10:57:32 | precheck previo | `RESULTADO_B2_DUALWAN_PRECHECK=0`; sin contenedores ni namespaces |
| 11:03:57 | `up --snapshot-confirmado` | `RESULTADO_DESPLIEGUE=0`, `OSPF_DUAL_FULL: SI`; esperó hasta intento 8 para detectar dos vecinos Full |
| 11:08:49 | `status` | `RESULTADO_STATUS=0`; enlaces `wan-p` y `wan-b` UP, dos vecinos `Full/-` por router; LAN dummy y loopbacks |
| 11:09:30–11:09:31 | `fail` | Validó ruta inicial `dev wan-p`; bajó WAN-P exclusivamente en R-HQ y comprobó ruta remota vía `10.78.0.6 dev wan-b`, `CONMUTACION_WAN_B: OK (sondeo 1)`, `RESULTADO_FAILOVER=0` |
| 11:10:11 | `restore` | Subió WAN-P; ruta remota vuelve vía `10.78.0.2 dev wan-p`, `RESTAURACION_WAN_P: OK (sondeo 11)`, `RESULTADO_RESTAURACION=0` |
| 11:11:08 | `down` | `RESULTADO_B2_LIMPIEZA=0`, `RESULTADO_DOWN=0`; Docker vacío, netns vacío, IP/ruta host intactas, servicios activos, Git limpio |

## Topología efectiva durante el ensayo

- Contenedores Docker `nl360-b2-r-hq`, `nl360-b2-r-s1` sobre `--network none`.
- WAN principal R-HQ `10.78.0.1/30` ↔ R-S1 `10.78.0.2/30`, OSPF área 0 y costo por interfaz 10.
- WAN respaldo R-HQ `10.78.0.5/30` ↔ R-S1 `10.78.0.6/30`, OSPF costo 100.
- Loopbacks `10.79.0.1/32` y `10.79.0.2/32`.
- LAN simuladas **dummy** `10.70.10.1/24` (HQ) y `10.71.10.1/24` (S1); **no hay todavía hosts finales ni servicios de aplicación detrás de las LAN**.

**Vecindades OSPF comprobadas en ambos routers:**
```text
R-HQ -> 10.79.0.2 Full/- por wan-p y wan-b
R-S1 -> 10.79.0.1 Full/- por wan-p y wan-b
```

**Ruta OSPF observada desde HQ antes del fallo:**
```text
O>* 10.71.10.0/24 [110/20] via 10.78.0.2, wan-p
O>* 10.79.0.2/32 [110/10] via 10.78.0.2, wan-p
```

**Durante la caída WAN principal:**
```text
WAN_PRIMARIA: DOWN
RUTA_RESPALDO: 10.71.10.1 via 10.78.0.6 dev wan-b src 10.78.0.5
CONMUTACION_WAN_B: OK (sondeo 1)
O>* 10.71.10.0/24 [110/110] via 10.78.0.6, wan-b
```

**Durante restauración:**
```text
WAN_PRIMARIA: UP
RUTA_PRINCIPAL: 10.71.10.1 via 10.78.0.2 dev wan-p src 10.78.0.1
RESTAURACION_WAN_P: OK (sondeo 11)
O>* 10.71.10.0/24 [110/20] via 10.78.0.2, wan-p
```

El **sondeo 1** de conmutación y el **sondeo 11** de retorno no constituyen una medición precisa de tiempo de convergencia ni de pérdida de paquetes; el script no guardó una serie temporal de pings continuos. Se comprobó instalación de ruta FIB mediante `ip route get` y las rutas de FRR, pero **todavía no se demostró comunicación de datos con paquetes ICMP ni entrega de servicios sobre las LAN**. Evitar declarar esas verificaciones como completas.

## Logs originales locales

- `~/netlab360-bootstrap/evidencias/15-b2-dualwan-up-20261013-110357.log`
- `~/netlab360-bootstrap/evidencias/15-b2-dualwan-status-20261013-110849.log`
- `~/netlab360-bootstrap/evidencias/15-b2-dualwan-fail-20261013-110930.log`
- `~/netlab360-bootstrap/evidencias/15-b2-dualwan-restore-20261013-111011.log`
- `~/netlab360-bootstrap/evidencias/15-b2-dualwan-down-20261013-111108.log`

**Capturas tomadas según protocolo del usuario (aún no revisadas visualmente ni subidas al repositorio):** `B2_12_Vecinos_y_Rutas_OSPF_DualWAN.png`, `B2_13_Failover_WAN_Principal_a_Respaldo.png`, `B2_14_Restauracion_WAN_Principal.png`. Registrar en issue #43 para inspección del lote.

## Estado posterior y pendientes

- Docker `ps -a` vacío; `sudo ip netns list` vacío; `ens33 UP 192.168.47.40/24`, default `.2`, servicios `docker/ssh/open-vm-tools` activos, Git limpio.
- **Subhito de routing/alta-baja y recuperación concluido.** Próxima prueba específica: **conectividad real ICMP con origen de LAN/loopback**, antes/durante/después del corte, y medición con timestamps/pérdida/convergencia. Debe ejecutarse en sesión nueva solo si hay margen y rollback.
- Pendientes mayores: clientes reales LAN, redundancia de equipo, LACP/trunks/ACL, telemetría/exporter/Prometheus, eventos/alarma y dashboard, OpenTofu/Ansible aplicados, anomalías y documentos/release/OVA. Issue #42 queda ABIERTA por criterios adicionales; #12 ABIERTA por incidente aún no observable en dashboard.
- El usuario solicitó cierre de sesión a las 12:00 para sincronizar GitHub y **apagar todo antes de las 12:15**, hora de Panamá.
