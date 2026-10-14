# NETLAB360 — Matriz de aceptación y decisiones de cierre S01

**Fecha del registro:** 14/10/2026. **Fase interna:** S01, originalmente prevista 5–11/10. **Estado:** ABIERTA; criterios integrales del issue #1 sin aprobación global. **Avance 72/100:** ponderación de gestión interna, no nota docente. **IMPORTANTE:** el esquema original exige capacidades de automatización/IA/exportación dentro de S01 aunque las issues especializadas de OpenTofu/Ansible y ML están etiquetadas S03 y S06. No reinterpretar o recortar sin confirmar la guía docente.

| Nº | Criterio integral de S01 | Evidencia existente | Falta para aceptación integral | Dictamen |
|---|---|---|---|---|
| C01 | HQ + sucursal, VLAN, FRR/OSPF, WAN redundante, respaldo de equipo y servicio | VLAN/ACL aisladas, WAN HQ–S1 con OSPF+HTTP en tres estados | Integración VLAN→WAN→servicio en un mismo escenario; falla de equipo real/simulado | Parcial |
| C02 | LAG dos puertos, dual NIC, SoT/OpenTofu/Ansible | LACP virtual 2→1→2, active-backup virtual, IPAM YAML y IaC→FRR | Redundancia de equipo/servidor y ownership/reconciliación vivo exigibles | Parcial |
| C03 | API/dashboard e incidente real, métricas, alarma y tiempo | Exporter live, Prometheus tres reglas, dos firing/resuelta; NOC inicial | Integración de alarmas al NOC multisitio, receptor/SLI según alcance | Parcial |
| C04 | Prototipo evaluable de anomalía scikit-learn, distinto de reglas | 76 ICMP y 12 eventos de otras sesiones; perfil y reglas | Dataset etiquetado independientemente; modelo ML y evaluación fuera de muestra | Pendiente |
| C05 | Borradores de investigación, bitácora y manual | Borradores V0.1 anteriores RECHAZADOS como formato; nuevos índices maestros S01–S08 creados | Redactar por secciones en plantilla institucional, APA7 y capturas | En preparación |
| C06 | Pre/postcheck, recuperación, regresión integrada reproducible | Pre/postchecks, rollback y 24 tests offline | Prueba integral reproducible L2+WAN+servicio+NOC cuando requerida | Parcial |
| C07 | Integración red, automatización, observabilidad, analítica y dashboard | Módulos separados verificados, IaC alimentó FRR real | Flujo unificado de componentes | Parcial |
| C08 | Capturas trazables fecha/commit/resultados | 86 PNG, 7 CSV SHA256 en GitHub; lotes auditados | Cuatro fotos IaC recuperadas por logs aún no recibidas; captura postcheck nueva pendiente de incorporación | Parcial avanzado |
| C09 | Actualización de 3 documentos y compatibilidad | Política e índices maestros nuevos, bitácoras de sesiones | Contenido final revisado de tres documentos | En preparación |
| C10 | Commit/PR y tag/release demostrable | GitHub sincronizado y CI exitosa | Tag/release validado, PR si requerido | Pendiente |
| C11 | VM sanitizada, exportada/reimportada y SHA256 | VM funcional, snapshot conocido, gestión estable | Sanitización, exportación, reimportación y hash | Pendiente |

## Dependencias y decisiones que deben confirmarse

- **D01 / Prioridad bloqueante:** guía/rúbrica oficial y fecha: si 11 criterios son exigencia estricta de S01 o metas transversales semestrales. Registrar respuesta en issues #9 y #36. No cerrar por porcentaje.
- **D02:** si la OVA se entrega cada fase, como snapshot en S01 o solo al cierre S08; no borrar credenciales sin plan de recuperación.
- **D03:** alcance de integración de S01: si es obligatorio un único escenario que conecte VLAN↔WAN↔servicio↔NOC y redundancia de equipo o si los MVP separados bastan como demostración inicial.
- **D04:** si en S01 se necesita ML evaluado o únicamente baseline por reglas, ya que issues #25/#26 corresponden a S06.
- **D05:** metadatos institucionales, autores, docente, fecha oficial, norma de portada y extensiones, para redactar los tres maestros.

## Bloqueos y plan prudente

1. Conservar S01 ABIERTA, congelar S02 y nuevas funciones B4 mientras se aprueban índices y se redactan partes S01.
2. No repetir pruebas OSPF, IaC ni alertas sólo para capturas; reconstruir cuatro fotografías IaC desde logs ya validados.
3. Trabajar sobre TRES documentos maestros con capítulos por fase y UNA bibliografía/índice por documento.
4. Preparar una única regresión integral adicional sólo si criterio S01 la requiere; preferir prueba mínima con pre/postcheck, nunca tocar ens33.
5. Acordar alcance docente; ejecutar exclusivamente las brechas rubricadas; terminar documentación, release/OVA si obligatorio y cerrar con trazabilidad.

**Punto de control técnico:** commit b410548 (lote06), 86 PNG/7 CSV, CI 38511477595 exitosa, postcheck 23:35:02 del 13/10/2026 con Docker/netns vacíos y gestión intacta. Los commits nuevos documentales posteriores requieren pull ff-only de Ubuntu antes de operar.
