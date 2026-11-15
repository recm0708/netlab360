# NETLAB360 — Corte operativo S05, lotes 152 y 153 (parcial)

**Fecha:** 15/11/2026, Panamá. **Referencia:** [corte 151](CORTE-MAESTRO-NETLAB360-S05-151-20261115.md). **No repetir** los lotes 152 ni el importador 153; continuar en la rama local ya creada.

## Resultado demostrado: lote 152 HA de instancia

- Un ensayo **real y único** de caída/restauración del backend HQ, mediante scripts/operacion/s05-lote-ha-instancia-con-watchdog.sh, con temporizador transitorio 120 s armado **antes** de la perturbación y cancelado tras restauración.
- El NOC observó `BACKEND_HQ → BACKEND_S1 → BACKEND_HQ` con **17 muestras** y `S05_HA_NOC_CICLO=HQ_S1_HQ_OK`, `S05_HA_TRANSICION_VERIFICADA=OK_HQ_S1_HQ`, `LOTE152_HA_INSTANCIA=OK`.
- JSONL: `~/netlab360-bootstrap/s05/evidencias/ha-noc/S05_HA_NOC_CICLO_20261115T233530Z.jsonl`, SHA256 `8fcee9fdc02acbbddc359898fe9832ba085e08d4aa24c5aae47e0fa6de97a9c8`. Todavía no versionado en GitHub.
- Postcheck NOC healthy, 6/6 unidades activas, FIB S1=s1p/S2=s2p, ens33=192.168.47.40/24 gateway .2; Git main limpio. Es **HA lógica de backend en una VM**, no HA física de host/hipervisor ni redundancia del frontal.
- Captura 64 (`S05_64_HA_Instancia_HQ_Respaldo_S1_y_Retorno.png`): usuario confirma que fue tomada, **no recibida como imagen en GitHub ni auditada visualmente**. El nombre se distingue de la captura 64 antes propuesta como complementaria.

## Resultado demostrado: lote 153 parcial

- Se creó la rama local `evidencias/s05-70png-verificados-20261115` desde main `23ad4b3`.
- El importador `--import` **copió realmente 70 PNG** en `evidencias/capturas/fase5`, con inventario CSV y manifiesto SHA-256. `sha256sum -c` imprimió **70/70 OK**. Total descomprimido 5 588 763 bytes. **PNG64 no forma parte de los 70** (el CSV termina en PNG63).
- La comprobación posterior de dimensiones abortó por un `AssertionError` en la regla `100 <= ancho,alto <= 10000`; **no se identificó el nombre causante**. Este umbral arbitrario puede rechazar recortes pequeños legítimos; **no hay evidencia de corrupción**, puesto que se verificaron hashes 70/70 y cabecera PNG del importador. Hacer un listado de todas las dimensiones, marcando valores menores de 100 sin invalidar automáticamente las imágenes.
- Como el bloque abortó antes de `153-07` y el marcador final, todavía no hay `git add`, commit, push, PR ni merge de capturas. **No repetir el importador ni recrear la rama**: reanudar tras los archivos presentes.

## Orden pendiente

1. Diagnóstico de dimensiones **no destructivo** de 70 imágenes e inventario de la rama local. La fotografía/documento original no se modifica.
2. Localizar PNG64 original en Windows y trasladarlo por SSH/SCP a la VM; contrastar su SHA256 en origen y destino. Copiarlo exclusivamente a `evidencias/capturas/fase5` y generar un **manifiesto adicional de la captura 64**, preservando intacto el manifiesto histórico 70/70.
3. Revisar 71 capturas por legibilidad y secretos antes de su publicación; los hashes no equivalen a inspección visual.
4. Versionar en la rama existente: 71 imágenes, manifiesto original de 70, manifiesto separado PNG64, inventario de 70 y documentación; push y PR, verificar blobs Git antes de cerrar #105/#43/#64.
5. Versionar copia JSONL auténtica y log TXT de 152 con hashes, preparar acta de aceptación solo lectura, incorporar límites mono-VM y datos P1/P1B correctos.
6. Cerrar #32/#23/#31/#64/#105 y finalmente #5/milestone S05 solamente cuando su evidencia/documentación esté aceptada. Mantener S06/S07/S08 abiertas.
7. No apagar/reiniciar Ubuntu mientras los 21 namespaces efímeros sean necesarios; primero respaldo/recuperación o suspensión VMware comprobada.

**CI/repo:** esta actualización documental no afirma que la rama local del usuario, PNG64 o JSONL de 152 ya estén presentes en GitHub.
