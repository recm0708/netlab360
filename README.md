# NETLAB360 — Plataforma Virtualizada de Redes Empresariales Multisede

**Control del proyecto actualizado: 17/10/2026.** En este repositorio se almacenan **solo instrucciones de trabajo adaptadas al proyecto, configuraciones, scripts, pruebas y evidencias PROPIAS de NETLAB360**. No publicar materiales recibidos de la profesora (guías, documentos, grabaciones ni transcripciones), ni archivos o hashes de esos materiales. [Criterios y calendario aplicables](docs/academico/00-criterios-docentes-y-hitos.md).

## Entrega semestral y fechas de control

- **Un solo informe académico-técnico de mínimo 40 páginas**, con 12 apartados en orden. [Índice maestro](docs/entregables/01-proyecto-investigacion-maestro.md). Borrador previo de 65 páginas del estudiante se reorganizará y ampliará, **sin recrearlo desde cero**.
- **Título propuesto en Teams**: enviar al chat de la asignatura y esperar aprobación/ajuste del docente. **Estado de envío/aprobación del grupo por confirmar**.
- **30/10/2026**: revisión grupal del borrador de **introducción, objetivo general y específicos, planteamiento del problema**. Mostrar **el documento en Teams**, sin PowerPoint especial. Designar un representante del grupo.
- **13/11/2026**: revisión grupal de **fundamento técnico y diseño de la solución**.
- **Anexos técnicos en archivo aparte AUTORIZADOS** junto con el informe. Se preparará ZIP de configuraciones/código/evidencias del proyecto con README, índice e integridad SHA256, excluyendo secretos y archivos ajenos. [Paquete de anexos](docs/academico/03-anexos-y-demostracion.md) · [#45](https://github.com/recm0708/netlab360/issues/45).
- **Presentación y demostración EN VIVO obligatoria** sobre infraestructura funcional, en fecha final aún no comunicada: PowerPoint derivado del informe, estados normal/falla/recuperación explicados. [#44](https://github.com/recm0708/netlab360/issues/44).
- **Manual técnico integral 02 POSPUESTO** para después de la entrega y funcionamiento; no es obligatorio ahora ni bloquea el plan. [#28](https://github.com/recm0708/netlab360/issues/28).
- **Parcial 1 / Laboratorio 5** es actividad individual distinta, hasta 25/10; se gestiona en **otro chat** y no se incorpora como obligación ni evidencia del semestral.

## Estado técnico comprobado S01

- VM Ubuntu Desktop en VMware NAT VMnet8; gestión `ens33 192.168.47.40/24`, GW `192.168.47.2`, SSH clave Ed25519 operativo; hardening `PasswordAuthentication yes` pendiente en #38.
- Inventario IPAM HQ/S1 y S2 reservada, nueve VLAN propuestas y doble WAN; VLAN/trunk/ACL HTTP de HQ comprobados en escenario aislado; FRRouting/OSPF/HTTP dual WAN HQ↔S1 comprobados en otra subtopología, WAN-P→WAN-B→WAN-P.
- LACP `2→1→2`, bonding active-backup virtual **sin equivalencia a NIC físicas o switches redundantes**.
- SoT/OpenTofu metadata→Ansible archivos FRR usados en B2; idempotencia/drift sobre copias de configuración **no sobre router activo**.
- NOC/exporter inicial y Prometheus alertas firing/resueltas; B4 76 ICMP y 12 eventos de sesiones distintas, reglas estadísticas **NO modelo ML entrenado**.
- 86 PNG planos, siete CSV con SHA256 de archivos propios de evidencias, 24/24 pruebas, CI exitosa. Ubuntu apagado de forma ordenada tras revisión de red, recursos y Git local limpio.

**S01** continúa abierta por criterios técnicos internos y no supone una calificación docente: 72/100 fue solo avance estimado histórico. **S02 puede comenzar**, priorizando la integración de **HQ–S1–S2 en un mismo escenario**, VLAN→servicio por doble WAN, OSPF failover y recuperación sin afectar ens33/VMnet8. [Plan reordenado](docs/academico/02-plan-operativo-s02-s08-repriorizado.md). Mantener actividades del escrito paralelas a las prácticas, garantizando la revisión del 30/10.

## Navegación

- [Punto de reanudación y próxima tanda de trabajo](docs/REANUDAR-AQUI.md).
- [Criterios docentes ya convertidos en pautas NETLAB360](docs/academico/00-criterios-docentes-y-hitos.md).
- [Reorganización del borrador institucional](docs/academico/01-migracion-borrador-a-formato-docente.md).
- [Plan S02–S08 reordenado](docs/academico/02-plan-operativo-s02-s08-repriorizado.md).
- [Informe único](docs/entregables/01-proyecto-investigacion-maestro.md).
- [Control de aceptación técnica S01](docs/control/03-matriz-aceptacion-y-decisions-s01.md).
- [Issues académicas abiertas](https://github.com/recm0708/netlab360/issues/36).

**Portada propuesta:** NETLAB360: Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede. **Encabezado Word:** `NETLAB360 | Redes Empresariales Multisede`. Título formal **sujeto a observaciones de la profesora**.
