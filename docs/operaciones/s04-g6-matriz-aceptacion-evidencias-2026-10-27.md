## Actualización de cierre técnico al borrador 4.4 — 27/10

Las verificaciones G0–G4 siguen aprobadas; G5 es **medición válida con SLO 99% candidato por ratificar**; G6 dispone de pruebas y evidencia técnica aceptadas, con redacción académica en evolución. El borrador 4.4 incluye 5.6 y 6.9, Figuras16–20 y Tabla13; capítulos7/8 y Tabla12 aún requieren actualización editorial. Catálogo actual de **122 PNG oficiales (83 S01 / 9 S02 / 8 S03 / 22 S04)**, conservando integridad original de cada archivo. El cierre de SSH ocurrió tras `sudo systemctl poweroff`; revisar indicador de VM Powered Off en VMware. La matriz debajo documenta los criterios medidos en el corte de su creación.

---

## Postcierre operativo posterior al corte de la matriz — 27/10

Las puertas G0–G4 técnicas se mantienen aprobadas; G5 SLO sigue propuesto, G6 aceptación académica aún pendiente. Desmontaje ordenado comprobado (LAN 12 namespaces, cuatro WAN, tres FRR) y cierre de observabilidad con respaldo TSDB/SQLite, hash verificado. Se ejecutó `sudo systemctl poweroff` después de `S04_APAGADO_AUTORIZADO=SI`; SSH cerrado; **verificación VMware Powered Off todavía pendiente**. El borrador **4.3 de 99 páginas** incorpora 5.6 completo, no 6.9/capítulo7–8 S04. Texto inferior «No se desmontan los recursos» corresponde al postcheck anterior y **ya no es el estado actual**. [Bitácora vigente](../sesiones/2026-10-27-s04-poweroff-solicitado-borrador43.md).

# NETLAB360 — S04 G6: matriz de aceptación técnica y cierre documental

**Corte:** 2026-10-27. Fuentes: salidas reales del operador y CI GitHub. **S04 aún no cerrada académicamente.**

| Puerta | Aceptación verificable | Estado al corte |
|---|---|---|
| G0 | Colector/Prometheus/NOC offline, tests y evidencia inicial | **Aprobada**, primer lote S04 7 PNG |
| G1 | 3 FRR, 4 WAN, 9 VLAN, OSPF FULL 4/2/2, FIB 6/6, gateways 9/9 e ICMP 6/6 | **Aprobada** |
| G2 | exporter 9110 25 series, scrape 9091 UP, NOC 9120 CENTRAL/HQ/S1/S2 | **Aprobada**, lote02 |
| G3 | incidente principal HQ/s1p 60s, pending→firing, backup s1b/S2 estable y recuperación | **Aprobada**, 06:05–06:06Z del 27/10 |
| G4 | TSDB persiste tras reinicio Prometheus 68/68 WAN y 28/28 firing, UNKNOWN sin falsa WAN, historial SQLite 3 eventos persiste tras reiniciar NOC | **Aprobada**, lote03 |
| G5 | SLI 15 y 60m con denominadores, SLO candidato y política de notificación | **Medición aprobada; SLO 99 % candidato y alcance local pendientes de ratificación**. Resultado 60m 97.586 % y presupuesto −25, sin maquillarlo |
| G6 | evidencias íntegras en GitHub, regresión final, secciones académicas e informe/aceptación | **Integridad y regresión aprobadas; redacción integrada y aceptación académica pendientes** |

## Trazabilidad de imágenes

Manifiestos `evidencias/manifiestos/MANIFIESTO_SHA256_S04_LOTE0[1-3]_...`:
- Lote01 7 PNG, [PR #58](https://github.com/recm0708/netlab360/pull/58).
- Lote02 8 PNG, [PR #67](https://github.com/recm0708/netlab360/pull/67).
- Lote03 7 PNG, [PR #75](https://github.com/recm0708/netlab360/pull/75), incluyendo capturas S04_12–17 (S04_15 tiene dos partes), SHA256 Windows/Ubuntu 7/7.
- Inventario remoto `main` **129 PNG total**: S01 90, S02 9, S03 8, S04 **22**. CI automática de auditoría SHA-256/dimensiones SUCCESS en PR y push de S04 lote03.

## Último postcheck sin fallas nuevas

- FULL HQ=4/S1=2/S2=2; rutas principales 6/6; seis pings router; gateways 9/9; seis pings LAN; fuente exporter `active_fresh`; scrape Prometheus `up`; NOC `active` con **0 alertas actuales** y diario G3 **3/3** eventos; `ens33=192.168.47.40/24`, default `192.168.47.2`. `S04_G6_POSTCHECK=OK`.
- Auditoría de capturas S04 LOTE03 `7/7`, manifiesto LF, cinco tests de importador y dos de inventario OK.
- No se desmontan los recursos FRR, WAN/LAN, servicios 9110/9091/9120; reservarlos para S05 sin atribuir aún aceptación a S05.

## Tareas antes del cierre de fase

1. Validar por el responsable del proyecto la **decisión explícita** de SLO académico candidato del 99 % y alertas **locales en NOC**, sin canal externo en S04. Reconocer el incumplimiento de la ventana de 60 min y la ausencia de medición extremo a extremo.
2. Integrar resultados de G0–G5 y limitaciones en las **secciones 5, 6, 7 y 8 del informe académico único**, respetando títulos/estructura y reglas reales del borrador más reciente; integrar referencias/citas que procedan, no repetir figuras ni inventar anexos. No crear informe nuevo para cada fase.
3. Revisar capturas por legibilidad visual para seleccionar las obligatorias del escrito; SHA-256/dimensiones automatizados NO sustituyen revisión visual humana. Mantener el resto para TAR técnico final, sin secretos/state.
4. Actualizar la matriz de issues S04 con aceptación interna después de ratificación; la **issue #47** representa reunión académica futura 30/10 y **no** se debe cerrar antes de ese evento. No transformar su porcentaje por progreso indirecto.
5. Conservar SQLite original, backup y JSON fuera de Git hasta decisión de inclusión revisada en TAR final; no publicar datos operativos inadvertidamente.

## Límites

`netlab360_s04_wan_admin_up` mide estado administrativo, no ICMP/OSPF; `up` mide scrape, no disponibilidad contractual; `source_up` solo existe con muestra presente; 0 alertas actuales no implica histórico vacío. `resolved` significa ausencia observada con fuente confiable, no certifica hora de reparación física ni entrega de mensaje externo. Futuro grafo animado y colores por enlace forman parte de S05 issue #64.
