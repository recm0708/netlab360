# NETLAB360 — Auditoría visual oficial de evidencias B3, lote 02

**Fecha:** 2026-10-13 Panamá. **Fuente:** cinco imágenes PNG realmente recibidas y examinadas visualmente en esta conversación, no inferidas. **Lote anterior:** [B1/B2, 19 capturas](01-auditoria-visual-b1-b2-2026-10-13.md).  
**Estado:** 5/5 PNG recibidos, verificados y con SHA-256 registrado; **los bytes de las imágenes B3 aún NO están versionados en GitHub**. Un paquete ZIP y manifiesto CSV se prepararon para importación local segura.

| N.º | Archivo canónico | SHA-256 | Dictamen |
|---|---|---|---|
| 01 | `B3_01_Linea_Base_Observabilidad_ICMP.png` | `f116b30acbaa90f48ede64a2ae86c8ddd606b21eae413d1757138b5a2b7093f5` | **VÁLIDA**. Fecha, hostname, muestras 76, éxitos 76 y rutas en 5 fases, inicio/fin visibles |
| 02 | `B3_02_API_y_Metricas_Historicas.png` | `d1be1e1bbcc66c624b196cc5b7ee51189f7eef5dd79a1fcd4cb7ee60595c2ed8` | **VÁLIDA**. Salud JSON `mode: historical`, `live_monitoring:false`, origen CSV, 76 muestras y series `netlab360_icmp_samples/losses`, con marcadores |
| 03 | `B3_03_Panel_NOC_Historico-1.png` | `70070e4b0888b45f9151f013c417a605906bf424f691db31e3368480a1398115` | **VÁLIDA**, parte 1/2. URL local `127.0.0.1:8765`, banner *HISTÓRICO · NO EN VIVO*, 76/76/0 y barras de 5 fases |
| 04 | `B3_03_Panel_NOC_Historico-2.png` | `7fa431cc366bbef73471f833cbfcceda5c7212401a58d05c2990a4e9eb81efbd` | **VÁLIDA**, parte 2/2. Tabla por estado WAN, FIB `wan-p/wan-b`, fuente CSV original y enlaces /api/v1/baseline, /metrics y /healthz |
| 05 | `B3_04_Postcheck_Servicio_NOC.png` | `6b2c70cc802c0cebbef1f889463204155945293f7dd5570b3b5b6bdfc22e3d1c` | **VÁLIDA DIAGNÓSTICA** del estado intermedio: a las 15:52:24 `PUERTO_8765_LIBRE: NO`; Docker/netns vacíos, ens33 `192.168.47.40/24`, GW `192.168.47.2`, servicios activos, Git limpio |

### Cierre posterior comprobado

El usuario aportó posteriormente **salida real de terminal a las 16:09:58** con `PUERTO_8765_LIBRE: SI`, contenedores y namespaces vacíos y red de administración preservada. Esa salida **supersede el estado del puerto mostrado en B3_04**, pero **no es una captura PNG recibida**. Por eso B3_04 mantiene su nombre y su clasificación de diagnóstico; no alterarla para simular un postcheck que ocurrió después. La tercera terminal Windows probablemente corresponde al túnel `ssh -N -L 8765:127.0.0.1:8765 netlab360`; si permanece abierta, basta `Ctrl+C` en esa ventana de PowerShell. No detener procesos de la VM de forma indiscriminada.

### Valor probatorio exacto

- **B3-01:** análisis histórico reproducido desde 76/76 sondeos del CSV B2, 0 pérdidas en los instantes medidos.
- **B3 API:** `/healthz`, `/api/v1/baseline`, `/metrics` y `/` consultados exitosamente (HTTP 200); `404` a URL inexistente y `405` a POST según salida original; imágenes B3_02/03 corroboran payloads y presentación.
- **NOC histórico visible:** HTML accesible por loopback/túnel SSH, tarjetas, gráfica y tabla verificadas. **No son datos en vivo, ni Prometheus con scrape, ni alarma WAN conectada.**
- **Pendiente:** capturar el postcheck final con `PUERTO_8765_LIBRE: SI` solo si se necesita imagen ilustrativa para informe; la salida posterior ya soporta técnicamente la liberación de puerto, sin reejecutar servidor.
- El ZIP conserva los cinco PNG **sin modificar sus píxeles ni bytes**; dos fragmentos `B3_03` se guardan separados, sin montaje artificial. SHA256 ZIP **`747edb1eeee115e9bcbd68c64d50c043692b0015d76781416fd74da13921695e`**. Manifestación en CSV: nombre de columna `canonico` y `sha256`, archivos internos bajo `capturas/`.

**Estado Git:** usuario logró preparar/stage 19 capturas del lote 01 y validó `CAPTURAS_VERIFICADAS: 19`, `SHA256_ARCHIVOS: OK`, pero `git commit` **FALLÓ por `user.name/user.email` sin configurar**. El mensaje `Everything up-to-date` en `git push` confirma que NO se publicaron los 19 PNG todavía. Corregir identidad **solo a nivel de este repositorio** (preferentemente con login e ID públicos del usuario autenticado a `gh` para noreply), commitear stage, sincronizar vía `git fetch` + `git rebase origin/main`, push y verificar. Recién entonces marcar lote 01 físicamente publicado. El lote 02 B3 aún necesita transferencia y commit separados.

**Issue:** [#43](https://github.com/recm0708/netlab360/issues/43) permanece ABIERTA hasta incorporación de ambos lotes y auditoría de pendientes posteriores.
