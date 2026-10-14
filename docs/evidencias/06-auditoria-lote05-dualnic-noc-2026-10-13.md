# NETLAB360 — Auditoría lote05: dual-NIC y cierre NOC

**Corte:** 13/10/2026, después de 21:39 Panamá.  
**Fuente:** 8 PNG recibidos y salida íntegra real de Ubuntu con pasos 125–136. **4 PNG dual-NIC + 1 PNG NOC final aceptados para publicación**; 3 adjuntos adicionales excluidos por duplicación o por ser cierres intermedios superados. Ninguna imagen fue editada.

## Acreditación técnica dual-NIC

- **B2_DUALNIC_01 (21:37:29):** bonds Linux `fault-tolerance (active-backup)`, A primario `a1` y B `b1`, 2 slaves en cada bond, MII up, HTTP `NETLAB360_DUAL_NIC_HTTP_OK`, `HTTP_DUALNIC_PRIMARIA=OK`.
- **B2_DUALNIC_02 (21:37:32):** fallo controlado a1 provoca MII down a1/b1, `Link Failure Count:1`, switchover automático a2/b2, dos miembros registrados en cada bond, `HTTP_DUALNIC_RESPALDO=OK`.
- **B2_DUALNIC_03 (21:37:35):** a1/b1 de nuevo MII up, a2/b2 continúa activo (sin failback preferido), dos miembros registrados, `HTTP_DUALNIC_RECUPERADA=OK`, `DUALNIC_ACTIVE_BACKUP_TRES_ESTADOS=OK`.
- **B2_DUALNIC_04 (21:39:13):** Docker/netns vacíos, ens33 `192.168.47.40/24`, GW `192.168.47.2`, tres servicios activos y `main...origin/main` limpio. Log de ensayo `~/netlab360-bootstrap/evidencias/b2-dualnic-activebackup-20261013-213725.log`, `RESULTADO_B2_DUALNIC=0`, `RESULTADO_EJECUCION_DUALNIC=0`, `RED_GESTION_INTACTA=SI`.
- **B3_04_FINAL (16:25:50):** cierre NOC histórico, `PUERTO_8765_LIBRE: SI`, sin contenedores ni namespaces, gestión intacta. Es evidencia complementaria del anterior `B3_04_Postcheck_Servicio_NOC.png` que mostró el puerto todavía ocupado; conservar distinción temporal, sin alterar historia.

**Límites técnicos:** la redundancia probada usa dos pares de interfaces veth en network namespaces aislados, **no** dos adaptadores VMware de la VM, dos switches físicos, redundancia de host, ni disponibilidad medida sin pérdida durante el instante de falla. Puntuación provisional del bloque redundancia pasa de 4/10 a 6/10 (+2 por active-backup funcional); matriz global S01 **65/100**. Los 4 puntos restantes en redundancia son equipamiento/servidor real y mayor integración. No sumar puntos por el cierre fotográfico NOC.

## Adjuntos excluidos (NO IMPORTAR)

| Archivo | Motivo |
|---|---|
| `B3_04_Postcheck_Servicio_NOC(1).png` | **Duplicado exacto byte a byte** del ya versionado `evidencias/capturas/B3_lote02/B3_04_Postcheck_Servicio_NOC.png`; Git blob SHA `9b1237823ba483223c24e96b280f0c9458891405` |
| `B3_09_Postcheck_Telemetria_Viva.png` | Diagnóstico intermedio con 9108 ocupado, supersedido por `B3_09_Postcheck_Telemetria_Viva_Final.png` del lote03, que acredita liberación |
| `B2_L3_04_Postcheck_HTTP_WAN.png` | Cierre del primer intento L3 abortado, supersedido en evidencia funcional por `B2_L3_04_Postcheck_HTTP_WAN_Final.png` del lote03 |

**Los tres adjuntos excluidos no deben añadirse otra vez a Git.** Los dos cierres intermedios pueden permanecer documentados en las bitácoras históricas sin publicarlos como PNG prioritarios.

## Manifiesto lote05 (bytes originales)

| PNG | SHA-256 | Bytes |
|---|---|---:|
| `B2_DUALNIC_01_Primaria_Activa.png` | `3524bcfa383327ddf9eece83f0d92281b1beff736d0c10acfc368a728ed87445` | 61702 |
| `B2_DUALNIC_02_Conmutacion_Respaldo.png` | `8f77af2c4c3865a0f964fc41c7aa9ac6b3dbe7b81c941a0b17a12bfb57387c4d` | 67454 |
| `B2_DUALNIC_03_Interfaz_Restaurada.png` | `510dda6358ead4c79b4755d22d27132ff7c598990f70a393bab2fd8ae3566a6f` | 87935 |
| `B2_DUALNIC_04_Postcheck_Final.png` | `6e34af2db4287f8ad049bdb9dff296a89a7b8bc7c35abbd528cc389f13097200` | 36121 |
| `B3_04_Postcheck_Servicio_NOC_Final.png` | `9c004b3dd7e7a7030e142d9f0a3e4527ab2294ce50cb6ba28674c0bdb51d6d90` | 34783 |

Paquete de transferencia `NETLAB360_LOTE05_DUALNIC_NOC_5PNG_2026-10-13.zip`: **252109 bytes**, SHA-256 `9e57057e402a9a87e1c2e91997ad59dd88cb136d6329f75ba50721181959cdfa`, ZIP test íntegro, 5 PNG + manifiesto CSV + instrucciones TXT. **Imágenes recibidas y auditadas, pero PENDIENTES de subir bytes a GitHub.** Tras migración, ubicar PNG sin subcarpetas en `evidencias/capturas/` y CSV en `evidencias/manifiestos/`.

## Proyecto y GitHub

- Lotes 01/02: 24 PNG publicados.
- Lote03: 20 PNG + CSV publicados por commit `0d749df`.
- Lote04: 13 PNG + CSV **publicados por commit `2af7a8054a87bc10db1195f5f54d92b2dbc04c8f`**, verified `LOTE04_PUBLICADO=OK`, refs local/remoto iguales.
- Total actualmente versionado y auditado antes de lote05: **57 PNG**, 4 grupos, 4 CSV.
- Se solicita organización de **todos los PNG directamente** en `evidencias/capturas/`; migración segura con `git mv` y hashes en `scripts/mantenimiento/aplanar-capturas.py`, commit `d068779`. No afirmar que la reorganización fue ejecutada o publicada sin recibir el próximo `git push` del usuario.
