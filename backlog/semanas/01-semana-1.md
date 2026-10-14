# S01 — MVP transversal y viabilidad: backlog vigente

**Plan interno inicial:** 5–11/10/2026. **Último corte técnico:** 13/10/2026 23:35 Panamá. **Estado S01:** ABIERTA; **72/100 puntos internos**, no nota de docente ni criterio aprobado. El desfase calendario y reparto de requisitos pendientes requieren confirmación de guía oficial en [#36](https://github.com/recm0708/netlab360/issues/36).

## Logros demostrados
- Base virtualizada operativa y segura; IPAM draft validado, tres sedes previstas con HQ–S1 bajo ensayo.
- VLAN 802.1Q, router-on-stick, ACL HTTP y HTTP de sedes por WAN dual probados en subtopologías separadas.
- FRR/OSPF Full y failover WAN-P→WAN-B→WAN-P, LACP 2→1→2, virtual active-backup.
- SoT/OpenTofu/Ansible→FRR B2 realmente usado, idempotencia y drift en copias.
- API/exporter, NOC inicial, scrape Prometheus y alertas firing/resueltas.
- Perfil B4 y reglas deterministas de 76 ICMP y 12 eventos en sesiones distintas; no ML evaluado.
- 86 PNG, siete CSV SHA, 24 pruebas Python, CI exitosa y host sin residuos.

## Criterios integrales NO cerrados
El issue [#1](https://github.com/recm0708/netlab360/issues/1) conserva once criterios originales, detallados con evidencia y brechas en [matriz canónica](../../docs/control/03-matriz-aceptacion-y-decisions-s01.md). Ningún criterio integral se aprueba por un solo componente de laboratorio. IaC avanzada aparece también en S03 y ML en S06; la rúbrica docente decidirá si se exige antes.

## Orden vigente
1. Definir estructura editorial definitiva y tres documentos maestros acumulativos S01–S08 en la plantilla institucional.
2. Redactar S01 de investigación, memoria técnica y manual con capturas seleccionadas y citas verificadas.
3. Obtener guía/rúbrica docente, definición exacta de entrega de S01, extensión y obligatoriedad de OVA/ML.
4. Cubrir sólo brechas técnicas exigidas por esa rúbrica, con una prueba integrada por criterio y pre/postcheck.
5. Sanitizar/validar exportación/reimportación de VM si obligatoria, versionar release y cerrar issues al cumplir requisitos.

**No comenzar fase S02 mientras el usuario no apruebe documentos y cierre S01.** Referencia [checkpoint](../../docs/REANUDAR-AQUI.md). Los relatos cronológicos antiguos siguen en Git y `docs/sesiones`.
