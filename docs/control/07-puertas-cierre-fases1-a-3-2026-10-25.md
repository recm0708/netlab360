# NETLAB360 — Estado y puertas de cierre de las fases 1–3

**Corte de gestión:** 25 de octubre de 2026. **Actualización del cierre académico:** borrador 3.2 revisado (94 páginas); fase 2 cerrada internamente y fase 3 pendiente de decisión de alcance. **Rama operativa:** `main` exclusivamente. Esta matriz define criterios de aceptación **propios** de cada fase, separando ejecución técnica, evidencia publicada y cierre académico. Los porcentajes son indicadores internos, no calificaciones docentes.

## Estado comprobado

| Fase | Indicador | Estado técnico | Fotografías en main | Issue de control |
|---|---:|---|---:|---|
| 1: línea base | **72 % histórico** | Pruebas iniciales superadas y subtareas base cerradas; aceptar alcance fundacional | **90 PNG** | [#1](https://github.com/recm0708/netlab360/issues/1) ABIERTA |
| 2: integración multisede | **100 % de sus criterios de cierre propios** | **Núcleo técnico y documentación de fase validados**: WAN, VLAN, HTTP/ACL, conmutación, Figura 1 | **9 PNG** | [#2](https://github.com/recm0708/netlab360/issues/2) CERRADA |
| 3: automatización y GitOps | **≈90 %** | Ansible real, metadatos OpenTofu y CI/PR **validados** | **8 PNG** | [#3](https://github.com/recm0708/netlab360/issues/3) ABIERTA |

**Inventario:** 107 PNG definitivas clasificadas (90/9/8); 21 nuevas por [PR #53](https://github.com/recm0708/netlab360/pull/53), [regresión postmerge SUCCESS](https://github.com/recm0708/netlab360/actions/runs/40241580823), [auditoría #51](https://github.com/recm0708/netlab360/issues/51) CERRADA. Los siete manifiestos históricos y la integridad SHA-256 del lote se conservan. La evidencia GitOps S03_09 es **Markdown verificable**, no PNG.

## Puerta S01 — Línea base

### Aprobado
- [x] VMware/Ubuntu Desktop, presupuesto de VM, NAT y conectividad SSH por clave (sin afirmar endurecimiento completo del servidor).
- [x] IPAM inicial y topología diseñados; [#11](https://github.com/recm0708/netlab360/issues/11) cerrada.
- [x] Prototipo FRR/OSPF doble WAN, VLAN/ACL inicial, LACP virtual y pruebas de conmutación.
- [x] Evento observable y Prometheus firing/resolved como **PoC**, sin atribuir dashboard final ni Alertmanager; [#12](https://github.com/recm0708/netlab360/issues/12) cerrada.
- [x] Evidencias de fase 1 clasificadas: 90 PNG y manifiestos conservados.

### Necesario antes de cerrar #1
- [ ] **SSH seguro:** inspeccionar `sshd -T` y decidir endurecimiento/rollback con acceso alterno; [#38](https://github.com/recm0708/netlab360/issues/38).
- [ ] **Compatibilidad fundacional:** registrar estado firmware/boot/ISO origen como comprobado o limitación explícita sin reinstalar VM; [#34](https://github.com/recm0708/netlab360/issues/34).
- [ ] **Acta de aceptación de línea base:** documentar alcance realmente probado, límites y traslado de capacidades a fases posteriores, sin reclamar que la matriz de 72/100 equivalga al 100 % técnico.

**No bloquea la fase 1:** SoT `candidate` (fase 3, [#16](https://github.com/recm0708/netlab360/issues/16)), NOC central (fase 4), LACP multistream/SDN (fase 5), IA (fase 6), exportación OVA opcional/entrega (fase 8). No aumentar artificialmente el 72 % histórico al cerrar una subissue.

## Puerta S02 — Infraestructura multisede

### Aprobado
- [x] FRR tres routers, cuatro WAN OSPF con Full 4/2/2, FIB 6/6 y conectividad 6/6; [#13](https://github.com/recm0708/netlab360/issues/13) cerrada.
- [x] Falla/restauración independiente S1/S2, respaldo y retorno; [#14](https://github.com/recm0708/netlab360/issues/14) cerrada.
- [x] Tres switches y nueve VLAN: 9/9 gateways, 6/6 ICMP.
- [x] Cliente HQ VLAN110 `10.70.10.10` → S1 VLAN220 `10.71.20.20`, HTTP 8080 permitido y ACL 8081 denegada con dos paquetes/120 bytes; [#30](https://github.com/recm0708/netlab360/issues/30) cerrada tras cotejo de bitácora.
- [x] Postcheck/teardown seguros, gestión `ens33` intacta, regresión offline.
- [x] Capturas definitivas S02_01–S02_09 en GitHub con hashes.

### Condiciones de cierre #2 — verificadas en borrador 3.2
- [x] **Figura 1** de topología definitiva HQ/S1/S2 insertada en capítulo 4, página 25.
- [x] Referencias narrativas/«anexos», Tablas 5–6 y redacción por fases actualizadas; el material técnico se entrega en **TAR independiente**.
- [x] Versión **3.2 del PDF** (94 páginas) revisada: implementación 5.4, pruebas 6.3–6.5, análisis y conclusiones congruentes con las evidencias de fase 2.
- [x] **Cierre interno** del alcance S02 mediante [#2](https://github.com/recm0708/netlab360/issues/2). La revisión docente futura no se declara celebrada.

**No bloquea S02:** LACP/capacidad multistream [#31](https://github.com/recm0708/netlab360/issues/31) en fase 5, NOC fase4, IA fase6 y entrega fase8. No recrear los escenarios para tomar fotografías. **Cierre efectuado al comprobar la documentación 3.2.** Quedan ajustes tipográficos generales del informe único en [#27](https://github.com/recm0708/netlab360/issues/27), sin actividades técnicas S02 pendientes.

## Puerta S03 — SoT, Ansible, OpenTofu y GitOps

### Aprobado
- [x] SoT de 3 sedes, 9 VLAN y 8 extremos WAN contrastado con FRR vivo.
- [x] Ansible audita 8/8 costos OSPF, detecta drift 100→150 y reconcilia 150→100, seguido de `changed=0`; [#18](https://github.com/recm0708/netlab360/issues/18) cerrada.
- [x] OpenTofu: 17/17 **metadatos** `terraform_data` con `apply` de 17 adiciones, manifiesto 3/4/9 y segundo plan sin cambios. State externo al repositorio.
- [x] GitHub Actions declarativa y regresión general, PR #49 y CI verde, ciclo GitOps técnico cerrado en [#19](https://github.com/recm0708/netlab360/issues/19).
- [x] Regresión Ubuntu 29/29 S02, 87/87 general; gestión administrativa intacta.
- [x] S03_01–08 PNG y S03_09 Markdown auténticas/versionadas.

### Necesario antes de cerrar #3
- [ ] **Contrato SoT:** formalizar uso `source_status=candidate`, propiedad de los cambios y límites del origen de datos; [#16](https://github.com/recm0708/netlab360/issues/16).
- [ ] **Decisión OpenTofu:** el objetivo original incluía data sources y ownership de infraestructura externa; los 17 `terraform_data` **no lo cumplen**. Resolver si se amplía con prueba real o se documenta explícitamente su reducción/reprogramación; [#17](https://github.com/recm0708/netlab360/issues/17).
- [x] **Informe 3.2:** implementación en 5.5, pruebas 6.7–6.8, análisis capítulo 7, conclusiones/recomendaciones capítulo 8 y Figuras 12–15 contrastadas con evidencias reales.
- [ ] Revisar versión exportada y registrar aceptación/transición a fase 4.

**No bloquea S03:** completar NOC S04, SDN S05, ML S06 o TAR S08. **No repetir** inyección de drift, `tofu apply`, arranque/desmontaje S02 ni PR artificial.

## Reorganización de issues y ramas al corte

- Tareas técnicas cerradas por resultados verificados: [#10](https://github.com/recm0708/netlab360/issues/10), [#11](https://github.com/recm0708/netlab360/issues/11), [#12](https://github.com/recm0708/netlab360/issues/12), [#13](https://github.com/recm0708/netlab360/issues/13), [#14](https://github.com/recm0708/netlab360/issues/14), [#18](https://github.com/recm0708/netlab360/issues/18), [#19](https://github.com/recm0708/netlab360/issues/19) y [#30](https://github.com/recm0708/netlab360/issues/30).
- Issues redundantes cerradas por consolidación: [#9](https://github.com/recm0708/netlab360/issues/9) → [#36](https://github.com/recm0708/netlab360/issues/36); [#37](https://github.com/recm0708/netlab360/issues/37) → [#29](https://github.com/recm0708/netlab360/issues/29).
- NOC [#15](https://github.com/recm0708/netlab360/issues/15) reasignado a fase 4; LACP avanzado [#31](https://github.com/recm0708/netlab360/issues/31) a fase 5. Versiones transversales #34, evidencia futuras #43, entrega TAR #45 y OVA condicional #29 se administran en fase 8.
- Cinco ramas antiguas provenientes de PR ya fusionados se eliminaron mediante [workflow controlado](https://github.com/recm0708/netlab360/actions/runs/40242595670) **SUCCESS**. Se retiró el workflow de una sola ejecución y se agregó [autolimpieza de ramas tras merge](https://github.com/recm0708/netlab360/blob/main/.github/workflows/limpiar-rama-tras-merge.yml).
- El repositorio conserva **solo `main`**. Las issues de fases posteriores y revisiones académicas siguen abiertas conforme a trabajo futuro legítimo; una lista sin issues abiertas no sería fiel al estado del proyecto.

## Orden operativo recomendado

1. Completar revisión de seguridad SSH y registro de compatibilidad de la línea base para cerrar S01 sin interferir con WAN/FRR.
2. **Fase 2 aceptada y cerrada**: preservar su documentación y evitar reconstrucciones innecesarias.
3. **Fase 3 en revisión de alcance**: formalizar SoT `candidate` (#16) y decidir requisito de data sources/ownership externos de OpenTofu (#17); no describir los 17 metadatos como aprovisionamiento real.
4. **Pulido transversal del Word:** corregir coma de la página 7, sangría de 6.5 en el índice y espaciado excesivo de las notas de Figuras 12–15 y Tabla 12; conservar en #27.
4. Mantener al día la revisión docente **30/10** (Introducción/Objetivos/Planteamiento) y **13/11** (Fundamento/Diseño) sin marcarlas como celebradas antes de su ejecución.
5. Continuar fases 4–8 y preparar TAR final por separado cuando los módulos correspondientes estén validados.

**Criterio editorial:** documentación redactada como bitácora propia del proyecto, sin fórmulas de terceros que atribuyan el trabajo a interlocutores externos, sin alterar hechos. No hay anexos en Word; hay **TAR externo**.
