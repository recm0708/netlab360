# NETLAB360 — Indicadores y puertas de cierre por fase
**Corte original: 25 de octubre de 2026; actualización verificable vigente: 27 de octubre de 2026.** Porcentajes **estimados del alcance propio de cada fase**, no equivalentes entre sí ni a calificación docente. Se evita retroasignar como nuevos logros de fase 1 los módulos previstos en fases 4–8.

| Fase | Indicador | Condición técnica/administrativa | Pendientes reales para cierre |
|---|---:|---|---|
| **1 (S01)** | **72 % histórico** | Prototipo y escenarios iniciales probados: VM/IPAM/OSPF/VLAN/ACL, LACP virtual, SoT/IaC inicial, Prometheus/reglas, CI histórica y 90 PNG versionadas | Sus 28 puntos originales abarcan trabajos reasignados a las fases 2–8 y no deben reclamarse como ejecutados en fase 1. Se conciliaron 93 capturas originales: 90 seleccionadas y tres históricas excluidas; decidir cierre administrativo de la línea base sin exigir funciones de fases posteriores. |
| **2 (S02)** | **CERRADA por alcance propio** | Núcleo multisede validado: 3 routers/4 WAN, OSPF Full 4/2/2, 6 FIB, 6 ICMP, recuperación S1/S2, 9 VLAN/hosts, ACL HTTP 2 paquetes/120 bytes, regresiones y desmontaje controlado | Nueve evidencias finales S02_01–S02_09 publicadas, Figura 1 integrada al informe 3.2 y cierre interno validado en **issue #2 CERRADA**. No implica aprobación docente ni obliga a completar NOC fase 4, LACP/SDN fase 5, IA fase 6 o demo de fase 8. |
| **3 (S03)** | **90 %** | Ansible auditó 8/8 FRR, drift real cost100→150→100 y reconciliación idempotente; OpenTofu metadata-only 17/17, manifiesto 3/4/9, plan idempotente, PR #49 fusionado, GitHub Actions general y específica success; VM regresión 29/29 y 87/87 | Ocho capturas S03_01–S03_08 publicadas y verificadas. La evidencia remota de GitOps `S03_09` existe en Markdown con enlaces reales, **no en PNG**. Formalizar alcance: OpenTofu administra metadatos **no infraestructuras FRR**, y decidir si el objetivo de ownership externo/data sources sigue pendiente y pasa a fase posterior. Los capítulos 5–8 del borrador 3.2 ya incorporan los resultados; formalizar contrato SoT `candidate` (#16) y decidir/resolver data sources/ownership externo (#17) antes de cerrar #3. **No exige** módulos completos S04–S08. |
| **4 (S04)** | **G0–G4 técnicos OK; G5 medido; G6 pruebas y capturas OK** | Exporter 9110/Prometheus 9091/NOC 9120; G3 failover y alerta reales, G4 TSDB 68/68 y 28/28 + SQLite 3/3 tras reinicios; G5 15m 450/450 (100 %) y 60m 1698/1740 (97.586 %, 42 fallos), SLO 99 % solo candidato; regresión G6 OSPF 4/2/2, WAN 6/6, LAN 9/9+6/6; **22 PNG S04 auditadas** | Ratificar objetivo SLO/notificación local y actualizar Word/PDF borrador 4.0 (5.6,6.9,7.10,8, tablas/figuras) con revisión editorial; cierre administrativo S04 posterior. No repetir incidente G3 ni atribuir disponibilidad contractual. |
| **5 (S05)** | **0 % formal** | Redundancia/capacidad avanzada y SDN OVS/Faucet pendientes. LACP 2→1→2 aislado de fase1 es antecedente, no cierre de fase5 | Integración en entorno multisede, LACP pruebas multistream, falla de equipo/enlace, experimentación SDN, regresión y métricas. |
| **6 (S06)** | **0 % formal** | Diagnóstico inteligente no entrenado/evaluado | Dataset etiquetado por sesión, comparación contra reglas, validación sin fuga de datos, métricas de evaluación cuando exista referencia fiable. |
| **7 (S07)** | **0 % formal** | Integración integral de automatización + NOC + red + diagnóstico y recuperación extremo a extremo pendiente | Escenario reproducible completo y fallos encadenados con monitorización y recuperación. |
| **8 (S08)** | **0 % formal** | Entrega, demostración, paquete TAR y congelación final pendientes | Calidad/documentación, README, paquete **.tar externo sin apartado de anexos en informe**, auditoría de secretos, hashes, extracción de prueba, PPT y demostración en vivo. |

## Estado vigente: GitHub milestones frente al cumplimiento técnico — 27/10/2026

Se revisaron **50 issues normales**, abiertas y cerradas: **50/50 tienen milestone S01–S08**, ninguna carece de asignación. El porcentaje visible en GitHub se calcula exclusivamente sobre **issues cerradas / issues asignadas**; **NO** mide porcentaje de capacidades, cumplimiento del SLO, trabajo académico ni calificaciones.

| Milestone | Issues completadas / total | GitHub aproximado | Lectura correcta |
|---|---:|---:|---|
| S01 | 11/14 | 79 % | 72 % matriz histórica distinta, pendientes SSH/título/aceptación |
| S02 | 3/3 | 100 % | Cerrada internamente por alcance propio |
| S03 | 3/6 | 50 % | Automatización probada; tres seguimientos abiertos SoT/metadata y fase |
| S04 | 2/6 | 33 % | NOC y Prometheus completados en #15/#20; SLO/academia/fallas/cierre por formalizar |
| S05 | 0/6 | 0 % | Ninguna issue de S05 cerrada; correcto aunque LACP S01 sea antecedente |
| S06 | 0/4 | 0 % | AIOps no evaluado |
| S07 | 0/1 | 0 % | Integración avanzada pendiente |
| S08 | 1/10 | 10 % | Un seguimiento previo consolidado, paquete y defensa pendientes |

Los dos cierres parciales S04 corresponden a funcionalidades **verificadas**; no se cerró la issue #4 ni la #47 (revisión del 30/10 aún futura), ni se adelantó el SLO del 99 % como aprobado. Los títulos/checklists antiguos se preservaron como cronología, con **encabezado de estado vigente** que prevalece para nuevas consultas.

## Reglas de cierre

1. Una fase se acepta **por su alcance explícito**, no por la finalización total de NETLAB360. Los componentes reaprovechados se registran en la fase que los implementó; no se exige repetirlos.
2. Una captura localizada por PowerShell no significa que se revisó visualmente; un fichero Markdown verificable de GitHub no es imagen PNG.
3. **Fase 1 72 % es un indicador histórico de matriz propia de 100 puntos; 90 % fase 3 es una estimación de seguimiento no basada en esa matriz; fase 2 está cerrada por aceptación interna de su alcance y fase 4 tiene aceptación parcial sin porcentaje arbitrario.** No sumarlas ni promediarlas como métrica global.
4. Las evidencias GitHub se mantienen en `evidencias/capturas/fase1` a `fase8`, con `S01_` a `S08_` como prefijo. El inventario publicado y verificado es de 90 PNG fase1, 9 fase2 y 8 fase3. Los lotes históricos y el de 21 capturas nuevas se acreditan mediante sus propios manifiestos de integridad. Se validaron localmente y publicaron mediante [PR #58](https://github.com/recm0708/netlab360/pull/58) **7 PNG S04 y un CSV SHA-256**. **Registro histórico del primer lote:** en ese momento había 114 PNG; **al corte actual** el árbol remoto contiene **129 PNG** (90 S01, 9 S02, 8 S03, 22 S04) auditadas en tres lotes.
5. Versión académica más reciente recibida/auditada: **`1457-Proyecto Semestral_borrador4.0.pdf`, 94 páginas**, aún con fases 1–3, Figura 1 y Figuras 12–15. Permanece pulido tipográfico transversal registrado en [#27](https://github.com/recm0708/netlab360/issues/27); fase 4 requiere incorporar nuevas implementaciones/pruebas solamente cuando estén validadas.
6. La docente aceptó entrega de código en archivo **TAR independiente**, no en sección de anexos Word. No imponer OVA.
7. La VM preserva el state OpenTofu S03 fuera de Git. **El laboratorio S02 fue reactivado temporalmente para S04 y se encuentra desplegado** (3 FRR/4 WAN/9 VLAN, validado en vivo); retirarlo por orden seguro al cerrar la sesión antes de comenzar S05, con respaldos y verificación. No repetir drift ni `tofu apply` solo para capturas.

Enlaces de control: [S02 #2](https://github.com/recm0708/netlab360/issues/2), [S03 #3](https://github.com/recm0708/netlab360/issues/3), [OpenTofu #17](https://github.com/recm0708/netlab360/issues/17), [GitOps #19](https://github.com/recm0708/netlab360/issues/19), [TAR #45](https://github.com/recm0708/netlab360/issues/45).

8. La progresión entre fases es flexible: pendientes legítimos S01/S03 no bloquean S04–S08. Revisar los criterios satisfechos en cada fase y actualizar la estimación solo si su propia matriz lo fundamenta. El 72 % S01 sigue siendo histórico, no un porcentaje automáticamente acumulativo de S04; no inventar ponderaciones retroactivas.

**Actualización 27/10:** S04_07–09 declaradas tomadas por el operador, sin auditoría/publicación. G3 precheck preparado por [PR #62](https://github.com/recm0708/netlab360/pull/62) con CI SUCCESS; prueba real de caída/restauración pendiente. No se modifica 72 % histórico S01 ni ≈90 % S03.

**Corte 27/10 G3:** HQ/s1p DOWN a 06:05:04Z, alerta `pending→firing` 06:05:07–06:05:13Z, respaldo s1b y S2 estable, restauración s1p/alarma no activa a 06:06:18Z; [bitácora comprobada](../sesiones/2026-10-27-s04-g3-incidente-real-y-recuperacion.md). Ocho imágenes S04 lote02 auditadas localmente, **pendientes de importar y publicar**, sin alterar contador remoto 114 PNG. G4–G6 por cerrar. Historial G4/G5 y [topología interactiva S05 #64](https://github.com/recm0708/netlab360/issues/64) definidos sin atribuir implementación inexistente.


**Corte verificable 27/10/2026 (posterior a lotes y postcheck):** Fase S04 conserva issues abiertas aunque sus puertas G0–G4 cumplen. G5 compara scrape 15m=450/450 (100 %) y 60m=1698/1740 (97.586 %) con el 99 % **solo candidato, no aprobado**; falla el objetivo propuesto a 60m, presupuesto restante −25. G6 dispone de **22 PNG S04 publicadas** (lotes 7+8+7), total remoto **129 PNG**, CI de integridad PR #75 y push SUCCESS, postcheck OSPF 4/2/2, FIB 6/6, gateways 9/9, pings LAN 6/6, NOC activo y gestión intacta. Falta ratificación de SLO/notificación y revisión del borrador académico en secciones 5–8 antes de aceptación de fase. [Matriz de cierre](../operaciones/s04-g6-matriz-aceptacion-evidencias-2026-10-27.md). **No modificar el 72 % histórico S01 ni 90 % estimado S03 por estos logros.**

**Corte editorial 27/10/2026:** el borrador **4.0** (94 páginas) aún tiene S04 «Planificada» en Tabla 5, la fila NOC futura en Tabla 1 y Tabla 12 con 107 capturas; las cifras y estados deben actualizarse **en el Word original**. El guion y [protocolo de apagado ordenado](../05-plan-operativo-y-pausas.md) ya se prepararon, pero no consta ejecución de parada ni edición final del manuscrito.
