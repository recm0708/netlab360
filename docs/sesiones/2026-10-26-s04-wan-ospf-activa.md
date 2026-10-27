# NETLAB360 — S04: infraestructura WAN/OSPF activa y comprobada

**Registro de ejecución: 26/10/2026, aproximadamente 23:48 (America/Panama).** Evidencia: salida real de tres bloques ejecutados por el operador en la VM `netlab360-lab`. Este registro actualiza exclusivamente el progreso de la fase 4; no sustituye ni reabre las pruebas finales de S02.

## Sincronización y acceso comprobados

- Git: cambio seguro de `feat/s04-evidencias-lote01` a `main`, `git pull --ff-only origin main`; `d1aa854` y árbol limpio al momento de la ejecución. Siete PNG S04 en `main`, `S04_GIT_SINCRONIZADO=OK`.
- Desde una segunda PowerShell de Windows, se accedió por SSH a `rc-aa-ec@192.168.47.40`. Hubo un intento de contraseña rechazado y luego autenticación correcta. Esto comprueba continuidad de acceso, **no** un endurecimiento de SSH (pendiente #38).
- El operador había confirmado previamente una instantánea VMware S04. Se usó el indicador `--snapshot-confirmado` para la activación de WAN; no se ha probado restauración desde dicha instantánea.

## Routers FRR y WAN desplegados

- Precheck S02: `S02_PRECHECK_RESULTADO=0`, runtime validado para R-HQ, R-S1 y R-S2.
- Inicio: contenedores `nl360-s02-r-hq`, `nl360-s02-r-s1`, `nl360-s02-r-s2`, todos `Running` con red Docker `none`. `S02_RESULTADO_ARRANQUE=0`, `S04_ROUTERS_ACTIVOS=3`, `S04_G1_ROUTER=OK`.
- Precheck WAN: `S02_WAN_PRECHECK=OK`. Cuatro enlaces desplegados en namespaces FRR aislados: primario/respaldo HQ–S1 (`s1p/s1b`) y HQ–S2 (`s2p/s2b`). Tres loopbacks configuradas: 10.79.0.1/32 (HQ), .2/32 (S1) y .3/32 (S2).
- Resultado despliegue `S02_WAN_LINKS_UP=4`, `S02_WAN_UP=OK`, `S02_HOST_GESTION_INTACTO=SI`.

## Comprobaciones operativas (G1 — WAN)

| Criterio | Resultado real |
|---|---|
| OSPF HQ | `S02_OSPF_FULL_HQ=4` |
| OSPF S1 | `S02_OSPF_FULL_S1=2` |
| OSPF S2 | `S02_OSPF_FULL_S2=2` |
| Preferencia de rutas primarias | `S02_FIB_WAN_PRIMARIA=6/6` |
| Ping entre loopbacks | 6/6 OK, `S02_OSPF_Y_CONECTIVIDAD=VALIDADOS` |
| Espera del validador | `S02_OSPF_ESPERA_INTENTOS=8` |
| Host Ubuntu | `ens33=192.168.47.40/24`, puerta de enlace `192.168.47.2` sin cambios |
| Cierre del bloque | `S04_G1_WAN_OSPF=OK` |

**Interpretación:** cuatro WAN y adyacencias OSPF **operativas de verdad**; todavía no están validadas las nueve VLAN dentro de este nuevo despliegue. No atribuir todavía estados activos del exporter, alertas o NOC a esta operación. La fase 4 permanece abierta.

## Continuidad exacta

1. Mantener encendidos los tres routers FRR y los cuatro enlaces WAN. No desmontar WAN ni ejecutar `docker compose down` antes de las pruebas LAN/observabilidad.
2. `sudo -v`; `python3 scripts/laboratorio/s02-lan-vlan.py precheck`; con snapshot VMware previamente confirmado, `python3 scripts/laboratorio/s02-lan-vlan.py up --snapshot-confirmado`; `python3 scripts/validacion/validar-lan-s02.py`; `python3 scripts/laboratorio/s02-lan-vlan.py status`. Detener secuencia ante cualquier fallo, conservando state y salida.
3. Validar 9/9 gateways, 6/6 ICMP inter-VLAN/intersede y la administración `ens33` sin cambios. Esto completa G1 solo cuando esté respaldado con resultados reales.
4. Reutilizar exporter S04 9110, Prometheus 9091 y NOC 9120 en ese orden; comprobar métricas frescas y recopilar S04_07–S04_09. La conmutación/falla y resolución serán pruebas posteriores controladas G3.
5. **Sin alteración de porcentajes históricos:** S01 sigue en 72 % de la matriz antigua (pendiente #38 y compatibilidad #34), S03 en ~90 % hasta formalizar SoT #16 y OpenTofu externo/ownership #17. No declarar ninguna como cerrada por el funcionamiento de S04.

**Referencias:** [matriz S04](../operaciones/s04-cierre-observabilidad-multisede.md), [issue #4](https://github.com/recm0708/netlab360/issues/4), [tablero](../control/06-tablero-porcentajes-cierre-fases-2026-10-25.md).
