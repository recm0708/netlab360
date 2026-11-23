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

**Precaución técnica:** la auditoría S06-025 y su continuación S06-026 identificaron que el `status` WAN compara literalmente la tabla de rutas del host: `docker0` conservaba `172.17.0.0/16` pero su marcador `linkdown` pasó a ausente tras iniciar Docker. La red administrativa y OSPF seguían intactos. Reparar el validador con prueba unitaria y no reducir controles de rutas críticas. La regresión completa debe reanudarse; no declarar S06-025 aprobada.

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
