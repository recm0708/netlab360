# S01 — Prototipo inicial validado (registro de continuidad, 16/10)

**Período del plan interno original:** 5–11/10/2026. **Estado de issue #1:** ABIERTA por alcance integral pendiente, aunque los experimentos base están documentados. **72/100** corresponde a puntaje histórico de gestión, NO aceptación/nota docente ni criterio que bloquee S02.

## Funciones demostradas S01
- VM Ubuntu Desktop VMware/SSH/VMnet8 y red gestión protegida; hardening SSH servidor pendiente.
- IPAM HQ/S1 y S2 reservada, nueve VLAN previstas y WAN doble.
- VLAN/ACL intra-HQ; FRR/OSPF+HTTP HQ→S1 en otra topología con WAN-P→WAN-B→WAN-P.
- LACP 2→1→2 y active-backup virtual; no redundancia real de equipo/servidor ni benchmark capacidad.
- SoT→OpenTofu metadata→Ansible→FRR vivo, drift reconciliado en COPIAS candidatos.
- Exporter/NOC inicial y Prometheus con alertas firing/resueltas.
- B4 estadística/reglas sobre 76 ICMP + 12 eventos de sesiones diferentes, sin ML entrenado.
- 86 PNG/7 CSV SHA256, 24 tests/CI correctas; apagado ordenado de VM registrado.

## Norma docente y nueva política
Tres criterios académicos vigentes al 17/10: **UN informe escrito >=40 páginas** con 12 apartados, PowerPoint y demostración final. Código y configuraciones en anexos; ZIP externo autorizado junto con el informe. El manuscrito institucional S01 previo tiene 65 páginas y será **reorganizado**, no descartado. **Manual 02 diferido a después**.

## Camino para recuperar desfase
No bloquear S02 por manual ni por un Word inconcluso; S01 queda en seguimiento para requisitos transversales pendientes. [Plan reordenado S02–S08](../../docs/academico/02-plan-operativo-s02-s08-repriorizado.md). Próximo esfuerzo: integración real HQ–S1–S2, cliente VLAN→dos WAN→servicios, seguridad/monitoreo y casos de demo con baseline esperado/real. La transcripción futura definirá calendarios y límites.

**No repetir pruebas aprobadas por capturas ni reejecutar IaC destructivo.** Red de gestión ens33 .40/24/GW .2 intacta.


**Corte académico obligatorio durante el proyecto:** título al chat Teams, primera revisión **30/10/2026** (Introducción, Objetivos, Planteamiento), segunda revisión **13/11/2026** (Fundamento técnico y Diseño). Ambas muestran el **mismo borrador en Teams**, representante designado; no requieren diapositivas. ZIP de anexos externos autorizado con el informe, demo final EN VIVO. [Criterios aplicables](../../docs/academico/00-criterios-docentes-y-hitos.md).
