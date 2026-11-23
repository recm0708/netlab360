# NETLAB360 — Plan maestro vigente S06–S08

**Corte:** 22–23 de noviembre de 2026. **Finalidad:** documento técnico permanente para retomar el trabajo sin reconstruir el contexto de conversaciones. **No sustituye los PDF docentes originales ni equivale a resultados no ejecutados.**

## 1. Objetivo del proyecto

**Título:** Plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede.

Plataforma de laboratorio en Ubuntu Desktop 26.04.1 LTS/VMware Workstation, con tres sedes **HQ, S1 y S2**, red administrativa `ens33 192.168.47.40/24` y gateway `192.168.47.2`, separadas de las redes experimentales. Reproducir, monitorizar, diagnosticar y demostrar situaciones reales de red en una consola web interactiva con pruebas ejecutables, resultados medibles, recomendaciones y recuperación controlada.

**No confundir:** alta disponibilidad lógica dentro de una VM ≠ tolerancia a falla física del host o hipervisor.

## 2. Lo implementado y comprobado — S01–S05

| Componente | Estado acreditado |
|---|---|
| S01 | Máquina virtual, herramientas, IPAM inicial, acceso SSH y línea base |
| S02 | Tres routers FRRouting, OSPF con cuatro WAN (primarias y alternas), nueve VLAN y clientes en tres sedes, pruebas de conectividad |
| S03 | SoT candidate, Ansible FRR para compliance/drift/reconciliación, OpenTofu con metadatos locales `terraform_data`, CI/GitHub; **no** aprovisionamiento externo real con OpenTofu |
| S04 | Exporter, Prometheus, SLI/SLO experimentales, incidentes y NOC con histórico SQLite |
| S05 | HTTP HA HQ↔S1, LACP 802.3ad en HQ/S1/S2, SDN con OVS/Faucet, NOC de topología y telemetría |
| Recuperación 22/11/2026 | Reinicio **real del invitado Ubuntu**, kernel `7.0.0-44-generic`, restauración **manual** S02–S05: 21 namespaces, 4 contenedores y 6 servicios NETLAB360; NOC `healthy=true`, 18 nodos, 21 enlaces; sin fallo de gestión |
| Entorno S06–S08 | venv aislada bajo `~/netlab360-bootstrap/entornos/netlab360-s06-s08`, NumPy/pandas/SciPy/scikit-learn, FastAPI, Dash, Plotly, pytest y utilidades. Bibliotecas instaladas **no equivalen a funcionalidades implementadas** |

**Regresión posterior al reinicio, corregida y aprobada (S06-029):** S06-025/026/027/028 identificaron falsos positivos en `status` WAN/LAN cuando la ruta `172.17.0.0/16 dev docker0` conservaba sus atributos y solo cambiaba el indicador transitorio `linkdown`. El PR #154, integrado en `main` (`ffde7b5`), normalizó exclusivamente ese caso y añadió 16 pruebas unitarias de aceptación/rechazo. La regresión S06-029 de la VM pasó: WAN/LAN, OSPF 4/2/2 FULL, HA, LACP HQ/S1/S2, SDN 31 reglas, NOC 18 nodos/21 enlaces y 376 tests offline, con `ens33 192.168.47.40/24` y gateway `.2` intactos; `S06-029_REGRESION_CORREGIDA=OK`. **Pendiente separado:** Prometheus S04 no escuchaba en `127.0.0.1:9091`, aunque binarios versión 3.7.0 y base TSDB histórica permanecían presentes. No inferir que los datos históricos constituyen ya un dataset ML etiquetado.

## 3. Material académico que alimenta el diseño

Se recibieron capítulos **I–XII**, materiales complementarios, actividades individuales, laboratorios resueltos y guías docentes del proyecto semestral, incluyendo laboratorios relacionados con IA, detección de anomalías, pronóstico, calidad de datos y QoS. Su matriz de cobertura por capítulo está en `docs/_temporal_continuidad/docs/academico/06-matriz-cobertura-s06-s08-y-auditoria-20261122.md`.

**Regla de procedencia:** capítulos y ejercicios son antecedentes didácticos, no mediciones NETLAB360. Para el informe solo atribuir resultados a ensayos genuinos con registros. No subir PDF docentes completos, respaldos privados ni material de terceros innecesariamente al TAR o repositorio.

## 4. Trabajo pendiente por fases y puertas de aceptación

### S06 — Ciencia de datos aplicada a la red y diagnóstico inteligente

- Adquirir datos reales de NETLAB360 en situaciones NORMAL, DEGRADED, FAULT y RECOVERY con origen, `session_id`, timestamp UTC, sede, enlace/servicio, condiciones, unidades y ground truth justificado; UNKNOWN si no hay suficiente certeza.
- Normalizar, controlar duplicados/ausencias, extraer características y ventanas; dividir TRAIN/VALIDATION/TEST por sesión y tiempo sin data leakage ni etiquetas filtradas.
- Implementar reglas explicables, umbrales históricos/P95, modelos supervisados **si existen etiquetas fiables**, y detección no supervisada cuando corresponda.
- Comparar precisión, recall, F1, FP/FN, sensibilidad, costo operativo, resultados por sede/escenario; utilizar MAE/error de horizonte solo para pronóstico genuino.
- Probar detección temprana de degradación, concept/data drift, incertidumbre y explicabilidad; API de inferencia inicialmente solo lectura.
- **Gate:** evidencia reproducible sobre TEST no visto, comparación honesta con reglas y limitaciones explícitas. Issues #6, #25, #26.

### S07 — AIOps supervisado

- Correlacionar evento, telemetría, estado OSPF/FIB, HA, LACP, SDN y diagnóstico S06.
- Diseñar catálogo de procedimientos permitidos, prechecks, bloqueo de concurrencia, límites y aprobación humana antes de modificar redes.
- Ciclo medido **detectar → explicar → recomendar → aprobar → ejecutar → verificar → rollback/restaurar**, con bitácoras y postcondiciones.
- Sin autoejecución de cambios riesgosos por resultados IA. **Gate:** escenarios reales con aprobación, acciones reversibles, auditoría y red de gestión intacta. Issue #7.

### S08 — Consola web interactiva, regresión y entrega

- Crear **un único menú web central**, integrando NOC S05 existente, pruebas ICMP corto/extendido, traceroute, HTTP y TCP/UDP iperf3 limitado entre endpoints permitidos, series y visualización, inferencia S06, recomendaciones/acciones S07 y resultados antes/después.
- Vincular cada botón a **identificadores de acciones aprobadas** en un catálogo versionado, no a cadenas de shell ingresadas por el usuario. Guardar implementaciones en `scripts/s08/acciones/`; instalar ejecutores privilegiados revisados como archivos root-owned fuera de la carpeta Git editable.
- API única y visualización operativa sin necesidad de teclear comandos en la demostración; auditar parámetros, tiempos, resultados y postcondiciones; distinguir READY/DEGRADED/DOWN/UNKNOWN.
- Probar regresión y recuperación desde reinicio/arranque frío, sin afectar `ens33`.
- **Gate:** demo integral y TAR técnico seguro/verificado, PowerPoint e informe académico validados. Issues #8, #27, #44, #45, #106.

**Orden de implementación:** terminar regresión S06-025/026 y corregir `status` WAN → diseñar/adquirir datos S06 → modelos y métricas → AIOps S07 → consola S08 e integración progresiva → pruebas finales/entrega. Se puede crear el esqueleto del frontend en paralelo, pero no marcar pantallas de IA como operativas antes de su implementación.

**Adquisición S06 validada en VM:** PR #155 incorporó `scripts/s06/capturar_baseline.py` y PR #156 `scripts/s06/medir_rendimiento.py`; ambos se probaron localmente en S06-032/033 (12+12 registros válidos), con procedencia y etiqueta `UNKNOWN`. Las sesiones fueron auditadas en S06-034 con el normalizador del PR #157; **no** constituyen un dataset de entrenamiento etiquetado ni acreditan un modelo de IA. Protocolos: `docs/diseno/s06-adquisicion-observacional.md`, `docs/diseno/s06-mediciones-rendimiento.md` y `docs/diseno/s06-normalizacion-y-calidad.md`.

## 4.1. Adquisición S06-032/033 y normalización S06-034 (22/11/2026, Panamá)

**Avance funcional estimado de S06: 35 %**, cálculo conservador del esfuerzo implementado frente al alcance total de datos, experimentos, modelos, pronóstico y API; no calificación docente. No usar la proporción de casillas ni la cantidad de pruebas como porcentaje de IA completada.

- **Infraestructura validada:** S06-029 corrigió WAN/LAN (PR #154) y confirmó 376 pruebas, HA/LACP/SDN/NOC. S06-030/031 restauró Prometheus 3.7.0 en localhost 9091 mediante unidad temporal systemd, resguardó la TSDB y observó cinco familias de métricas S04. S06-032/033 alcanzó 407 pruebas offline, siete servicios operativos, 21 namespaces, cuatro contenedores, sin modificar `ens33` ni el gateway.
- **Sesión de referencia S06-032:** `S06_BASELINE_20261123T043741Z_39a268`, 12/12 observaciones JSONL íntegros; 25 series por consulta, cinco familias, etiqueta `UNKNOWN` y `ground_truth_verified=false`.
- **Sesión de rendimiento S06-033:** `S06_PERF_20261123T044532Z_cea2dc`, enlazada a S06-032, 9 pruebas ICMP (3 por ruta) y 3 HTTP. Pérdida 0 % en el periodo observado; RTT promedio HQ→S1 **0.084 ms**, HQ→S2 **0.074 ms**, S2→frontend HQ **0.081 ms**; HTTP medio **7.594 ms**, backend `BACKEND_HQ`; JSONL y permisos comprobados, `S06-033_RENDIMIENTO_VALIDADO=OK`, RC=0. Son tiempos en una VM, no WAN físicos ni un SLO estadístico.
- **S06-034 ejecutado y validado:** `S06-034_NORMALIZACION_VALIDADA=OK`, RC=0, **423/423 pruebas offline**. Derivado privado `S06_QA_20261123T045339Z_4658bf`, integridad verificada, 375 filas de métricas (`prometheus_s04=300`, `icmp_s02=72`, `http_s05=3`), 0 scrapes repetidos detectados, 0 valores faltantes y 0 etiquetas supervisadas. Familias S04: routers 36, source 12, topology 48, VLAN 108 y WAN 96; cada sonda de rendimiento presenta tres muestras. Timestamps UTC y unidades `state/packets/percent/ms` válidos; raws conservados sin cambios. **375 filas no son 375 observaciones independientes de aprendizaje**.
- **Pendiente inmediato:** S06-035 validar aislamiento físico/lógico de interfaces candidatas, qdisc actual y plan de experimentación con intervención y reversión. Luego recopilar sesiones con etiquetas verificadas, iperf3 TCP/UDP restringido, TRAIN/VALIDATION/TEST por sesión/tiempo, modelos/anomalías, pronóstico/drift e integración.
- **Política GitHub:** issues #6, #25, #26 y dependientes #7/#8 actualizadas con esta evidencia; no cerrar ninguna con casillas sin comprobar. Los programas para S08 seguirán usando un catálogo de acciones allowlisted y autorización humana.

## 4.2. S06-035: precheck de escenarios de degradación (solo código)

PR [#158](https://github.com/recm0708/netlab360/pull/158) fusionado (`317ab99`), con el precheck de escenarios y 18 pruebas nuevas. **S06-035 validado en VM real**: 441/441 tests offline, `S06-035_PLANIFICACION_VALIDADA=OK`, RC=0; `nl360-s02-h-hq-120`/`eth0` UP con `10.70.20.20/24`, gateway `10.70.20.1` y qdisc `noqueue` (estado `CANDIDATE_NOQUEUE`), plan JSON privado `S06_035_20261123T050249Z_6cb815`. Red `ens33 192.168.47.40/24`/gateway `.2`, 21 namespaces, 4 contenedores, NOC intactos, sin fallas inducidas ni etiquetas. **S06-036 concluido**: PR #159 (`bf4699a`), **457/457 tests** y ejecución real del temporizador marcador aprobada en VM; solo crea un marcador, no altera qdiscs. Ver la aceptación detallada en la sección 4.3. No se permite `tc netem` hasta probar un watchdog real de restauración y su rollback. El avance técnico estimado sigue en **35 %**.

## 4.3. S06-036/037: temporizador verificado y seguridad simulada (23/11/2026)

- **S06-036 validado en VM:** `S06-036_TIMER_VALIDADO=OK`, RC 0; 457 pruebas offline y 16 específicas. Unidad transitoria systemd `netlab360-s06-wd-probe-4cf18377` ejecutó un marcador privado y quedó documentado en `~/netlab360-bootstrap/s06/watchdog-tests/S06_036_4cf18377/S06_036_Resultado_Watchdog.json`. El estado `qdisc noqueue` en `nl360-s02-h-hq-120/eth0`, la gestión `ens33 192.168.47.40/24`, gateway `.2`, NOC y Prometheus siguieron intactos. **Es un timer inocuo, no rollback real**.
- **S06-037 código integrado, VM pendiente:** PR [#160](https://github.com/recm0708/netlab360/pull/160), commit `30343fc`, 478 pruebas CI aprobadas (21 nuevas). Simulador `scripts/s06/simular_rollback.py` con 14 escenarios de autorización, exclusión mutua, watchdog lógico, reloj virtual/TTL, crash, fallo y escalamiento por propiedad ajena. Informe solo de simulación; `real_rollback_implemented=false` y etiquetas `UNKNOWN`. [Protocolo](s06-rollback-simulacion.md).
- **Próxima operación:** ejecutar S06-037 en Ubuntu y revisar las 14 simulaciones, datos privados y topología. Después construir S06-038 con ejecutor root-owned, bloqueo, propiedad de qdisc, timer de restauración real, ensayo de fallo y pre/postchecks. **No ejecutar netem** hasta demostrar los mecanismos de recuperación.
- **Avance técnico estimado:** 35 % de S06; no es calificación docente. Las sesiones observadas y la normalización están aprobadas, pero no hay etiquetas verificadas por estímulo, dataset representativo, modelos entrenados, pronóstico ni API de inferencia.

## 4.4. S06-037 comprobado en VM (23/11/2026)

`S06-037_SIMULACION_VALIDADA=OK`, RC=0: 21 tests específicos, **478/478** pruebas offline; 14 escenarios de simulación con estados `RESTORED=4`, `ABORTED=1`, `ESCALATED=2`, `NEW=5`, `APPROVED=2`. El reporte privado `~/netlab360-bootstrap/s06/rollback-simulaciones/S06_037_20261123T051618Z_66720c/simulacion_rollback.json` fue verificado contra la huella indicada por el programa. Qdisc real `noqueue` antes/después, `ens33 .40`, gateway `.2`, 21 namespaces, 4 contenedores, NOC 18/21, Prometheus READY, cero unidades fallidas. **No hubo cambios de red, netem real, etiquetas verificadas ni rollback real.** El porcentaje técnico S06 sigue estimado en **35 %**. S06-038 deberá implementar guardas privilegiadas, timer efectivo y restauración demostrable con pruebas adversas; las issues siguen abiertas y no se permiten cierres con casillas sin verificar.

## 4.5. S06-038A — guardia root y timer de estado NOOP (23/11/2026)

PR [#161](https://github.com/recm0708/netlab360/pull/161) fusionado (`509a3da`) tras pasar **499/499 tests offline** (21 nuevas pruebas específicas). La guardia `scripts/s06/guardia_protegida.py` se instala como copia root-owned en `/usr/local/libexec/netlab360/s06-guardia.py`, revisa exclusivamente `ens33` y el cliente HQ `nl360-s02-h-hq-120/eth0`, protege estado y lock bajo `/run/netlab360-s06`, programa timer transitorio de 5–30 s y registra vencimiento de estado `EXPIRED_NOOP`. **No contiene ninguna operación que agregue, borre o reemplace qdiscs.** **S06-038A aceptado en VM:** `S06-038A_GUARDIA_ROOT_VALIDADA=OK`, RC 0, 21 tests específicos y 499 globales correctos. Ejecutable root 0750 íntegro, auditoría de IPAM/qdisc `noqueue`, timer `netlab360-s06-guard-cf7b78e1daea9747` venció en `EXPIRED_NOOP`, cleanup dejó estado `NONE`. Gestión, topología, 7 servicios y NOC intactos. S06-038B deberá demostrar restauración de qdisc primero en namespace efímero **aislado**, no sobre el cliente real, antes de cualquier intervención de producción. El código simulado y el NOOP no acreditan rollback real ni permiten fallas inducidas. `S06=35 %` estimado. [Protocolo](s06-038-guardia-root-y-watchdog-noop.md).

## 4.6. S06-038B: restauración real exclusivamente en dummy aislado (23/11/2026)

[PR #162](https://github.com/recm0708/netlab360/pull/162) fusionado (`e1d8000`), **523 pruebas CI offline aprobadas**. El ejecutor `scripts/s06/rollback_qdisc_aislado.py` solo opera en namespace temporal `nl360-s06-isotest` y dispositivo `dummy0`, sin IP, veth, bridge ni ruta; `tc netem 106:` con delay de 20 ms se instala únicamente **después** de comprobar el watchdog root systemd (TTL 20 s). Timer espera la liberación del lock, coteja estado/token/identidad del namespace y solo elimina `netem` si pertenece a ese entorno aislado; caso ambiguo escala sin borrar. `cleanup` elimina solo namespace/dummy **tras comprobar** retorno `noqueue`. **Ejecución real en VM pendiente**: no afirmar todavía recuperación real verificada. La VM mantiene operativa la guardia NOOP S06-038A previamente validada. [Procedimiento y límites](s06-038b-restauracion-aislada.md). Ninguna intervención de producción, etiqueta de falla ni modelo IA aprobado; **35 % estimado S06**.

## 5. Diseño permanente de la consola

Especificación de menú, arquitectura y mapeo de procedimientos:
`docs/diseno/s08-consola-interactiva-y-acciones.md`. Reutilizar `servicios/topologia-s05/` sin romper su API ni interfaz; no duplicar innecesariamente el sistema NOC.

## 6. Formato de entrega excepcional — confirmado por la profesora

El estudiante confirmó que **para NETLAB360** la docente autorizó **TAR independiente en sustitución de anexos técnicos** de la guía general. Se entregarán:
- **Informe PDF**: mínimo 40 páginas, capítulos académicos, análisis, resultados auténticos, referencias; **sin capítulo de anexos técnicos**, conforme a excepción docente.
- **`.tar` externo**: scripts `.py/.sh`, `.yml/.yaml`, `.json`, `.tf/.hcl`, configuraciones FRR/OVS/Faucet, pruebas, inventarios e instrucciones reproducibles; excluir secretos, llaves, estados privados, respaldos, material temporal y archivos ajenos.
- **PowerPoint y demo**: problema, objetivos, arquitectura, metodología, pruebas, limitaciones y demostración **mediante el menú web, no tecleando comandos**.

No afirmar OVA/OVF obligatorio sin confirmación explícita. Revisar tamaño y canal de entrega antes de empaquetar. Verificar la integridad del paquete, auditar `tar -tf`, la extracción en directorio limpio y las pruebas offline.

## 7. GitHub, persistencia y conservación

Repositorio `recm0708/netlab360`, rama estable `main`; issues S01–S05 cerradas; **S06–S08 siguen abiertas**, sin confundir dependencias instaladas con funcionalidad. Referencias maestras: #6, #7, #8, #25, #26, #27, #34, #44, #45 y #106. #17 (OpenTofu externo) y #29 (OVA/OVF) son ampliaciones condicionadas y no bloquean las funciones obligatorias si no se requieren.

El histórico `docs/_temporal_continuidad/` es archivo temporal, no entrega final; solo eliminarlo cuando no contenga evidencias únicas y el informe/TAR estén completados. Estados runtime, registros originales privados, datasets en bruto y entornos Python permanecen bajo `~/netlab360-bootstrap/`. No eliminar imágenes Docker ni snapshots de recuperación sin validar.

**Para reanudar en otra conversación:** leer este documento y el diseño S08; consultar issues activas y estado local `git status`/comprobaciones S02–S05. **No** reejecutar despliegues `up` mientras existan los estados de propiedad; no apagar VM sin entender la volatilidad de los namespaces.

## 8. Política obligatoria de aceptación y cierre en GitHub

- Ninguna issue debe cerrarse mientras exista al menos una casilla `- [ ]` pendiente de implementación o validación.
- Marcar `- [x]` **solo** tras comprobar la condición con código, pruebas, bitácoras o evidencias identificables; nunca marcar para forzar el cierre.
- Si una tarea está resuelta pero quedó sin marcar por omisión, comprobar su evidencia y después actualizar su casilla. Si no existe evidencia, mantenerla abierta.
- Antes de cerrar una issue: revisar todas sus casillas, enlaces, dependencias, criterios de aceptación y correspondencia con la fase.
- No cerrar un milestone por calendario; verificar que las issues asignadas se hayan completado y cerrado formalmente.
- Auditoría del 22/11/2026: 38 issues cerradas revisadas; la única inconsistencia (#153) se corrigió contrastando PR #154, pruebas S06-029 y recuperación S06-030/031. Resultado: cero issues cerradas con casillas sin completar.
