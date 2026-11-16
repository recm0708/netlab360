> **AVISO VIGENTE 16/10/2026:** el `72/100` mostrado abajo es un **indicador interno histórico de avance de prototipo S01 (corte 13/10)**. **NO es nota, rúbrica oficial ni bloqueo para S02**. Las guías docentes recibidas el 16/10 exigen un **único informe escrito >=40 páginas, PPT/demostración y anexos**, NO un manual técnico aparte. La celda histórica «dos documentos» se conserva como dato de la matriz original pero queda **sustituida** por [guía oficial](../academico/00-criterios-docentes-y-hitos.md), [matriz adaptada](03-matriz-aceptacion-y-decisions-s01.md) y [plan de migración](../academico/01-migracion-borrador-a-formato-docente.md). No recalcular el 72% retroactivamente por recibir guías.

# NETLAB360 — Matriz ponderada de seguimiento S01

> **Control de issues y milestones (14/10):** 43 issues totales, 38 abiertas/5 cerradas, cero abiertas sin milestone, según [auditoría canónica](04-auditoria-issues-milestones-2026-10-14.md). #33 CI y #42 OSPF cerradas por pruebas específicas; sus cierres **no aumentan 72/100** ni acreditan aceptación de S01 integral. #38 SSH permanece abierta por hardening/rollback. Dos índices documentales aprobados, textos pendientes.


**Corte técnico:** 13/10/2026 23:35 Panamá. **Consolidación de control:** 14/10/2026. **Estado:** S01 ABIERTA; porcentaje interno, **no rúbrica docente**. Guía oficial y distribución S01–S08 pendientes de ratificación. [Matriz de 11 criterios](03-matriz-aceptacion-y-decisions-s01.md).

| Componente | Peso | Acreditado | Pendiente | Evidencia representativa / límite |
|---|---:|---:|---:|---|
| B0 Infraestructura VMware/Ubuntu, SSH, herramientas y snapshot | 12 | 12 | 0 | VM y VMnet8 operativas; hardening final de exportación pendiente |
| B1 Topología/IPAM Source of Truth | 10 | 8 | 2 | YAML válido sin solapamientos; diseño draft, S2 reservada |
| B2-L2 VLAN, trunks, ACL, HTTP | 10 | 8 | 2 | 802.1Q y router-on-stick HQ; aún sin unión a la topología WAN efectiva |
| B2-L3 FRR/OSPF, WAN primaria/respaldo, HTTP HQ–S1 | 18 | 18 | 0 | Dos Full por router y conmutación/restauración; no continuidad sin pérdida demostrada |
| Redundancia LACP/equipo/servidor | 10 | 6 | 4 | LACP 2→1→2 y active-backup virtual, no falla de equipo/VM dual NIC física |
| IaC y compliance OpenTofu/Ansible/FRR | 10 | 7 | 3 | Terraform_data metadatos, candidatos FRR aplicados a B2, idempotencia y drift de archivos; no drift FRR vivo |
| B3 telemetría/API/NOC/alertas | 15 | 10 | 5 | Exporter, Prometheus y alertas reales; no receptor/SLI/NOC multisede integral |
| B4 analítica IA evaluable | 5 | 0 | 5 | Perfil + reglas descriptivas reales, sin entrenamiento/evaluación ML |
| Documentación/evidencias/CI | 5 | 3 | 2 | 86 PNG y 7 CSV SHA, tests/CI aprobadas; dos documentos maestros aún sin redacción final |
| B5 Release/exportación VM/OVA | 5 | 0 | 5 | No tag/release ni exportación/reimportación verificadas |
| **Total** | **100** | **72** | **28** | **S01 NO CERRADA** |

## Control de evidencias verificadas
- Capturas 86 PNG originales aplanados; 7 CSV; validador final `AUDITORIA_CAPTURAS_PLANAS=OK`.
- Commit de lote06 `b410548f9338233c8dc23816ce78a11d67bb2896`; SHA local/remoto iguales después de push.
- CI GitHub Actions [38511477595](https://github.com/recm0708/netlab360/actions/runs/38511477595) exitosa, suite local de 24 pruebas.
- Cuatro resúmenes IaC 01/03/04/06 recuperados de logs originales con códigos cero; fotos nuevas no recibidas. Postcheck lote06 adicional recibido en chat; falta publicación.
- Último control host: 13/10 23:35:02, Docker/netns vacíos, gestión `ens33 192.168.47.40/24`, GW `192.168.47.2`, servicios activos.

## Políticas de cómputo y cierre
- **No incrementar** por preparar scripts sin ejecutarlos, por un Word no final, por fotos ya acreditadas ni por repetir CI verde.
- El motor por reglas de B4 no satisface ML supervisado/no supervisado evaluable; sin etiquetas independientes no se calcularán precision, recall, F1.
- La puntuación interna sirve para priorizar, **no prueba** aceptación de los 11 criterios integrales de S01. No modificar condiciones de S01 para simular cierre.
- La línea base de documentación es [dos maestros consolidados](../entregables/00-politica-editorial-y-entrega-acumulativa.md), redactados por secciones en la plantilla institucional del usuario y APA7; el Documento 01 recoge incidentes técnicos reales y el Documento 02 soluciones preventivas posibles.
- Resolver con docente las actividades inter-fase (OpenTofu avanzado S03, dataset/ML S06, OVA final S08) en [#9](https://github.com/recm0708/netlab360/issues/9) y [#36](https://github.com/recm0708/netlab360/issues/36).

**Archivo histórico:** los progresos anteriores de 30%, 43%, 53%, 63%, 68%, 71% y 72%, junto a su cronología detallada, permanecen consultables en Git, comentarios de issues y `docs/sesiones/`. Este documento deliberadamente NO apila encabezados con estados contradictorios.
