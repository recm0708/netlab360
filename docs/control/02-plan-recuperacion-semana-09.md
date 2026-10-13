# NETLAB360 — Plan de recuperación de S01 desde semana académica 9

**Corte:** 13 de octubre de 2026, después de las 18:36 (Panamá).  
**Situación:** el operador indicó que el curso ya va por la **semana académica 9**, mientras que `S01` sigue abierta. La plantilla de GitHub programa `S01` para el 5–11 de octubre de 2026, lo cual puede representar una nomenclatura interna distinta del calendario docente. **No equiparar automáticamente semana S01 de GitHub con semana académica real; ratificar criterio y prioridad en [#36](https://github.com/recm0708/netlab360/issues/36).** No desplazar fechas S02–S08 ni alterar la rúbrica sin consulta.

## Estado probado al corte

**S01 53/100 técnico provisional** ([matriz](01-avance-s01.md)). B2 dual-WAN OSPF ya pasa Full/Full, usa WAN-P preferida, conmuta a WAN-B y retorna; se verificaron ICMP en subpruebas anteriores. B3 histórico y live disponibles. **Prometheus 3.7.0 real** con tres reglas cargadas y **dos alertas `firing`** tras cortar WAN-P; retorno del enlace deja **0 alertas WAN activas**. Se comprobó limpieza (`down=0`, puertos 9090/9108 libres, contenedores y namespaces vacíos, `ens33=192.168.47.40/24`, gateway `192.168.47.2`, `git status` limpio). [Bitácora](../sesiones/2026-10-13-b3-prometheus-alertas-firing-y-resolucion-verificadas.md).

**No significa fase completada.** Issue #1 tiene **11 criterios integrales de aceptación** y ninguno debe marcarse aprobado solo por un subhito parcial. La porcentual es gestión interna, NO nota ni cumplimiento jurídico/contractual.

## Secuencia de recuperación priorizada

| Prioridad | Bloque | Trabajo mínimo con evidencia de éxito | Dependencias y límite |
|---|---|---|---|
| P0 | **Cerrar pruebas repetidas B2/B3** | Preservar bitácoras y screenshots ya solicitados; no ejecutar otra WAN caída/restore salvo que un nuevo subsistema lo requiera. Validación de documentación en issues #42/#12 | No extender la instrumentación histórica; nuevas capturas PNG se auditan cuando usuario las envíe (#43) |
| P1 | **B2-L2 VLAN, trunk y ACL + cliente/servicio real** | Subtopología HQ/S1 con redes segmentadas, aislamiento positivo/negativo, política ACL y al menos un cliente/servicio realmente atravesando WAN-P y WAN-B; recoger comando + salida, sin depender solo de dummy IP de routers | Precheck de VM y espacio/CPU, inventario IPAM, no tocar red ens33/VMnet8; issue #30 y #42 |
| P2 | **Redundancia de enlace y equipo** | LAG/LACP de dos puertos con extremos compatibles, prueba up/down y restauración; host dual-NIC y conmutación de equipo/servicio hasta donde permita el hipervisor; distinguir simulación de redundancia física real | Validez de implementar LACP 802.3ad con Linux bridge/bond y dispositivos del emulador debe comprobarse; no declararlo completo con simple failover de ruta |
| P3 | **IaC reproducible** | SoT/IPAM consumido por OpenTofu/Ansible, validación plan/diff, apply controlado, segunda ejecución idempotente y comprobación de compliance; inventario y rollback con secretos excluidos | La instalación de herramientas ya existe, pero 1/10 pts en la matriz; evitar comandos que modifiquen red de gestión |
| P4 | **Prototipo analítico y validación** | Conjunto de métricas del laboratorio o dataset sintético **rotulado como tal**, baseline de reglas, modelo simple scikit-learn, train/test separados, métricas de clasificación y tasa de falsos positivos; no confundir detectores umbral con IA | Solo lo mínimo exigido por la rúbrica, no crear un módulo comercial innecesario |
| P5 | **Integración y entrega** | Integración reproducible en un runbook, pre/postcheck, informe académico, bitácora ilustrada, manual usuario, capturas versionadas, CI/PR/release, OVA sanitizada, importación de prueba y checksum | Issue #35, #43, #1; consulta #36 por alcance de entrega oficial |

## Acciones de gobierno inmediatas

1. **Rúbrica/alcance:** solicitar o revisar guía docente definitiva y decidir si los 11 criterios de S01 deben completarse realmente en la primera fase del repositorio o si hay una **fase MVP transversal** con algunos criterios demostrativos. No reducir unilateralmente alcance. Registrar respuesta docente en #36.
2. **Criterio de priorización:** ejecutar primero los puntos con mayor brecha ponderada de S01 (LACP 0/10, IaC 1/10, L2 3/10, B4 0/5, release 0/5) y no sobreoptimizar B2-L3 17/18 o B3 10/15.
3. **Ciclo de trabajo:** para cada bloque, **precheck→una ejecución exitosa→verificación/rollback→captura obligatoria→commit/issue→siguiente bloque**. No volver a repetir pruebas por documentación si ya hay logs verificables.
4. **Uso de capturas:** imágenes B3_05–B3_14 **se consideran tomadas salvo aviso del operador, NO visualmente recibidas/auditadas**. Los primeros **24 PNG sí están publicados y auditados** en repositorio. Priorizar código funcional y luego incorporar siguiente lote de PNG cuando se reciba.
5. **Estado del host al empezar próximo bloque:** última salida 18:36 indicó puertos 9090/9108 libres, Docker/netns vacíos, red protegida y Git limpio respecto a `origin/main` de ese instante; nuevos commits GitHub hacen que el usuario tenga que ejecutar `git pull --ff-only origin main` antes de empezar.

## Qué NO afirma este plan

No compromete una fecha de recuperación sin conocer la evaluación real, capacidad de horas disponibles y criterios de la profesora. No otorga puntos de nota ni sustituye documentación académica. No presenta Alertmanager como integrado: **las alertas `firing` verificadas fueron del motor de Prometheus**, no notificaciones a destinatarios. Sin LAN clients/servicio, no se debe afirmar servicio final extremo a extremo en producción.
