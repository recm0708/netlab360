# NETLAB360 — Informe académico de la fase S01

**Estado:** Borrador técnico-académico V0.1, no entregable final. **Asignatura:** Tópicos Especiales II. **Título provisional:** Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico inteligente de redes empresariales multisede. **Autores, docente, grupo y fecha oficial:** pendientes de confirmar. **Corte de resultados:** 13 de octubre de 2026.

## Resumen
NETLAB360 es un laboratorio virtualizado orientado a simular componentes de una red empresarial multisede sobre una única máquina Ubuntu Desktop en VMware Workstation. La fase inicial combina inventario de direcciones IP, segmentación mediante VLAN 802.1Q, routing dinámico FRRouting/OSPF con dos WAN, pruebas de redundancia de enlaces virtuales, automatización con OpenTofu y Ansible, y observabilidad con un exportador y Prometheus. Las pruebas confirmaron rutas primaria–respaldo–principal, tráfico HTTP en los tres estados estables, configuraciones FRRouting obtenidas de Ansible y alertas de WAN disparadas y resueltas. El análisis de 76 sondeos ICMP y 12 eventos de otras sesiones permitió caracterizar el comportamiento sin confundir reglas estadísticas con IA entrenada. Quedan pendientes la integración completa de subtopologías, la evaluación ML independiente y la distribución verificada de la VM.
**Palabras clave:** multisede, FRRouting, OSPF, infraestructura como código, observabilidad, redes virtualizadas, AIOps.

## 1. Introducción y problema
La operación de redes multisede requiere coordinación entre segmentación, enrutamiento, disponibilidad, configuración y diagnóstico. Los laboratorios separados por tecnología dificultan demostrar un ciclo operativo completo y repetible. NETLAB360 busca integrarlos en un entorno controlado, preservar evidencias y aislar las fallas de la red utilizada para administrar la VM.

**Pregunta orientadora:** ¿Qué capacidades de una red multisede —segmentación, conmutación WAN, automatización y observabilidad— pueden demostrarse de forma reproducible y segura mediante un MVP virtualizado?

## 2. Objetivos
**General:** diseñar y verificar un MVP de plataforma de laboratorio de redes multisede con automatización, observabilidad y recuperación controlada.

**Específicos:** (a) elaborar IPAM/Source of Truth HQ–S1 con S2 reservada y redes sin conflictos; (b) validar VLAN, troncales y ACL aplicadas a servicios; (c) comprobar FRR/OSPF por WAN principal y respaldo; (d) generar y utilizar configuraciones derivadas de OpenTofu/Ansible; (e) evidenciar métricas y alertas reales; (f) estudiar señales diagnósticas conservando límites metodológicos; (g) asegurar trazabilidad, integridad y limpieza de recursos.

## 3. Metodología
Se aplicó prototipado incremental por bloques B0–B4: precheck, escenario aislado, prueba positiva/negativa, registro de salida, recuperación y postcheck. Se emplearon namespaces Linux, contenedores Docker sin conectividad a la red administrativa de pruebas y fuentes de configuración versionadas. Los indicadores se interpretan dentro del alcance del instrumento: una adyacencia OSPF Full no mide disponibilidad de aplicación, y un muestreo ICMP no demuestra continuidad absoluta entre muestras.

## 4. Entorno y arquitectura
VMware Workstation Pro 26H1u1; Ubuntu Desktop 26.04.1 LTS, 8 vCPU, 16 GB RAM y disco virtual de 160 GB. La administración utiliza la interfaz ens33, 192.168.47.40/24, con gateway 192.168.47.2 en VMnet8 NAT, protegida frente a intervenciones del laboratorio. Inventario YAML: tres sedes previstas, nueve VLAN y dos WAN; HQ y S1 activas en los ensayos, S2 reservada. Enlaces WAN: 10.78.0.0/30 con costo OSPF 10 y 10.78.0.4/30 con costo 100. Los módulos L2, WAN, LACP y active-backup corresponden por ahora a topologías de prueba separadas; no deben presentarse como una sola malla persistente.

## 5. Implementación y resultados
**B1 y B2-L2.** El validador IPAM no encontró solapamientos. Una troncal 802.1Q interconectó dos VLAN dentro de HQ. El router-on-a-stick permitió HTTP inter-VLAN; antes de la ACL respondían 8080 y 8081; tras nftables, 8080 permaneció permitido y 8081 fue bloqueado aunque el servicio seguía activo.

**B2-L3.** R-HQ y R-S1 alcanzaron dos vecinos OSPF Full por router. La FIB utilizó WAN-P, cambió a WAN-B al bajar el enlace primario y regresó a WAN-P al restaurarlo. Un cliente de HQ y un servicio HTTP de S1 respondieron en los tres estados estables. En una sesión de convergencia se registraron 76 sondeos ICMP exitosos; ello no certifica cero interrupciones entre sondeos.

**Redundancia virtual.** Se observó LACP IEEE 802.3ad con agregador 2→1→2 miembros activos y HTTP funcional en los estados de prueba. Otro ensayo validó bonding active-backup virtual. No se probaron switches físicos duplicados, NIC físicas adicionales de VMware ni failover de servidor completo.

**IaC.** OpenTofu 1.13.1 registró cinco recursos declarativos internos y produjo un manifiesto; Ansible core 2.20.1 generó archivos candidatos FRRouting, resultaron COMPLIANT y su segunda ejecución tuvo changed=0. Una copia con costo OSPF alterado fue detectada como NON_COMPLIANT y restaurada por Ansible. Las configuraciones generadas se utilizaron para levantar FRR y verificar OSPF y failover. No se probó reconciliación de drift sobre FRR vivo.

**B3 observabilidad.** Un exportador expuso eventos y métricas de la WAN. Prometheus 3.7.0 realizó scrape válido, cargó tres reglas y mostró WANPrimaryDown y WanBackupSelected en estado firing durante el incidente; tras la restauración quedaron cero alertas WAN activas. Alertmanager con recepción externa y NOC multisede integral siguen pendientes.

**B4 analítica.** Se auditaron 76 observaciones ICMP y 12 eventos JSONL de otras sesiones. El perfil registró cero pérdidas y cero discrepancias FIB estables. Tres reglas deterministas sobre ICMP, FIB y RTT identificaron cero señales y cuatro transiciones operativas; umbrales RTT 0.147 y 0.245 ms fueron exploratorios, basados en la misma sesión. No existe modelo ML entrenado ni precision, recall o F1 válidos.

**Trazabilidad.** En el corte final, 86 capturas PNG y siete CSV constan en carpetas planas del repositorio, integridad SHA-256 OK, commit de publicación b410548 y Git local/remoto sincronizados. Se ejecutaron 24 pruebas unitarias y GitHub Actions verificó la regresión offline con éxito.

## 6. Discusión y limitaciones
Los ensayos demuestran viabilidad funcional de segmentos del MVP, pero no todos los criterios integrales: topologías L2 y WAN no enlazadas en un único ciclo persistente, redundancia física no ensayada, detector IA no evaluado, falta integración final de alarmas con receptor, y exportación/reimportación de VM no comprobadas. La matriz 72/100 es una estimación interna, no una nota ni aceptación docente.

## 7. Conclusiones preliminares
Se logró preservar la gestión mientras se probaron fallas virtuales; se verificó el failover de rutas OSPF y respuestas HTTP; se conectó un Source of Truth con OpenTofu/Ansible y FRR; y se demostraron alertas activas/resueltas de WAN. El bloque analítico aún requiere múltiples sesiones y etiquetas independientes para evaluar ML.

## 8. Requisitos de edición final
Completar portada institucional, autores, docente, figura de topología y figuras con pie, referencias APA 7 verificadas, criterios docentes de S01 y resultado de release/OVA si aplica. No inventar bibliografía ni declarar la fase cerrada antes de cumplir la rúbrica.
