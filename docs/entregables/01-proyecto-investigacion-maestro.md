**CONTROL DE TABLAS PDF 4.4 (27/10):** La Tabla 12 (p. 98) compara capacidades de S01/S02 y se conserva. Hay dos rótulos «Tabla 13»: la tabla SLI de capítulo 6 mantiene el 13; la segunda, en 7.8 (p. 104), debe renumerarse a Tabla 14 y su fila de 107 capturas debe actualizarse a 122 (83/9/8/22). Revisar también cifras en 6.6 (p. 81), 6.9.6 (p. 97) y 7.7.1 (p. 103). No se ha editado el PDF; la corrección corresponde al Word del equipo.

**ÚLTIMA VERSIÓN REVISADA: borrador 4.4 (110 páginas, 27/10).** S04 5.6 y validaciones 6.9 completas, Figuras16–20 y Tabla13. Pendiente análisis 7.10, actualización de conclusión/recomendaciones S04 y consolidación de Tabla12 para **122 PNG oficiales (83/9/8/22)**. Un solo informe académico, TAR técnico separado, sin anexos al Word. No presumir SLO formal ni revisión docente celebrada.

**CONTROL 27/10 — PDF 4.3, 99 páginas.** Confirmado en el PDF adjunto que 4.7 p.32 ya no contiene el párrafo obsoleto, 5.5.9 fue ajustado y 5.6.1–5.6.5 están redactados (pp.66–70). No rehacer 5.6. El informe único aún requiere 6.9, interpretación de S04 en capítulo7, conclusiones y recomendaciones S04 y actualización de Tabla12; el capítulo6 todavía habla solo de tres primeras fases. La VM ejecutó `sudo systemctl poweroff` y cerró SSH, **falta observar `Powered Off` en VMware**. [Registro](../sesiones/2026-10-27-s04-poweroff-solicitado-borrador43.md).

**VERSIÓN VIGENTE AL 27/10/2026:** `1457-Proyecto Semestral_borrador4.2.pdf` (**95 páginas**), todas las correcciones 1–13 confirmadas. El único párrafo antiguo repetido está en 4.7 p.32 y debe eliminarse. Falta incorporar texto nuevo de S04 en 5.6/6.9/7.10, conclusiones y Tabla12 en Word; SLO sigue propuesto, y no existe aceptación docente. Bitácora de preapagado y desmontaje 4.69–4.75 OK; los servicios están detenidos y la red S02 desmontada, pero no consta poweroff de Ubuntu. [Registro](../sesiones/2026-10-27-s04-borrador42-desmontaje-validado.md).

# NETLAB360 — Índice maestro y situación del informe único

**Actualizado el 27/10/2026.** Documento principal: Word institucional editado por el equipo. Última exportación recibida: `1457-Proyecto Semestral_borrador4.1.pdf` (**95 páginas**): incorporadas cinco correcciones intro/fundamento/diseño/Tabla5, pero todavía no los apartados completos 5.6, 6.9 y 7.10. Las correcciones se entregarán **por mensajes de chat**, para copiar y pegar en el Word original, y se comprobará un PDF posterior antes de declarar aceptación.

**Título comunicado en Teams el 17/10/2026:** «Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede». Aprobación docente pendiente. Encabezado abreviado del proyecto: `NETLAB360 | Redes Empresariales Multisede`.

## Estructura real verificada en borrador 4.0

1. **Introducción** y portada/índice.
2. **1. Objetivos** (general/específicos).
3. **2. Planteamiento del problema** (contexto, problema, formulación y justificación).
4. **3. Fundamento técnico** (virtualización, VLAN, OSPF, LACP, SoT, OpenTofu, Ansible, Prometheus/NOC, datos y límites de AIOps).
5. **4. Diseño de la solución** (topología real HQ/S1/S2, direcciones, VLAN, WAN redundante, gestión aislada, automatización y NOC).
6. **5. Implementación**: `5.3` S01, `5.4` S02, `5.5` S03 **ya presentes**; agregar `5.6` S04 de collector/Prometheus/NOC/SQLite/SLI con límites documentados.
7. **6. Pruebas y validación**: `6.1–6.8` ya presentes; agregar `6.9` para alerta G3, persistencia TSDB/SQLite, UNKNOWN, regresión y mediciones 15/60 minutos.
8. **7. Análisis**: `7.1–7.9` presentes, centrados en tres fases. Añadir `7.10` y actualizar frases de estado vigente en `7.1,7.6,7.8,7.9`.
9. **8. Conclusiones y recomendaciones**: actualizar `8.1`, convertir `8.2.2` de «integrar NOC» en mejoras realmente futuras, mantener los demás límites.
10. **Referencias APA 7** al final, sin capítulo de anexos.

Hasta el borrador 4.0 hay **15 figuras** y **12 tablas**, por lo que las nuevas S04 seguirán la secuencia **solo al insertarlas y revisar índice**, sin numerarlas por anticipado. Actualizar **Tabla 1** (NOC integrado), **Tabla 5** (S04 no «Planificada») y **Tabla 12** (objetivos de observabilidad y **129 PNG**, no 107). Nota de Tabla 12 aparece separada en p. 89 de la tabla p. 88; revisar saltos de párrafo en Word.

## Fuente de evidencia técnica

- **S01**: validaciones de mecanismos experimentales; 90 PNG finales.
- **S02**: integración 3 FRRouting, cuatro WAN, nueve VLAN, pruebas WAN/ACL y 9 PNG; cierre interno #2.
- **S03**: auditoría y reconciliación Ansible sobre FRR, OpenTofu 17 recursos `terraform_data` **solo metadatos**, GitHub Actions; 8 PNG y evidencia GitOps Markdown (no PNG).
- **S04**: NOC central y por sede, exporter 9110 y Prometheus 9091, alerta real G3, UNKNOWN sin falsas WAN/VLAN, TSDB tras restart 68/68+28/28, SQLite G3 3/3 tras reinicio NOC, 22 PNG S04 y regresión OSPF/LAN final. G5 medición 15m 450/450=100% y 60m 1698/1740=97.586%, 99 % SLO **solo propuesto**, presupuesto -25. Sin notificaciones externas ni modelo IA acreditado.

**No insertar en el informe** scripts extensos, contraseñas, tokens, estados operativos OpenTofu, anexos o PDF originales de la docente. Todo lo distribuible y necesario se preparará en un **TAR técnico separado, auditado**, en S08. No prometer OVA/OVF ni manual separado como requisito confirmado.

## Prioridades editoriales

- [ ] Incorporar al Word los bloques corregidos de Introducción, 3/4 (NOC real), 5.6, 6.9, 7 y 8; contrastar tablas y seleccionar figuras legibles con preámbulos/títulos/notas y referencias cruzadas.
- [ ] Exportar nuevo PDF (borrador 4.0 **no** cambia por actualizar GitHub), comprobar paginación, índice, las notas huérfanas y coherencia APA 7.
- [ ] Presentar Introducción, Objetivos y Problema por Teams **30/10**, registrar revisión real; Fundamento y Diseño **13/11**.
- [ ] Formalizar por el grupo SLO candidato, alcance de alertas solo locales y decisiones de inclusión de datos antes de aceptación S04; continuar S05–S08 en el mismo informe.

[Guion de S04 para Word](../academico/s04-guion-de-actualizacion-del-informe.md) · [Matriz de pruebas S04](../operaciones/s04-g6-matriz-aceptacion-evidencias-2026-10-27.md) · [Criterios docentes](../academico/00-criterios-docentes-y-hitos.md) · [TAR técnico final](../academico/03-anexos-y-demostracion.md).

**Control 27/10 (borrador 4.1):** se validaron 5 correcciones efectivamente incluidas, sin alterar datos originales del informe. Quedan textos de estado anterior a S04, en especial 2.4.1, 3.8, Tabla1 y nota de Tabla5; la edición se suministra por chat y se coteja después con una nueva exportación. En paralelo se respaldaron estados WAN/LAN y SQLite G3, se detuvieron servicios NOC/Prometheus/exporter; la topología FRR/LAN/WAN todavía no consta desmontada. [Bitácora S04](../sesiones/2026-10-27-s04-borrador41-preapagado.md).
