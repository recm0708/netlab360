# NETLAB360 — Estado del proyecto al 17/10/2026

## Compromisos docentes convertidos en plan
- Entregable: **un único informe académico-técnico de al menos 40 páginas**, y posteriormente PowerPoint con demostración **en vivo**.
- **Título propuesto a revisar en chat Teams**: verificar envío/aceptación (no afirmarlos sin confirmación).
- **30/10/2026:** revisión grupal del documento con introducción, objetivos y planteamiento del problema; muestra en Teams por representante, sin PPT para la revisión.
- **13/11/2026:** revisión de fundamento técnico y diseño de solución.
- Anexos de código y configuraciones **AUTORIZADOS en archivo separado junto al informe**; preparar ZIP solo de artefactos NETLAB360, con integridad SHA256 y sin secretos.
- [Criterios docentes aplicables sin materiales originales](academico/00-criterios-docentes-y-hitos.md). No almacenar archivos o hashes de material de clase en este repositorio.
- Manual técnico separado #28 difiere hasta después del proyecto; parcial individual/laboratorio 5, plazo 25/10, se trabaja en otro chat.

## Estado técnico
S01 issue #1 abierta por pendientes integrales; 72/100 interno antiguo no es nota ni cierre. VMware Ubuntu/ens33 .40/24 y GW .2 funcionando; SSH con claves pero `passwordauthentication yes` requiere hardening seguro; IPAM HQ/S1 (S2 reservada), pruebas aisladas VLAN/ACL y FRR/OSPF+HTTP dual WAN, LACP y bonding virtuales, IaC a FRR con drift de copias, Prometheus/NOC inicial, analítica por reglas B4 sin ML evaluado. 86 PNG y 7 CSV SHA256 **del proyecto**, 24 pruebas/CI exitosa.

El Ubuntu se apagó desde el SO por comando tras verificar Docker/netns vacíos y gestión preservada; control VMware Powered Off no visto directamente. **GitHub ahora tiene nuevos commits no descargados al Ubuntu hasta nuevo pull.**

## Prioridades
1. Confirmar entrega del título en Teams.
2. Preparar borrador para **30/10** desde documento institucional existente, sin borrar 65 páginas: seleccionar las secciones solicitadas, reorganizar índice solo cuando sea oportuno.
3. Integrar HQ–S1–S2 en S02; generar pruebas reproducibles aptas para demo en vivo y enriquecer el informe en paralelo.
4. Preparar y revisar fundamento/diseño para **13/11**.
5. Ensayos completos, cierre técnico, ZIP anexos, informe final y PPT/demo; manual después.

[Reanudar](REANUDAR-AQUI.md) · [Plan S02–S08](academico/02-plan-operativo-s02-s08-repriorizado.md).
