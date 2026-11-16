> **NORMA DOCENTE POSTERIOR, 16/10/2026:** esta matriz se conserva como **inventario histórico de dependencias S01**. Toda referencia a «dos documentos maestros» ya fue sustituida: la profesora exige **UN informe final >=40 páginas** y PPT+demostración; Manual 02 pospuesto. Fuente normativa actual: guía 1457. Las versiones de herramientas mostradas son las observadas al corte técnico y requieren nueva verificación cuando se reinicie la VM.

# NETLAB360 — Matriz vigente de dependencias S01

**Actualizada 14/10/2026.** Inventario del ambiente comprobado al 13/10. No instalar dependencias preventivas para S02–S08 ni introducir nuevas tecnologías mientras se redacta S01.

| Subsistema | Herramienta o entorno | Estado conocido | Limitación/próxima decisión |
|---|---|---|---|
| Gestión | Ubuntu Desktop 26.04.1, SSH, VMware Tools, Git/GitHub | Funcional, ens33 192.168.47.40/24, gateway .2 | Sanitizar y revisar permisos antes de OVA |
| Contenedores | Docker Engine, namespaces Linux, iproute2, bonding | Verificados, sin recursos residuales postcheck | No equivale a infraestructura física redundante |
| Routing | imagen FRRouting 10.7.1 y OSPF | Full por ambas WAN y failover comprobados | Integrar L2/servicio en escenario único si rúbrica exige |
| Switching/ACL | bridge, 8021q, nftables, curl | VLAN, trunk y ACL HTTP funcionales | Topología aislada intra-HQ |
| IaC | OpenTofu v1.13.1, Ansible core 2.20.1 | Manifiesto/archivos candidatos y uso FRR real; compliance archivos | Ownership y reconciliación live pendiente |
| Observabilidad | exporter Python, API HTTP, Prometheus 3.7.0 | Scrape/TSDB y dos alertas firing/resueltas observadas | Alertmanager receptor/NOC multisede final pendientes |
| Analítica | Python 3.14.4, numpy disponible | JSON de 76 sondeos y 12 eventos distintos, reglas/estadística ejecutadas | sklearn/pandas/matplotlib no instalados al corte; ML no evaluada |
| Pruebas/CI | unittest y GitHub Actions Node24 | 24 tests locales, run 38511477595 success | No prueba fallas integrales del hipervisor |
| Documentos | Dos índices maestros Markdown + Word institucional del usuario | Política 2 documentos e índices propuestos, pendientes de aprobación | Redacción APA 7 de S01 pendiente |

## Antes de futuras operaciones de red
1. Confirmar snapshot de la VM e intención del ensayo.
2. Revisar git status y pull ff-only sin sobrescribir cambios.
3. Comprobar Docker, ip netns, ens33 y gateway antes de lanzar B2.
4. Ejecutar pruebas exclusivamente en recursos aislados y registrar salida/retorno.
5. Cerrar con down/rollback específico; no limpiar recursos ajenos.
6. Comprobar red administrativa, servicios, evidencias y Git al terminar.

**Estado actual:** no se requieren paquetes nuevos ni pruebas de red para elaborar los documentos académicos S01. No afirmar que faltaba Prometheus: fue validado en la sesión del 13/10 18:29–18:36. Bitácora.
