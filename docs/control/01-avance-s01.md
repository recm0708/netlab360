# NETLAB360 — Control de avance y cierre de Fase S01

**Corte técnico actualizado:** 2026-10-13 11:24 (Panamá, UTC−05:00).  
**Versión de seguimiento:** v1.2. **Fase:** [#1](https://github.com/recm0708/netlab360/issues/1) **ABIERTA**.  
**Estado oficial de la rúbrica:** pendiente de ratificación con la docente. **Porcentaje provisional; no es nota, auditoría de cumplimiento oficial ni valor calculado por GitHub.**

## 1. Estimación ponderada del avance S01

Los pesos se asignan a las capacidades mínimas que aparecen en la issue #1 y en `docs/05-plan-operativo-y-pausas.md`. Se acredita solo lo comprobado en la VM, no la mera instalación de software ni el diseño no desplegado.

| Bloque de trabajo S01 | Peso | Puntos acreditados | Fundamento verificable |
|---|---:|---:|---|
| B0: infraestructura, SSH operativo, herramientas, snapshot y rollback base | 12 | **12** | VMware/Ubuntu/Docker/Git, VMnet8/IP fija, SSH con clave, reinicio y snapshot; cuestiones de hardening final en #38 pendientes |
| B1: topología e IPAM/SoT inicial | 10 | **8** | YAML draft validado, 3 sedes/9 VLAN/2 WAN previstas, sin solapamientos; diseño no desplegado/aprobado |
| B2-L2: VLAN/trunks/ACL de primer dominio | 10 | **3** | prueba VLAN 110/120 y retorno con Linux bridge; sin trunk real, inter-VLAN, ACL ni integración entre sedes |
| B2-L3: FRR/OSPF, WAN primaria/respaldo, convergencia y failover | 18 | **16** | FRR v5, dos routers y dos Full/OSPF por router, FIB WAN-P→WAN-B→WAN-P; 13/10 30/30 ICMP entre interfaces LAN simuladas, 0% pérdida en 3 estados, rollback; faltan pérdida/transitorio medidos durante fallo y hosts/servicios reales |
| Redundancia LAG/LACP, equipos, servidor dual-NIC | 10 | **0** | sin laboratorio implementado |
| IaC y compliance (OpenTofu + Ansible) | 10 | **1** | herramientas instaladas y operativas, sin automatización de la topología NETLAB360 |
| B3: telemetría/API/dashboard/alertas, eventos reales | 15 | **0** | no implementados |
| B4: anomalías/datos/IA evaluada | 5 | **0** | no existe prototipo con evaluación |
| Documentación académica, evidencia, CI/PR y regresión | 5 | **2** | bitácoras/logs/commits y capturas tomadas; faltan informe APA, manual, auditoría visual de PNG, CI, regresión integrada |
| B5: release y OVA sanitizada importada, SHA-256 | 5 | **0** | sin exportación, reimportación ni tag/release demostrable |
| **TOTAL** | **100** | **42** | **42% estimado, 58% pendiente** |

**Criterio de cálculo:** total de puntos acreditados / 100. Del 30% al 40% al comprobar doble OSPF Full/FIB/retorno, y **del 40% al 42%** por +2 puntos B2-L3 al acreditar **30/30 paquetes ICMP entre las LAN simuladas** en tres estados; no acreditar medición de pérdidas durante la transición. No confundir este indicador de avance físico-técnico con el cumplimiento **binario** del checklist de aceptación de #1: en la fecha de corte todavía no están cerrados los 11 criterios integrales de esa issue. Los avances parciales de cada dominio no cierran su criterio integral.

## 2. Estado de GitHub

Consulta del repositorio `recm0708/netlab360` realizada el 12/10/2026: **43 issues en total; 3 cerradas y 40 abiertas** después de abrir #43 para la auditoría de capturas.

**Issues cerradas y verificadas:**  
- [#39 — dirección fija en VMnet8](https://github.com/recm0708/netlab360/issues/39): `192.168.47.40/24`, fuera del pool DHCP, SSH y persistencia tras reinicio.  
- [#40 — GitHub CLI y clonación](https://github.com/recm0708/netlab360/issues/40): autenticación, Git HTTPS y sincronización de repositorio.  
- [#41 — herramientas base y snapshot](https://github.com/recm0708/netlab360/issues/41): Docker/IaC/herramientas y `NETLAB360-BASE-HERRAMIENTAS` confirmado por operador, reinicio/postcheck.

**Subhitos técnicos completados pero issues mayores aún ABIERTAS:**
- [#11 — IPAM y topología](https://github.com/recm0708/netlab360/issues/11): B1 YAML validador + pruebas sin conflictos; diseño `draft`.
- [#12 — PoC incidente observable](https://github.com/recm0708/netlab360/issues/12): B2-L2 prueba VLAN conexión/aislamiento/restauración funcional; falta incidente WAN + alarma.
- [#42 — FRRouting OSPF dual WAN](https://github.com/recm0708/netlab360/issues/42): FRR v5 **subprueba de arranque local** aprobada; **13/10 enrutamiento R-HQ/R-S1 con dos vecinos Full por router, failover a wan-b, retorno a wan-p y cleanup realizados exitosamente**, y **ping bidireccional 30/30 con LAN de routers** en los tres estados; sigue pendiente tráfico continuo durante corte, clientes reales y medición temporal estricta.
- [#16 — Source of Truth](https://github.com/recm0708/netlab360/issues/16): existe YAML IPAM inicial, falta inventario completo/consumo Ansible/OpenTofu.
- [#38 — Ubuntu y SSH seguro](https://github.com/recm0708/netlab360/issues/38): acceso por clave funciona; hardening/revisión y documentación formal pendientes.
- [#10 — inventario de recursos](https://github.com/recm0708/netlab360/issues/10) y [#34 — matriz versiones](https://github.com/recm0708/netlab360/issues/34): información sustantiva comprobada, quedan verificaciones de compatibilidad y cierre formal.

**Auditoría nueva:** [#43 — revisión visual de evidencias PNG](https://github.com/recm0708/netlab360/issues/43): abierta hasta recibir el lote y verificar su correspondencia con logs, fecha/hostname, comandos y resultados.

**No cerrar todavía:** [#1 S01](https://github.com/recm0708/netlab360/issues/1), #11, #12, #42, #38, #10, #34. Ninguna issue posterior de S02–S08 se cierra por resultados de smoke local.

## 3. Pendientes por bloque y secuencia recomendada

### B2 — Convertir la PoC local en red real aislada (prioridad inmediata)
1. **CONCLUIDO 13/10:** orquestador `scripts/laboratorio/b2-dualwan-ospf.sh` ejecutado sobre R-HQ/R-S1; aislamiento `--network none`, dos pares veth, `up/status/fail/restore/down` y cleanup exitosos, host ens33 intacto.
2. **CONCLUIDO 13/10:** WAN-P `10.78.0.0/30` OSPF costo 10, WAN-B `10.78.0.4/30` costo 100, loopbacks `10.79.0.1/32` y `.2/32` y LAN dummy HQ/S1 anunciadas en OSPF área 0; vecinos dos Full por router.
3. **CONCLUIDO 13/10, 11:24:** tráfico ICMP real entre IP LAN de R-HQ y R-S1 con orígenes `10.70.10.1`/`10.71.10.1`: 5/5 por dirección en los tres estados (normal, respaldo, restaurada), 30/30 y 0% pérdida en esos sondeos. **PENDIENTE:** medir pérdida y tiempo de convergencia durante el instante de falla con tráfico continuo; incluir clientes y servicios reales y una serie temporal.
4. Completar VLAN trunk/ACL mínimas y prueba de agregación/redundancia o someter recorte de alcance a rúbrica aprobada.

### B3/B4 — El MVP transversal exigido por S01
5. Exportar eventos reales de caída, reconvergencia, restauración a métricas con timestamp; integrar exporter/Prometheus, API y una vista NOC con alarma.
6. Incorporar OpenTofu y Ansible en recursos acotados de la topología (estado deseado, plan, comprobación, idempotencia).
7. Capturar un baseline de eventos y probar un prototipo de anomalía supervisado/no supervisado con métricas, evaluación y limitaciones. No atribuirle IA validada sin evaluación.

### B5 — Cierre formal de S01
8. Completar informe académico APA 7, bitácora y manual de usuario; revisar visualmente capturas PNG después de que el usuario las envíe; enlazar cada evidencia con fecha, comando, resultado y commit.
9. Confirmar con docente rúbrica definitiva y negociar cambios de alcance/calendario si procede; S01 estaba prevista para **5–11/10/2026** y a este corte sigue abierta.
10. Implementar CI local/PR adecuado sin ejecutar topologías privilegiadas en runners compartidos; generar etiqueta/release y exportación OVA **sanitizada** (revocar/borrar token CLI local antes de distribuir); comprobar checksum SHA-256 e importación en VM de prueba.

## 4. Política de control de evidencias y privacidad

El usuario indica que **todas las capturas solicitadas se asumen tomadas**, salvo que señale una excepción. Posteriormente remitirá PNG para revisión; **no afirmar que están visualmente aprobadas o subidas a GitHub**. Cada nueva captura debe tener nombre exacto, comando de presentación sin `clear`, marcadores `INICIO CAPTURA`/`FIN CAPTURA`, fecha/hostname y resultado literal. Preservar históricos fallidos como diagnóstico, no como prueba de éxito.

Nunca publicar tokens, claves privadas, credenciales, carpetas `~/.config/gh/hosts.yml` ni OVA no sanitizada. No alterar la red de gestión `ens33 192.168.47.40/24` ni VMware VMnet8 desde la topología de laboratorio.

**Evidencia ICMP de LAN simulada validada:** [bitácora de 30/30 pings](../sesiones/2026-10-13-b2-lan-icmp-tres-estados-verificado.md); logs locales `16-b2-lan-ping-{normal,respaldo,restaurada}-20261013-*.log`, captura B2_15 tomada según convención, auditoría visual pendiente. 

**Evidencia R-HQ/S1 dual-WAN validada:** [bitácora de failover](../sesiones/2026-10-13-b2-dualwan-ospf-failover-resultado.md), logs locales `15-b2-dualwan-{up,status,fail,restore,down}-20261013-*.log`, capturas B2_12–B2_14 presuntamente tomadas, aún no auditadas. 

**Evidencia FRR local exitosa:** `~/netlab360-bootstrap/evidencias/14-b2-frr-smoke-v5-20261012-235725.log`; [bitácora FRR v5](../sesiones/2026-10-12-smoke-frr-v5-exitoso.md).

**Actualizar este archivo y #1 cuando cambie una prueba funcional o el alcance oficial; no aumentar el porcentaje solo por escribir documentación o abrir issues.**
