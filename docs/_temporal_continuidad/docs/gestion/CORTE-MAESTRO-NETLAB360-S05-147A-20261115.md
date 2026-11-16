# CORTE MAESTRO NETLAB360 — S05 147A: originales P1 recuperables, PNG 70 inventariados

**Fecha 15/11/2026. Documento de continuidad vigente tras [corte 145C](CORTE-MAESTRO-NETLAB360-S05-145C-20261115.md) y auditoría 146A.** Objetivo: finalizar solo S05 sin repetir ensayos WAN/LACP/SDN ni adelantar técnicamente S06–S08.

## Lote 147A validado

- Main sincronizada al PR #146 (commit 9998de5); cuatro pruebas offline del auditor de procedencia P1 pasaron 4/4; lote 147A terminó con marcador LOTE147A_DIAGNOSTICO=COMPLETADO y Git limpio.
- TAR real P1 del 10/11 encontrado con 4/4 SHA-256 de miembros históricos idénticos al manifiesto original, sin extracción ni sobrescritura; 15662 bytes. Original log P1 y su manifiesto siguen intactos.
- Tres JSON fijos P1 actualmente en la VM muestran fechas del **11/11/2026** y hashes diferentes; existe segundo log S05_P1_20261111-100600.log, compatible con una repetición, pero correlación por contenido todavía pendiente. No mezclar métricas de dos corridas ni reescribir manifiesto del 10/11.
- P1B: verificación de manifiesto **5/5 archivos OK**. Sin nueva prueba iperf3.
- Milestones 5–8: operador ejecutó exitosamente GitHub CLI API PATCH de sus **cuatro descripciones**, verificó contadores S05 6/1, S06 3/0, S07 1/0, S08 11/2 y estado OPEN; marcador **MILESTONES_CORTE146A=OK**. La indicación previa de que no podían editarse ya no aplica: la edición la efectuó el operador en la VM, no el conector.
- CSV Windows **recibido y analizado**: 70 PNG, **5 588 763 bytes**, 70 SHA distintos (0 duplicados según CSV). Todas las rutas de las 70 entradas señalan Pictures/Screenshots, identificadores multipartes 17,18,58 y variantes 01/02. Ninguna falta por el filtro 48–63 anterior.
- PNG63 original Windows SHA d3506bdb33d28037f8860bd53bd1bf3bc3c6b33ff7083d58c80e5e377b1cccfe, 155432 bytes: coincide con adjunto visualmente revisado. **Los otros 69 no han sido inspeccionados por bytes ni importados** solo por el CSV.

## Código fusionado; NO ejecutado aún

- PR #147 / commit 330ab8f: recuperación P1 histórica exclusivamente a carpeta nueva, tests offline; script HA instancia con watchdog systemd transitorio 120 s independiente del SSH y prueba única HQ→S1→HQ en NOC, sin afectar WAN/LACP/SDN. [Runbook](../operacion/s05-lotes-148-149-recuperacion-p1-y-ha-instancia-segura-20261115.md).
- PR #148 / commit 5076fe8: importador ZIP+CSV de 70 PNG reales, verificación de tamaño/firma/hash y creación exclusiva de blobs/manifiesto; sin transferir ni importar PNG aún. [Procedimiento](../evidencias/s05-importacion-70-png-originales-20261115.md).
- Las comprobaciones CI verifican código y contratos offline, **no** equivalen a recuperación real de archivo, falla controlada HQ o importación de PNG.

## Ruta de cierre S05

1. Lote 148A: recuperar desde TAR cuatro originales del 10/11 a directorio nuevo y verificar SHA 4/4. Conservar JSON actuales del 11/11.
2. Lote 148B: cotejar segundo registro P1 con JSON del 11/11, documentar dos ejecuciones si corresponde, aprobar análisis P1/P1B sin repetir carga.
3. Preparar ZIP en Windows con 70 PNG listados y transferir ZIP/CSV a VM; ejecutar --check del importador; inspeccionar datos sensibles antes de --import y hacer commit/PR con originales reales.
4. Lote 149: precheck HA solo lectura; luego **un único ensayo real** con timer de rescate armado, registrar transiciones HQ→S1→HQ, logs y captura 64 solo después de marcador de éxito.
5. Completar reporte S05, evidencia SHA, aceptación solo lectura, cerrar #23/#31/#32/#64/#105 y por último #5 y milestone 5. S06/7/8 quedan abiertas.
6. Antes de apagar Ubuntu, preparar y verificar respaldos y procedimiento de reconstrucción de 21 namespaces efímeros (o suspender VMware con validación de reanudación). Guest shutdown ahora perdería esos recursos; no ejecutarlo antes del cierre.

**Prohibido repetir:** 145A/145B, LACP 2→1→2, WAN failovers, aislamiento SDN y caída sdna0, reinstalar Faucet, tocar ens33 o reiniciar guest sin plan comprobado. No usar clear.
