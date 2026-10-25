# NETLAB360 — Estado y puertas de cierre de las fases 1–3

**Corte de gestión:** 25 de octubre de 2026. **Rama operativa:** `main` exclusivamente. Esta matriz define criterios de aceptación **propios** de cada fase, separando ejecución técnica, evidencia publicada y cierre académico. Los porcentajes son indicadores internos, no calificaciones docentes.

## Estado comprobado

| Fase | Indicador | Estado técnico | Fotografías en main | Issue de control |
|---|---:|---|---:|---|
| 1: línea base | **72 % histórico** | Pruebas iniciales superadas y subtareas base cerradas; aceptar alcance fundacional | **90 PNG** | [#1](https://github.com/recm0708/netlab360/issues/1) ABIERTA |
| 2: integración multisede | **≈90 %** | **Núcleo técnico validado**, incluida VLAN→WAN→HTTP/ACL remota | **9 PNG** | [#2](https://github.com/recm0708/netlab360/issues/2) ABIERTA |
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

### Necesario antes de cerrar #2
- [ ] Sustituir **Figura 1** por topología definitiva HQ/S1/S2 en el borrador Word/PDF.
- [ ] Corregir referencias narrativas `S02` y «anexos» por **fase 2** y **TAR técnico externo**, cuando corresponda; verificar notas, preámbulos, tablas y figuras.
- [ ] Revisar nueva exportación del informe y registrar aceptación documental del núcleo S02.

**No bloquea S02:** LACP/capacidad multistream [#31](https://github.com/recm0708/netlab360/issues/31) en fase 5, NOC fase4, IA fase6 y entrega fase8. No recrear los escenarios para tomar fotografías. **Cierre previsto por condición:** una vez insertada Figura1 y validado el texto académico; no existe fecha de cierre independiente confirmada.

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
- [ ] **Informe:** incorporar 5.5 implementación de fase 3, capítulo 6 pruebas, capítulo 7 análisis y capítulo 8 conclusiones/recomendaciones, con limitaciones fieles al alcance real.
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
2. Incorporar la Figura1 y corregir el corte documental de S02; registrar su aceptación.
3. Redactar el corte de fase3, definir límites SoT/OpenTofu y revisar el Word/PDF; después aceptar S03.
4. Mantener al día la revisión docente **30/10** (Introducción/Objetivos/Planteamiento) y **13/11** (Fundamento/Diseño) sin marcarlas como celebradas antes de su ejecución.
5. Continuar fases 4–8 y preparar TAR final por separado cuando los módulos correspondientes estén validados.

**Criterio editorial:** documentación redactada como bitácora propia del proyecto, sin fórmulas de terceros que atribuyan el trabajo a interlocutores externos, sin alterar hechos. No hay anexos en Word; hay **TAR externo**.
