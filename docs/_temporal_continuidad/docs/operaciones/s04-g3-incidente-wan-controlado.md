# NETLAB360 — G3: observación de incidente WAN primario S1 y recuperación

**Estado:** procedimiento preparado, **NO ejecutado todavía**. La aceptación G3 dependerá exclusivamente de salidas reales en Ubuntu y capturas. Fecha de preparación: 27/10/2026.

## Contexto comprobado

- G0/G1: cerradas internamente; tres FRR, cuatro WAN, nueve VLAN, OSPF Full 4/2/2, FIB 6/6, 9/9 gateways y 6/6 ICMP LAN.
- G2: exporter 9110, Prometheus 9091, NOC 9120 probaron APIs en topología activa. El operador confirmó **S04_07, S04_08 y S04_09 tomadas**, pero **PNG aún no auditadas ni publicadas**. No modificar conteo remoto de 114 PNG.
- Regla de Prometheus `NETLAB360S04WANAdminDown`: `for: 6s`, evaluación/scrape cada 2 s; el script S02 original puede restaurar demasiado rápido para registrar `firing`.

## Control de seguridad y alcance

- Nuevo script `scripts/observabilidad/s04-incidente-wan.py`, con dos modalidades: `--check` solo lectura y `--execute --snapshot-confirmado` con corte real de **únicamente la interfaz HQ/s1p dentro del namespace del router FRR**.
- Reutiliza `validate_ownership`, `ns`, `route`, `ping`, `wait_fib` y `host_guard` del `s02-failover-wan.py`; verifica tres contenedores propiedad del laboratorio, `network_mode=none`, state externo WAN S02 y gestiona acceso privilegiado mediante `sudo -n`.
- `--check` exige fuente fresca, 3/3 routers, WAN 8/8, VLAN 9/9, Prometheus scrape UP, NOC disponible, alerta basal ausente, rutas primarias HQ→S1 y S1→HQ por `s1p`, HQ→S2 por `s2p`.
- `--execute --snapshot-confirmado` solo tras confirmar el precheck y snapshot vigente en VMware; sostiene `HQ/s1p DOWN` 32 segundos (admite 20–60 s, predeterminado 32), registra transiciones `pending`/`firing`, corrobora que el NOC exhiba `firing`, verifica respaldo HQ/S1 por `s1b`, estabilidad S2 por `s2p` e ICMP en corte.
- `finally` restituye `HQ/s1p UP` aunque se produzca excepción o Ctrl+C/SIGTERM/SIGHUP; verifica regreso FIB principal, ICMP, red administrativa intacta, fuente y serie recuperadas, alerta desaparecida de las **alertas activas** de Prometheus.
- **No afirmar alerta `resolved` como evento externo o notificación Alertmanager**: la API `/api/v1/alerts` solo muestra activas; tras haber visto `firing`, la ausencia con fuente fresca y `admin_up=1` fundamenta el estado resuelto local. No prueba disponibilidad HTTP real ni tiempos de convergencia externos.

## Secuencia protegida

1. Mantener los tres procesos activos: Term2 exporter 9110, Term3 Prometheus 9091 y Term4 NOC 9120. Term1 se usa para SSH interactivo/validaciones y el túnel hacia navegador Windows.
2. En Term1: `git pull --ff-only origin main`, árbol limpio, `python3 -m py_compile scripts/observabilidad/s04-incidente-wan.py`, `python3 -m unittest discover -s tests -p 'test_s04_incidente_wan.py' -v`, `sudo -v` y `python3 scripts/observabilidad/s04-incidente-wan.py --check`. Requiere `S04_G3_PRECHECK=OK` sin excepción.
3. Solo tras revisar la salida, preparar NOC en navegador y confirmar el snapshot S04. Ejecutar en Term1 `python3 -u scripts/observabilidad/s04-incidente-wan.py --execute --snapshot-confirmado`.
4. Captura `S04_10_Incidente_WAN_Principal_Alerta_Firing` **obligatoria**: en la ventana de 32 s, ver NOC/Prometheus con `NETLAB360S04WANAdminDown` `firing` y enlace HQ/s1p DOWN; conservar salida terminal `S04_G3_ALERTA_TRANSICION` y `S04_G3_RUTA_RESPALDO_HQ` en la bitácora.
5. Captura `S04_11_Recuperacion_WAN_Alerta_Resuelta` **obligatoria**: después del retorno confirmado, NOC sin alerta, HQ/s1p UP; terminal desde `S04_G3_HQ_s1p=UP_RESTAURADA` hasta `S04_G3_RESULTADO=OK` cuando corresponda.
6. **No repetir la falla** si no aparece `firing` sin diagnosticar primero las marcas temporales, source/exporter, reglas y FIB. Si el test acaba sin OK, preservar estado y comprobar que `s1p` quedó UP mediante herramienta S02; no forzar nueva caída.
7. G4–G6 posterior: histórico/TSDB, SLI/SLO/decisión de notificación, regresiones y escrito capítulos 5–8. La topología continúa activa salvo desmontaje controlado posterior.

## Estados de evidencia

La declaración del operador sobre S04_07–09 constituye **captura realizada**; requiere revisión real de los PNG y publicación por PR. Las capturas G3_10/11 son **planeadas**, no ejecutadas. Nunca inventar timestamps, duración de corte, estado de alerta o muestras de Prometheus.

## Pruebas unitarias

`tests/test_s04_incidente_wan.py` verifica filtrado por interfaz y sede, ausencia y duplicación de alertas, rechazo de URL ajenas y ejecución simulada donde el corte falla pero la rutina `finally` solicita restauración. Estas pruebas offline no reemplazan el ensayo G3 en Ubuntu.
