# NETLAB360 — Matriz de aceptación del núcleo S02 y traslado al informe académico

**Corte:** 24/10/2026, después de restaurar conexión HTTPS y Git en Ubuntu. **Estado:** VALIDACIÓN FUNCIONAL HISTÓRICA APROBADA; **ACEPTACIÓN DOCUMENTAL ABIERTA**. No es un certificado de despliegue en ejecución después del reinicio.

## 1. Resultado técnico previamente comprobado

| ID de prueba | Criterio | Resultado real reportado y verificado | Evidencia prevista |
|---|---|---|---|
| S02-01 | Preparación controlada sin modificar gestión | Prechecks, IPAM candidato de 3 sedes/4 WAN y FRR renderizados | S02_01, S02_02, S02_03, S02_04 |
| S02-02 | Tres routers FRR aislados | R-HQ, R-S1, R-S2 sobre Docker `network_mode:none`; prueba corregida, no primer intento | **S02_05_FRR_Tres_Routers_Aislados_Validados.png** |
| S02-03 | Cuatro enlaces WAN, OSPF y encaminamiento | HQ cuatro FULL; S1 dos; S2 dos; FIB principal 6/6; ICMP entre loopbacks 6/6 | S02_06; `S02_WAN_Validacion_OSPF.log` |
| S02-04 | Failover y retorno por cada sucursal | S1 primaria `s1p`→respaldo `s1b`→primaria; S2 `s2p`→`s2b`→`s2p`; en ambos casos la otra sucursal siguió estable | S02_07; `S02_Failover_S1.log`, `S02_Failover_S2.log` |
| S02-05 | LAN corporativa segmentada | Tres bridges/switches virtuales, 9 VLAN etiquetadas 802.1Q, 9 hosts, 9/9 gateways y seis ICMP inter-VLAN/sedes | S02_08; `S02_LAN_Validacion.log` |
| S02-06 | HTTP real intersedes y ACL diferenciada | HTTP temporal 4/4; servicio S1:8081 comprobado activo; bloqueo solo HQ VLAN110→S1:8081, contador nft **2 paquetes/120 bytes**; TCP8080 permitido; ACL y listeners temporales retirados | S02_09; `S02_HTTP_ACL_Prueba_Corregida.log` |
| S02-07 | Regresión y gestión | OSPF/LAN tras HTTP/ACL regresaron con rc0, `ens33=192.168.47.40/24`, default `192.168.47.2`, Git limpio | `S02_Regresion_Final_OSPF.log`, `S02_Regresion_Final_LAN.log` |
| S02-08 | Retiro y preservación | Desmontaje LAN→WAN→3 contenedores rc0, backups preapagado y archivos FRR presentes tras reboot; S02 queda **apagada intencionalmente** | `S02_Preapagado_Controlado.log` y bitácora de reinicio |

**Importante:** las magnitudes corresponden a pruebas del 23/10 **ANTES del desmontaje**. Una topología apagada no debe describirse como corriendo en la actualidad.

## 2. Inventario de capturas

Windows PowerShell verificó físicamente **9/9 PNG válidos** `S02_01`–`S02_09`, sin faltantes ni duplicación de identificadores y con tamaños >0. Manifiesto SHA-256 creado en `C:\Users\ruben\Documents\NETLAB360_Auditorias\S02_Manifest_Capturas.csv`. Se excluyó el antiguo `S02_05_FRR_Tres_Routers_Aislados.png`, correspondiente al intento incompleto. **Esto comprueba existencia/integridad básica; el archivo CSV y los PNG no están aún adjuntos al repositorio ni inspeccionados visualmente en este corte.** No afirmar lo contrario.

## 3. Criterios de aceptación pendientes antes de cerrar issue #2

- [x] Pruebas funcionales clave S02 realizadas realmente, incluidos failover, LAN 9/9, HTTP/ACL selectiva y regresión.
- [x] Preapagado, preservación de states de respaldo y reanudación Ubuntu/SSH verificados.
- [x] Nueve archivos PNG correctos localizados en Windows; manifiesto SHA256 creado.
- [x] HTTPS GitHub/resto de Internet restaurado el 24/10, git pull `bd76972` rc0.
- [ ] Auditar marcas y salidas de logs S02 para elaborar tabla de trazabilidad / criterios de evidencia; comprobar cada discrepancia sin inventar pruebas.
- [ ] Cotejar el borrador académico S01 de 65 páginas con la estructura docente única (12 partes); actualizar Introducción/Objetivos/Problema para revisión **30/10/2026**.
- [ ] Actualizar Fundamento técnico/Diseño HQ–S1–S2 para **13/11/2026** y secciones 7–9 con implementación, pruebas, análisis S01+S02 y referencias/capturas APA7.
- [ ] Definir cuáles capturas integrar al cuerpo vs índice de ZIP de anexos independiente autorizado; mantener fuente y numeración definitiva bajo control del archivo Word institucional.
- [ ] Comprobar manualmente consistencia de preámbulos, notas de figuras/tablas, citas y referencias; documentar estado de requisitos trasvasados.
- [ ] Aceptar documentalmente el **núcleo replanteado S02** y actualizar/cerrar issue #2 si corresponde; no afirmar cierre de módulos posteriores.

## 4. Transferencia de capacidades fuera del núcleo S02

- **S03:** Source of Truth, OpenTofu/Ansible, compliance y GitOps/CI (ejecución Ansible/drift anterior validada, OpenTofu/CI aún pendiente).
- **S04:** NOC/observabilidad central, métricas y alertas (issues #15/#20/#21).
- **S05:** LACP y pruebas avanzadas de capacidad/redudancia, SDN e integración correspondiente (issue #31, #5).
- **S06–S08:** diagnóstico inteligente/AIOps, integración, preparación de presentación/demo y entregables pendientes conforme plan vigente.
- **S01:** 72 % **histórico**, no sumar ni confundir con el porcentaje de S02.

## 5. Política para el informe docente

Un **único documento institucional** >=40 páginas al final, sin informes separados por S01, S02, S03. Orden: Portada; Introducción; Objetivos; Planteamiento; Fundamento; Diseño; Implementación; Pruebas; Análisis; Conclusiones/recomendaciones; Referencias; Anexos. Preservar contenido útil del borrador inicial, pero cambiar afirmaciones desactualizadas (p. ej. S2 como futuro cuando ya fue implementado). Figuras y tablas con preámbulo, numeración/nota APA7. Código completo y registros extensos al ZIP autorizado, sin contraseñas ni claves privadas.

**Enlaces:** [Issue S02](https://github.com/recm0708/netlab360/issues/2) · [Criterios docente](../academico/00-criterios-docentes-y-hitos.md) · [Informe único](../entregables/01-proyecto-investigacion-maestro.md) · [Bitácora](../sesiones/2026-10-23-s02-integracion-wan-lan.md).
