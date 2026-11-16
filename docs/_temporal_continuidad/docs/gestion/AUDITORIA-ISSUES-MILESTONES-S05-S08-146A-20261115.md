# NETLAB360 — Auditoría de issues y milestones S05–S08, corte 146A

**Fecha:** 15/11/2026. **Alcance:** seguimiento; no hubo ejecución técnica S06/S07/S08. Complementa [auditoría histórica 145B](AUDITORIA-ISSUES-MILESTONES-S05-S08-145B-20261115.md).

## Nuevas evidencias S05

- **145C:** captura NOC 63 recibida y validada: tres LACP HQ/S1/S2 en 2/2, Faucet conectado 26 reglas observadas, HA HTTP HQ principal. El original Windows tiene 155432 bytes, SHA-256 d3506bdb33d28037f8860bd53bd1bf3bc3c6b33ff7083d58c80e5e377b1cccfe, idéntico al archivo recibido.
- **146A:** 4/4 tests offline HA, 21 namespaces, 4 contenedores, 6/6 servicios, gestión ens33 y GW correctos; NOC healthy, FIB S1=s1p/S2=s2p, monitor HTTP desde S2 fresco, tres GET HTTP correctos y SDN inspección no destructiva satisfactoria.
- **Bloqueo 146A:** el log original P1 pasó SHA, pero los 3 JSON actuales difieren de hashes del manifiesto histórico. El validador abortó en 146A-13: no se ejecutaron 146A-14/15 ni existe marcador final. Las cifras P1 históricas son provisionales hasta reconciliar TAR. Ver [auditoría de procedencia](../evidencias/s05-reconciliacion-p1-146a-20261115.md).
- **Windows:** 70 PNG encontrados. La salida 48–63 fue solo un filtro, no ausencia de anteriores. Original 63 pasó comparación SHA, pero los PNG todavía no están importados a GitHub.

## Estado de hitos

| Hito | Estado correcto | Issues abiertas/cerradas | Razón |
|---|---|---|---|
| S05 #5 | ABIERTA | 6/1 | Integridad P1 (#31/#105), prueba instancia (#32), originales y acta (#23/#64/#5) |
| S06 #6 | ABIERTA | 3/0 | Solo datos candidatos/reglas; sin dataset etiquetado, entrenamiento ni evaluación ML |
| S07 #7 | ABIERTA | 1/0 | No se ha realizado un ciclo AIOps supervisado |
| S08 #8 | ABIERTA | 11/2 | Informe hasta S04, TAR, PPT, aceptación, exportación opcional y reboot guest sin validar |

Los conteos se mantienen respecto de auditoría 145B porque no se cerraron ni reasignaron issues. El conector GitHub disponible puede modificar issues/PR, pero no presenta acción para editar la descripción del objeto milestone. Este documento actualiza el seguimiento del hito; **no afirma que se haya editado el metadato interno de la milestone**. No corresponde cerrar ninguna de las cuatro.

## Checklist reconciliado

- **S05 #5/#23/#31/#32/#64/#105:** evidencias 145C/146A y bloqueo P1 registrados. #64 confirmó SHA de original PNG63; #23 SDN inspect correcto; #32 tiene precheck positivo pero prueba real pendiente. Ninguna cerrada indebidamente.
- **S06 #6/#25/#26:** insumos reales de S05 y baseline por reglas [x]; dataset, etiquetas, particiones y entrenamiento/evaluación [ ]. #25 incorpora advertencia de calidad de P1. #26 no tuvo avance nuevo.
- **S07 #7:** solo insumos S04/S05 [x], ciclo AIOps [ ].
- **S08 #27/#34/#36/#43/#106:** corte 145C como fuente, no Word/PPT/TAR terminado. #43 registró 70 PNG locales y SHA del original 63; #34 anotó 26 reglas capturadas; #106 recuerda que 21 namespaces no sobreviven a reboot guest sin reconstrucción verificada. #8/#17/#29/#44/#45/#48 no tienen nuevos checks acreditados y permanecen abiertos.
- **Issues cerradas #24/#28/#37:** se mantienen cerradas por decisiones explícitas de exclusión o consolidación, sin fingir implementación de WireGuard, manual separado ni OVA.

## Ruta de cierre real

1. Investigar P1 por lectura de TAR y SHA, conservando archivos actuales y originales sin sobrescribir ni regenerar hashes.
2. Realizar una sola prueba HA de backend HQ observada desde S2/NOC, con temporizador externo de restauración, aceptar rollback.
3. Verificar, importar y manifestar PNG/JSON/TXT/CSV; cerrar el análisis #31, evidencia #105, la documentación #23 y NOC #64.
4. Aceptar S05 y cerrar solo las issues completas, después #5 y milestone S05. Mantener S06/7/8 abiertas.
5. No apagar Ubuntu antes de asegurar evidencias y definir/probar procedimiento de reconstrucción o suspensión de VMware: shutdown destruye namespaces efímeros.
6. Una vez cerrada S05, incorporar resultados a la sección correspondiente del informe académico único; no adelantar técnicamente S06/S07.
