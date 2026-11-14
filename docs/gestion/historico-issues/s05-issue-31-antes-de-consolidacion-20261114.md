# Archivo histórico de issue #31

**Fecha de corte:** 2026-11-14 (Panamá). **Origen:** https://github.com/recm0708/netlab360/issues/31

**Título original:** [023] LACP 802.3ad: multistream piloto medido; capacidad e integración pendientes

**Estado al archivar:** open

**Propósito:** preservar el texto íntegro previo a la normalización del tablero S05. Este archivo es histórico; NO usar las tareas antiguas como lista vigente. Consultar el issue original o `docs/gestion/s05-tablero-vigente.md` para el estado actual.

---

# Agregación LACP y capacidad — fase 5

## Línea base demostrada (fase 1)
- [x] Bonds IEEE 802.3ad negociados en extremos virtuales, con dos miembros activos.
- [x] Caída y recuperación de un miembro LACP, estado **2→1→2** observado.
- [x] HTTP preservado durante conmutación/recuperación; postcheck de host y capturas S01 conservados.

## Control de aceptación del alcance avanzado
- [x] Ejecutar **piloto reproducible multistream limitado**: 1 flujo y 8 flujos, distribución observada de miembros, 2→1→2 en servicio, registro JSON/manifest SHA-256 local y postcheck de red/limpieza.
- [x] Ejecutar **comparación P1B sin limitador iperf3** de 1/8 flujos, 1/2 miembros, afinidad de CPU, retransmisiones, distribución y reversión (ejecución 10/11/2026).
- [ ] Repetir ensayos con control experimental, variación de CPU y validación estadística para caracterizar capacidad efectiva virtual con incertidumbre. **No** equiparar los resultados internos de hasta 127,39 Gb/s a capacidad física.
- [ ] Comprobar LACP integrado al escenario multisede definitivo y diferenciar fallo de enlace de falla de equipo completo.
- [ ] Distinguir redundancia virtual de redundancia física; correlacionar con [#32](https://github.com/recm0708/netlab360/issues/32).
- [x] Redactar informe técnico P1 con mediciones, limitaciones y referencias a las cuatro capturas confirmadas por el operador.
- [x] **Recibir y revisar visualmente** 9 PNG P1/P1B del operador (P1 cuatro; P1B cinco), y contrastar las métricas con los logs aportados. [Auditoría visual de 14 PNG y fuente S04](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-auditoria-capturas-y-fuente-s04.md).
- [ ] **Importar** PNG/JSON/log originales al repositorio y manifiesto SHA-256, y completar controles experimentales/validación de redundancia multisede antes de cerrar.

**Ubicación corregida:** fase **5**, no impedimento para cerrar las pruebas núcleo de fase 2. No atribuir rendimiento agregado al valor nominal de una interfaz `veth`.

## Piloto P1 ejecutado el 10/11/2026 — validado por salida del operador

- [Script S05 LACP multistream acotado](https://github.com/recm0708/netlab360/blob/main/scripts/laboratorio/s05-lacp-multistream-piloto.sh): `--precheck` antes de `--run`; dos namespaces S05 propios, sin tocar `ens33`, Docker ni estado de S01–S04.
- **Resultados:** 1 flujo 120,06 Mb/s (0 retransmisiones); 8 flujos 959,81 Mb/s (0 retransmisiones); A1/A2 62,51 %/37,49 % bytes TX; 8 flujos con falla 2→1→2, 960,31 Mb/s de media y **553 retransmisiones**; `S05_RESULTADO_P1=0`, `S05_LIMPIEZA=OK`, 3 JSON válidos, SHA-256 registrado localmente. Cuatro capturas confirmadas tomadas, no recibidas ni auditadas.
- **Informe:** [sesión técnica S05/P1](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-lacp-multistream-piloto-validado.md). [Analizador de JSON y hashes, solo lectura](https://github.com/recm0708/netlab360/blob/main/scripts/validacion/s05-analizar-lacp-p1.py), preparado para ejecución posterior. 
- **Alcance:** las tasas están sujetas al límite aplicado de 120 Mb/s por flujo, por lo que no se deduce capacidad máxima; la retransmisión TCP impide afirmar fallo sin perturbación. No se declara integrado en el escenario multisede.
- **Análisis posterior completado:** 4/4 SHA-256 originales OK; manifiesto portátil validado 5/5 y TAR técnico creado localmente. Se revisaron intervalos, CPU y momentos aproximados de falla (5 s) y retorno (10 s), con 551/553 retransmisiones registradas en intervalos posteriores a la restauración.
- **P1B EJECUTADO:** [script](https://github.com/recm0708/netlab360/blob/main/scripts/laboratorio/s05-lacp-capacidad-comparativa.sh) e [informe de resultados reales](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-lacp-p1b-capacidad-validada.md). 1 flujo/2 miembros **70,21 Gb/s**; 8 flujos/2 miembros **113,30 Gb/s**; 8 flujos/1 miembro **127,39 Gb/s**; 8 flujos/2 restaurados **118,30 Gb/s**. Carga CPU cliente 98–200 % sobre 2 vCPU; 2/178/243/75 retransmisiones; distribución 50,26/49,74 % con 2 miembros, y 0/100 % con uno. Ratio 0,889 (dos vs uno, **−11,06 %**) sin inferencia causal ni capacidad de red física. Limpiado, 4 JSON válidos, manifiesto local SHA256 5/5. Cinco capturas confirmadas, aún sin auditar PNG.


## Auditoría de capturas recibidas 10/11/2026

Se examinaron los PNG de las cuatro pruebas del piloto P1 y cinco del comparativo P1B (sin incluir los dos prechecks generales). Todas ilustran resultados coherentes con las transcripciones: 1 flujo 120,06 Mb/s y 8 flujos 959,81 Mb/s, fase 2→1→2 con 553 retransmisiones; comparativa virtual 70 205,77 / 113 299,56 / 127 389,56 / 118 303,70 Mb/s, respectivamente. Se evita afirmar capacidad física o cero pérdidas. La **revisión de contenido visual está finalizada; la incorporación de bytes originales y su hash al repositorio no**. [Auditoría visual de 14 PNG y fuente S04](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-auditoria-capturas-y-fuente-s04.md).


## Corte 14/11/2026 — integración multisede, sin despliegue todavía

- [x] Lotes 107/108 en VM: validador `s05-lacp-integracion-precheck.py` 5/5 tests, plan 3 sedes, **35 direcciones IPv4 inventariadas**, switches/VLAN HQ120/S1-220/S2-320 protegidos, candidatos `10.70.20.40`, `10.71.20.40`, `10.72.20.40` no asignados ni con respuesta ICMP. `LOTE108_PRECHECK=OK`; seis units activos, Git limpio. Falta advertencia de IP silenciosa; no declarar reserva definitiva global.
- [x] Captura **`S05_45_LACP_Precheck_Integracion_Multisede`** declarada tomada por operador; salida terminal comprobada, PNG aún no auditado/importado.
- [x] Publicado **script HQ VLAN 120** `scripts/laboratorio/s05-lacp-hq-integracion.py` (PR #100), con operaciones `plan/precheck/up/status/down`, `up/down` bajo confirmación explícita, 2 veth a bond 802.3ad de cliente S05, un único puerto lógico en bridge S02, control de puertos/VLAN/servicios HA/gestión, alias de propiedad y limpieza selectiva. Pruebas offline CI B1-B4 exitosas; **script todavía NO ejecutado en VM**, ni HQ/S1/S2 modificados.
- [ ] **Inmediato:** sincronizar `main`, pruebas offline y `plan/precheck` HQ; solo después ejecución controlada de `up` HQ, revisar pruebas/pings/estado y evidencia, después falla 2→1→2. S1/S2 no desplegados. Conservar WAN OSPF y servicios HTTP.

## Corte 14/11/2026 — HQ realmente integrado, falla controlada pendiente

- [x] **Lote 109:** Git `a44f630` sincronizado; 8/8 tests `test_s05_lacp_hq_integracion.py` OK; `plan` HQ VLAN120 y `S05_LACP_HQ_PRECHECK=OK_SIN_CAMBIOS`; `LOTE109_HQ_PRECHECK=OK`. Hubo dos desconexiones SSH al inicio, ambas antes de éxito/despliegue; una tercera sesión completó el lote.
- [x] **Lote 110:** `s05-lacp-hq-integracion.py up --confirm-isolated` completó. Bond `s5bond0` del switch S02 HQ y `bond0` del namespace nuevo `nl360-s05-lacp-hq` negocian ambos **2 puertos 802.3ad layer3+4**, `s5p1/s5p2` ↔ `s5c1/s5c2`. Puerto lógico del bridge VLAN **120 PVID Egress Untagged**, IP cliente `10.70.20.40/24` (desde ahora **ocupada en HQ**, no solo candidata). Ping a `10.70.20.1`, `10.70.20.23`, `10.71.20.21`, `10.72.20.20` OK, HA HTTP/FIB/puertos S02 intactos, ens33 `192.168.47.40/24`, GW `.2`, Git limpio; `LOTE110_HQ_UP=OK`.
- [x] **S05_46 y S05_47:** salidas delimitadas comprobadas con contenido correcto (modo IEEE 802.3ad 2 miembros en ambos extremos, VLAN120 y conectividad/gestión). **No confirmado aún el archivo PNG capturado**; preguntar antes de considerarlo incorporado.
- [x] **PR #102** integrado con prueba 2→1→2 solo de esclavo cliente `s5c1`, rescate transitorio de `systemd-run` para corte SSH y `finally` que restaura primero y exige postcheck antes de cancelar el rescate. CI offline exitosa; **todavía no ejecutada en VM**.
- [ ] **Siguiente:** `git pull`, validar tests de prueba de falla, `--precheck`, ejecutar `run --confirm-failover` solo si pasan. Verificar 2→1→2, HTTP real, FIB/Git/gestión, guardar S05_48/S05_49. No cambiar S1/S2 aún. Issue abierta.

