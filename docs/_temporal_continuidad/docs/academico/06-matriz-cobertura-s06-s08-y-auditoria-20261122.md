# NETLAB360 — Matriz temporal de cobertura académica S06–S08

**Corte de análisis:** 22/11/2026, hora de Panamá. **Estado:** insumo temporal para planificación, no informe técnico final ni evidencia de funcionalidades implementadas. **Eliminar este archivo junto a la carpeta `docs/_temporal_continuidad/` al terminar las ocho fases y verificar que ningún dato único se pierda.**

## Regla de origen de evidencias

Los capítulos docentes, actividades individuales, laboratorios resueltos y parcial entregados por el estudiante son **referencias de aprendizaje y metodología**. Sus capturas, datasets sintéticos y cifras no constituyen mediciones realizadas en NETLAB360. No cargar sus PDF/ZIP/XLSX originales al repositorio salvo necesidad y autorización expresa; registrar únicamente la matriz derivada.

## Estado comprobado de plataforma

- S01–S05: solución multisede HQ/S1/S2 con tres FRR, cuatro WAN/OSPF, nueve VLAN, HTTP HA, LACP de tres sedes, SDN OVS/Faucet y NOC, versionados en `main`.
- 22/11/2026: APT, Snap y dependencias Python aisladas preparados; reinicio Ubuntu real con `7.0.0-44-generic` (S06-019).
- S06-020–024: recuperación manual de 21 namespaces, cuatro contenedores, seis servicios, observadores habilitados, NOC `healthy`, 18 nodos/21 enlaces, LACP 2/2, Faucet conectado. Evidencia en bitácoras privadas de `~/netlab360-bootstrap/s06/`; **no implica arranque autónomo ni prueba de regresión completa**.
- S06 analítica: sin dataset definitivo, modelo ML entrenado ni inferencia aceptada. S07/AIOps y aplicación S08 aún pendientes.

## Matriz de correspondencia entre contenido docente y producto

| Fuente académica recibida | Principio o práctica acreditada en esa fuente | Estado/traslado a NETLAB360 | Fase y seguimiento |
|---|---|---|---|
| Capítulo I, Actividad 1, Laboratorio 1 | Intención, SoT, drift, reconciliación, idempotencia, Intent Assurance y OSPF | S02–S03 tienen fundamentos; utilizar verificaciones de intención en escenarios del menú, sin confundir compliance con disponibilidad | S03 existente; S07 #7, S08 #8 |
| Capítulo II, Actividad 2, Laboratorio 2 | OpenTofu, módulos, recursos, estado, locking, ownership, WireGuard | S03 utiliza `terraform_data` local y Ansible modifica FRR; proveedor externo y túneles no se atribuyen a S03. Cualquier ampliación necesita justificación y aislamiento | #17 condicionado; #8 |
| Capítulos III–IV, Laboratorio 3 | Ansible multivendor, roles, CI/CD, Policy as Code, reconciliación y rollback | S03 ya tiene cumplimiento Ansible FRR; una interfaz S07/S08 debe ejecutar procedimientos permitidos, no shell arbitraria. VyOS adicional es opcional y no está implementado | #7, #8 |
| Capítulos V–VI, Laboratorio 4 | Telemetría, Prometheus, Blackbox, SLI/SLO, error budget, burn rate, failover, Grafana | S04 dispone de exporter/histórico/Prometheus y S05 NOC; contrastar por origen, series y estado real; diferencias de HTTP 200 vs buen rendimiento | #25, #26, #8 |
| Capítulo VII y Parcial 1 | Redes híbridas/cloud native; Kubernetes, Cilium/Hubble, eBPF, tráfico FRONTEND/API y experimentos NORMAL/DEGRADATION/RECOVERY | Adoptar metodología y correlación; Kubernetes/Cilium/Hubble solo se añadirá si aporta un caso distinto y es viable en la VM, nunca por inflar tecnología | #7, #8; opcional condicionado |
| Capítulo VIII y Parcial 1 | Ingesta, calidad, ventanas, dataset, trazabilidad; data leakage y shortcut learning | Construir pipeline sobre mediciones de NETLAB360, no copiar datos de otros laboratorios como pruebas propias | S06 #25 |
| Capítulo IX y Laboratorio 6 | IA/ML para operación, reglas vs modelos, clasificación supervisada y decisiones NOC | Entrenar solo con etiquetas justificadas y separar decisiones humanas de recomendaciones ML | S06 #6, #26; S07 #7 |
| Capítulo X y Laboratorio 7 | Detección de anomalías, Isolation Forest, referencias históricas y análisis no intrusivo | Comparar detección estadística con contexto de red, detección no equivale a incidente o autorización de cambios | S06 #25, #26; S07 #7 |
| Capítulo XI y Laboratorio 8 + libro de cálculos | Predicción de degradación, series temporales, horizonte `t+10`, uso de MAE y costo de alertas; análisis pre/post QoS | Pronóstico por horizonte medible, comparación de MAE con FP/FN y impacto del cambio de QoS en SLI/servicio; no usar información futura en predicción | S06 #26; S08 #8 |
| Capítulo XII y Laboratorio 8 | Explicabilidad, overfitting, model/data/concept drift, cambios de contexto y revisión humana | Monitorizar explicación/deriva, calidad y degradación del desempeño; nueva calibración cronológica cuando proceda | S06 #26, S07 #7 |
| Guía de elaboración y formato de proyecto | Informe mínimo 40 páginas, diseño, implementación, pruebas, resultados, referencias, anexos; PowerPoint y demostración | Mapear resultados propios a estructura docente, evitar redundancias y mostrar cambios reales desde menú sin comandos | S08 #27, #44, #45 |

## Arquitectura funcional prevista S06–S08 (diseño, no implementación)

1. **S06 Datos/IA:** mediciones propias y eventos etiquetados → limpieza y trazabilidad → ventanas/particiones temporales → baseline por reglas/P95 → modelo supervisado o no supervisado según etiquetas → métricas FP/FN, precision/recall/F1/costo y MAE cuando corresponda → inferencia solo lectura, explicabilidad y registro de UNKNOWN.
2. **S07 AIOps supervisado:** correlación de métricas y eventos → diagnóstico y recomendación → **aprobación humana explícita** → script/acción permitida con prechecks, límites, auditoría y rollback → postchecks de infraestructura/servicio.
3. **S08 Aplicación interactiva:** menú web con Inicio, Topología, Redes, HA, LACP, SDN, Pruebas ICMP/HTTP/iperf3, Métricas/Dashboards, IA, Incidentes/Runbooks, Evidencias; ejecutar scripts definidos en backend sin entrada de shell libre; registrar línea de tiempo y refrescar estado real.
4. **Pruebas:** NORMAL → DEGRADATION/FAULT → RECOVERY, incluyendo caídas de ruta/enlace/miembro LACP, indisponibilidad HTTP, segmentación SDN, pérdidas y retardos `tc netem`, pruebas iperf3 limitadas, latencia p95 y recuperación, sin tocar `ens33`.
5. **Entrega:** regresión offline y en vivo, ejecución reproducible del menú, restauración tras arranque frío, PPT, informe y TAR técnico sanitizado. No confundir failover lógico dentro de una VM con HA física.

## Puertas de aceptación

- **P0 antes de S06:** comprobar después de actualización, con scripts sin efectos destructivos, red de gestión, estado WAN/LAN/HA/LACP/SDN, API, Prometheus/SQLite, dependencias, tests y ausencia de warnings; archivar bitácora en `netlab360-bootstrap`.
- **S06:** fuentes auditadas, etiquetas/particiones sin leakage, resultados sobre TEST separado y comparación contra baseline. Instalar bibliotecas no equivale a aprobar el modelo.
- **S07:** flujo completo con aprobación, tiempo medido, acciones autorizadas y recuperación verificada; no realizar cambios no supervisados.
- **S08:** interfaz usable sin consola durante la demostración, gráficos vinculados a observación, pruebas con límites, escenarios restaurados, TAR íntegro y defensa sustentada.
- **Milestones:** mantener 6–8 abiertas hasta cumplir sus puertas de aceptación; no reabrir S01–S05 por mantenimiento rutinario.

## Riesgos y decisiones abiertas

- **Guía vs política de anexos:** la guía oficial incluye anexos como apartado 12; el plan interno actual eligió informe sin anexos y TAR técnico separado. Resolver explícitamente el modo de cumplimiento antes de dar por cerrado #27; un TAR no equivale automáticamente a cumplir la estructura escrita.
- **Datos sintéticos:** están permitidos como material de enseñanza/modelización, pero deben marcarse y mantenerse separados de las mediciones reales del entorno NETLAB360; no usar datos rotulados por la propia acción como única evidencia de exactitud predictiva.
- **Escalabilidad:** no desplegar más sedes, WireGuard, VyOS, Kubernetes o Cilium sin caso de uso, presupuesto de recursos y pruebas de aislamiento. Conservar la red principal funcional.
- **Persistencia:** la reconstrucción de S02–S05 ya fue probada manualmente tras reinicio, pero arranque automático desde VM apagada y runbook de usuario final aún pendientes (#106).
- **Archivos:** conservar guías y trabajos académicos fuera del árbol técnico final. No incluir tokens, respaldos privados, estados de OpenTofu o carpeta temporal en el TAR.

## Seguimiento GitHub

- S06: [#6](https://github.com/recm0708/netlab360/issues/6), [#25](https://github.com/recm0708/netlab360/issues/25), [#26](https://github.com/recm0708/netlab360/issues/26)
- S07: [#7](https://github.com/recm0708/netlab360/issues/7)
- S08: [#8](https://github.com/recm0708/netlab360/issues/8), [#27](https://github.com/recm0708/netlab360/issues/27), [#34](https://github.com/recm0708/netlab360/issues/34), [#44](https://github.com/recm0708/netlab360/issues/44), [#45](https://github.com/recm0708/netlab360/issues/45), [#106](https://github.com/recm0708/netlab360/issues/106)

**Este documento no exige instalar nuevos paquetes ni reiniciar la VM.** Cualquier cambio en topología, scripts o interfaces requiere implementación y pruebas independientes.
