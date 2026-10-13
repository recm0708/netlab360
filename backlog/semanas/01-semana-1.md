# S01 — Semana 1: MVP transversal y viabilidad

**Calendario previsto:** 5–11 de octubre de 2026.  
**Corte de situación actualizado:** 13 de octubre de 2026, 11:24 Panamá.  
**Estado de fase:** ABIERTA, con retraso respecto al plan inicial; no trasladar automáticamente fechas de S02–S08.  
**Issue:** [#1](https://github.com/recm0708/netlab360/issues/1).  
**Avance estimado:** **42%** según pesos y evidencias de [docs/control/01-avance-s01.md](../../docs/control/01-avance-s01.md). No es avance oficial de GitHub ni calificación de docente.

## Criterios integrales de aceptación (copiados de issue #1; sin aprobar aún)

- [ ] HQ y una sucursal: VLAN, FRR/OSPF, WAN redundante, respaldo de equipo y servicio comprobable.
- [ ] LAG dos puertos con extremos compatibles; host dual-NIC; Source of Truth, prueba OpenTofu y verificación Ansible.
- [ ] API/dashboard con incidente realmente observado, métrica, alarma y timestamps.
- [ ] Prototipo evaluable de anomalías scikit-learn, diferenciado de reglas y sin presentarlo como IA validada.
- [ ] Borradores informe APA, bitácora técnica y manual, con evidencias.
- [ ] Ejecutar precheck/postcheck y documentar recuperación y pruebas reproducibles integrales.
- [ ] Integrar red, automatización, observabilidad, analítica, dashboard y documentación.
- [ ] Conservar capturas con fecha/hora, versión/commit y resultado observable, auditadas.
- [ ] Actualizar los tres documentos y registrar compatibilidad y límites técnicos.
- [ ] Identificar commit/PR y crear tag/release demostrable.
- [ ] Validar exportación y reimportación de la VM sanitizada, con SHA-256.

**Interpretación:** ningún criterio integral se puede marcar completado por una prueba de factibilidad aislada. Las casillas no son porcentaje de trabajo ni calificación.

## Bloques del plan operativo

| Bloque | Estado | Avance comprobable |
|---|---|---|
| B0 — Base Ubuntu/VMware/VMnet8/SSH/GitHub/Docker/snapshot | **Cerrado a nivel operacional** | Issues [#39](https://github.com/recm0708/netlab360/issues/39), [#40](https://github.com/recm0708/netlab360/issues/40), [#41](https://github.com/recm0708/netlab360/issues/41) cerradas; hardening/documentos de #38 abiertos |
| B1 — Diseño multisede/IPAM y SoT inicial | **Validación preliminar completa, diseño draft** | IPAM 3 sedes, 9 VLAN, 2 WAN sin solapamientos; #11 y #16 abiertos |
| B2-L2 — Primer experimento de segmentación | **Subprueba terminada** | VLAN 110 conectividad, aislamiento VLAN 120 y recuperación, código 0; faltan trunks/ACL #30 |
| B2-L3 — Plano de control FRR en contenedor aislado | **Subprueba terminada** | `FRR_DAEMONS_ACTIVOS: SI`, `OSPF_CONTROL_PLANE: OK`, `RESULTADO_SMOKE_FRR_V5=0`; base de despliegue #42 |
| B2 red dual-WAN e incidente | **Red y failover probados; observabilidad pendiente** | R-HQ/R-S1 Full/Full, WAN-P→WAN-B→WAN-P, **30/30 ICMP entre IP LAN de routers en tres estados (0% pérdida)**, rollback 0. Falta medir pérdida *durante* cambio, hosts finales y evento visible/alarma #42/#12 |
| B3 observabilidad/API/NOC | **Por hacer** | Métricas, timestamps y alarma #15/#20/#21 |
| B4 IA/anomalía | **Por hacer** | Dataset, baseline y prototipo evaluado #25/#26 |
| B5 cierre | **Por hacer** | CI/PR, informe/manual/evidencias, release y OVA verificada #35/#36/#43/#29 |

## Evidencia y continuidad

- Bitácora de conectividad LAN dual-WAN: [30/30 ICMP y rollback](../../docs/sesiones/2026-10-13-b2-lan-icmp-tres-estados-verificado.md); logs originales en `~/netlab360-bootstrap/evidencias/16-b2-lan-ping-*.log`, captura B2_15 considerada tomada, pendiente de auditoría #43.
- Bitácora FRR v5: [resultado completo](../../docs/sesiones/2026-10-12-smoke-frr-v5-exitoso.md), registro original local `~/netlab360-bootstrap/evidencias/14-b2-frr-smoke-v5-20261012-235725.log`.
- Todas las capturas indicadas por el asistente **se consideran tomadas por instrucción del usuario**, salvo que anuncie lo contrario. Todavía no están cotejadas visualmente en conjunto; control en [#43](https://github.com/recm0708/netlab360/issues/43). Se distinguen imágenes diagnósticas v1–v4 de FRR de `B2_10_Arranque_FRR_V5_Verificado.png`.
- Próximo subhito: desplegar dos routers aislados con FRR, veth primario/respaldo, OSPF área0, anunciar LANs, demostrar failover y limpiar sin modificar `ens33 192.168.47.40/24`.
- Usuario confirmó snapshot `NETLAB360-BASE-HERRAMIENTAS`; **no volver a solicitarlo**. No incluir tokens del CLI de GitHub ni secretos en Git/OVA.
- La rúbrica definitiva y cualquier recorte/reprogramación necesitan confirmación docente, documentada en #9/#36.

**No cerrar [#1](https://github.com/recm0708/netlab360/issues/1) hasta verificar todos los criterios o registrar un alcance corregido aceptado.**
