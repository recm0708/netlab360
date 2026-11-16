# NETLAB360 — Revisión editorial de la versión S01 para integrar S02 (24/10/2026)

**Fuentes comparadas:** copia institucional aportada `1457-Proyecto Semestral_S01.pdf`, **65 páginas**, con portada fechada **14/10/2026**; guía docente `1457-Formato Proyecto Final.pdf`, **3 páginas**; resultados de terminal S02 aportados hasta auditoría **24/10/2026** y matriz [S02](../control/05-s02-aceptacion-y-documentacion-2026-10-24.md). El documento PDF **no ha sido editado**; trabajar en la copia Word de origen del equipo académico. No replicar cédulas ni datos personales dentro del repo.

## 1. Dictamen de la auditoría 59–73

- `git pull --ff-only` desde `bd76972` a `4d524e8`; Git limpio.
- Matriz S02 presente; 8/8 logs técnicos principales disponibles; estados WAN/LAN guardados, S02 desmontada deliberadamente.
- OSPF Full HQ=4, S1=2, S2=2, FIB 6/6; ping loopback 6/6.
- Failover S1 `s1p→s1b→s1p` y S2 `s2p→s2b→s2p`, visto en ambos extremos.
- LAN 9/9 gateways y 6/6 comunicaciones inter-VLAN/sedes.
- HTTP 4/4 referencia; ACL de laboratorio solo HQ VLAN110→S1:8081 deniega, mantiene 8080 y acceso S1, contador **2 paquetes/120 bytes**, regla temporal retirada.
- Regresiones OSPF/LAN terminan con marcas aprobatorias.
- Pruebas unitarias offline WAN **4/4**, LAN **4/4**, HTTP/ACL **6/6**, total **14/14**; `FALLOS_AUDITORIA=0`, `S02_AUDITORIA_DOCUMENTAL=OK`, `RESULTADO_AUDITORIA_S02=0`.
- Las nueve capturas S02_01–09 existen en Windows, CSV SHA256 generado. Su contenido visual individual y montaje en informe **pendientes**.
- **Veredicto:** S02 aprobado funcionalmente y en consistencia de logs; documentación docente + aceptación final de issue #2 aún abiertas. No elevar arbitrariamente el % a 100.

## 2. Diferencias concretas entre PDF S01 y formato oficial

| Ubicación PDF base | Texto/estructura anterior | Corrección obligatoria según docente y S02 |
|---|---|---|
| pp. 3–6 índice | Introducción; `1 Planteamiento`, `2 Justificación`, `3 Objetivos`, `4 Alcance`, `5 Marco teórico`, `6 Metodología`, `7 Diseño`, `8 Desarrollo`, `9 Resultados`, `10 Discusión`, `11 Recomendaciones`, conclusión, referencias | Reestructurar para orden de **12 partes** de la guía: Portada, Introducción, Objetivos, Planteamiento del problema (incluye justificación), Fundamento técnico, Diseño, Implementación, Pruebas, Análisis, Conclusiones y recomendaciones, Referencias, Anexos. *Metodología/alcance* pasan a subsecciones pertinentes sin perder material útil. Actualizar índice automático solamente después de reorganizar. |
| p. 7–8 Introducción | `sucursales que se incorporarán conforme avance el desarrollo`; énfasis fuerte en tecnologías antes del problema | Introducción: contexto→problema→propuesta→**resultado S02** HQ/S1/S2 con 4 WAN, 9 VLAN, pruebas OSPF/failover/HTTP y ACL. No presentar NOC, IA o SDN pendientes como integración productiva. Conservar citas realmente usadas, revisar correspondencia con referencias. |
| pp. 8–10 Planteamiento/Justificación | Problema y justificación separados como apartados principales 1 y 2 | Unificar en **Planteamiento del problema**: situación, problema, impacto, pregunta, justificación técnica/operativa/académica y viabilidad como subsecciones subordinadas, evitando repetir el contexto en varios párrafos. |
| p. 11 Objetivos | 7 específicos y general amplios pero coherentes; automatización/NOC/AIOps futuros | Mantener objetivo general de diseño/implementación/evaluación y específicos verificables; asegurar relación explicitada con pruebas reales y tareas futuras. No tachar como completados NOC final ni IA; evite redundancias. |
| pp. 11–14 Alcance | S2 `se incorporará`, inventario `tres sedes, nueve VLAN y dos enlaces WAN`, solo HQ↔S1 | En la narrativa **histórica S01**, conservar resultados de 2 sedes y ensayos aislados con fecha. Agregar corte S02 posterior: **3 sedes, cuatro enlaces WAN físicos virtuales (2 principales/2 respaldo), 9 VLAN integradas**, mantener distinción entre diseño y observación. El problema es el corte obsoleto, no los ensayos S01 originales. |
| pp. 14–21 Marco teórico | Título `Marco teórico y tecnológico` | Reetiquetar **Fundamento técnico**, clasificar fuentes oficiales, conceptos justificados y aplicados. Separar LACP/SDN/NOC global futuros de la prueba real específica. |
| pp. 21–26 Metodología | Capítulo independiente | Integrarla como **metodología de implementación** y **protocolo de pruebas** dentro de 7/8, sin repetir teoría de métodos o extender a nuevo capítulo numerado no autorizado. |
| pp. 26–34 Diseño | S2 descrita como parte proyectada; troncales/subredes y WAN según esquema temprano | Diseño S02 HQ/S1/S2, R-HQ/R-S1/R-S2, 3 switches, 9 segmentos 802.1Q, 4 WAN primario/respaldo, OSPF costs 10/100, 3 loopbacks; red de gestión `ens33 .40/24` separada. Diferenciar futuras funciones observabilidad/automación del desplegado en S02. |
| pp. 34–49 Desarrollo S01 | Desarrollo inicial llamado `8` y varios ensayos no integrados | Reubicar bajo **7 Implementación** con dos subpartes **S01 antecedente** y **S02 integración multisede** y archivos representativos; S03 solo indicación de continuidad si necesario. |
| pp. 50–56 Resultados S01 | Esencialmente resultados parciales S01 | Bajo **8 Pruebas y validación** añadir tablas S02 de baseline, evento, esperado, observado, evidencia y recuperación, con 9 PNG y logs citados por nombre; sin confundir resultados S01/ S02. |
| pp. 57–59 Discusión | Limitación menciona falta S2 y topología única | Bajo **9 Análisis de resultados**, **actualizar** limitación ya superada en S02; conservar limitaciones reales: WAN/LAN virtual, HTTP/ACL temporales, enlaces no constituyen equipos físicos redundantes, NOC/SDN y AIOps integrados pendientes. |
| pp. 60–64 Recomendaciones/Conclusión | Secciones separadas, conclusión todavía dice `integración de estos mecanismos dentro de una misma topología... requiere validaciones adicionales` | Fusionar **10 Conclusiones y recomendaciones**, evidenciar que S02 sí unificó WAN+LAN+ACL y aún faltan módulos globales. No copiar conclusiones viejas sin matizar. |
| p. 65 Referencias | 10 entradas, varias con `s. f.` | Contrastar TODAS con citas en cuerpo, URLs, datos editoriales, cursivas y APA7. No inventar fuentes ni fechas; agregar solo las que de verdad se citen. |
| Después referencias | Sin índice técnico de anexos del proyecto | Agregar **12 Anexos** al documento con mapa de evidencias; ZIP de scripts/configs/logs separado autorizado, evitar copiar todo el código al cuerpo. |

## 3. Prioridades antes del 30/10/2026

1. Producir en el **Word maestro existente** una portada completa sin publicar datos personales en GitHub, una **Introducción coherente con S02**, **Objetivos** verificables y **Planteamiento del problema** integrado (justificación incluida).
2. Comprobar redundancias, lenguaje de resultados, citas APA7 y referencias de estos apartados; generar tabla de contenido por estilos institucionales.
3. Compartir al grupo la versión revisada y designar representante que mostrará borrador en Teams el **30/10/2026**. No crear PPT para esa revisión.
4. En cortes posteriores, desarrollar Fundamento y Diseño (13/11) y después 7–12 hasta cubrir la fase S02; el informe final exige mínimo 40 páginas y presentación/demo separadas.
5. No cerrar la issue #2 hasta verificar que el documento está actualizado y la tabla de evidencias/transferencias está coherente.

**Limitación:** las correcciones editoriales listadas derivan de **PDF S01 y guía docente disponibles**; sin el Word actual no se puede confirmar que su edición vigente coincida exactamente con este PDF o efectuar cambios en sus estilos/índices. Ningún resultado posterior S03 se atribuye a S02.
