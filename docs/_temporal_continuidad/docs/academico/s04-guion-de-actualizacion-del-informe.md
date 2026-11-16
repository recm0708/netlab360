# NETLAB360 — Control editorial del informe hasta S04

**Corte: 01/11/2026.** Revisamos internamente el borrador **4.6 (113 páginas)** frente a la guía docente. Los apartados del informe hasta S04 están incorporados; no queda pendiente rehacer el análisis ni las conclusiones de estas cuatro fases.

## Contenido verificado

- Introducción, objetivos y planteamiento del problema, fundamentos técnicos y diseño.
- Capítulo 5: implementación de S01–S04, hasta 5.6.
- Capítulo 6: pruebas y validación de S01–S04, hasta 6.9.
- Capítulo 7: interpretación de resultados, incluida S04 en 7.10.
- Capítulo 8: conclusiones y recomendaciones conforme a los módulos implementados.
- **Figuras 1–20, tablas 1–13 y 10 referencias**; inventario oficial de **122 PNG**: S01=83, S02=9, S03=8, S04=22.

## Resultados S04 que conservamos

Se observaron OSPF Full 4/2/2, WAN 6/6, LAN gateways 9/9 y conectividad 6/6. El incidente HQ/s1p se recuperó tras disparar la alarma; las historias TSDB y SQLite sobrevivieron a reinicios. El SLI de scrapes fue 450/450 (100 %) en 15 minutos y 1698/1740 (97,586 %) en 60 minutos. **El valor 99 % es nuestra referencia experimental de comparación y no se cumplió en la ventana de 60 minutos**. No lo presentamos como SLA ni como nivel formalmente ratificado por la docente; los avisos demostrados son locales.

## Seguimiento académico

La presentación del **30/10/2026 se realizó**. Según confirmó el equipo el 01/11, la profesora indicó que todo estaba bien y autorizó avanzar al siguiente entregable. No se comunicaron correcciones específicas de este corte. La revisión del **13/11/2026** aún debe celebrarse, centrada en fundamento y diseño, con la versión de informe vigente.

Continuaremos trabajando sobre el **mismo documento Word/PDF**, incorporando los resultados reales de S05–S08 cuando se ejecuten. El material técnico se preparará en un TAR separado de la entrega escrita, sin duplicar documentos ni alterar las evidencias originales.

[Control de fases](../control/06-tablero-porcentajes-cierre-fases-2026-10-25.md) · [Revisión del 30/10](https://github.com/recm0708/netlab360/issues/47) · [Siguiente revisión](https://github.com/recm0708/netlab360/issues/48).
