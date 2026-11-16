# NETLAB360 — S04 lote 02 publicado y primer histórico G4 confirmado

**Fecha de operación:** 27/10/2026, hora Panamá. **Fuente:** resultados reales entregados por el operador para los pasos 4.39–4.40 y contraste remoto GitHub.

## Publicación de evidencias — finalizada

- Rama operativa `evidencias/s04-lote02-20261027`, commit inicial `58bac86`, `git diff --cached --check=0` tras convertir únicamente CSV CRLF→LF, ocho registros preservados, **PNG inalteradas**.
- Auditoría Ubuntu: `S04_LOTE02_PNG_AUDITADAS=8/8`, primer manifiesto S04 7/7, segundo 8/8, `FASE_4_PNG_VERSIONADOS=15`, `AUDITORIA_CAPTURAS_POR_FASE=OK`, `2/2` tests de inventario.
- [PR #67](https://github.com/recm0708/netlab360/pull/67) fusionado en `main`, commit `81519014166721ed2af35e26c029aacc7e3fe954`. **Inventario remoto de carpetas corroborado:** S01=90, S02=9, S03=8, S04=15, S05–S08=0. **TOTAL=122 PNG auténticas publicadas**.
- La verificación de rutas y manifiesto de PR #67 se comprobó remotamente. **GitHub Actions no se disparó para PR #67**: workflows existentes tenían filtros de rutas que excluían `evidencias/**`. No registrar resultado de CI inexistente para ese PR.
- Este incremento incorpora `.github/workflows/ci-evidencias.yml`: `pull_request` y `push` de `evidencias/**`, tests y validador, con verificación SHA256/dimensiones e inventario en CI. El **estado de aceptación del nuevo workflow** depende de resultados de su propio PR y posterior push, no se presume anticipadamente.

## G4 — primer ensayo histórico Prometheus, sin reinicio

- Consulta real `/api/v1/query_range` de `netlab360_s04_wan_admin_up{site="HQ",interface="s1p"}` en ventana UTC **2026-10-27 06:04:45 a 06:07:00**, paso 2 s: **1 serie, 68 muestras**, contiene al menos un `0` (DOWN) y un `1` (UP).
- Consulta simultánea `ALERTS{alertname="NETLAB360S04WANAdminDown",alertstate="firing",site="HQ",interface="s1p"}`: **1 serie, 28 muestras de valor 1** durante `firing`. `S04_G4_HISTORICO_WAN=CONSERVADO`, `S04_G4_CONSULTA_FINALIZADA=OK`.
- Esta evidencia acredita **historial de la incidencia en la TSDB mientras Prometheus está ejecutándose** y correlación con G3. No prueba reinicio/persistencia posterior, cobertura a largo plazo, exportación de logs ni historial durable web. La configuración actual usa retención TSDB **1 día** (`--storage.tsdb.retention.time=1d`).
- El log original G3 se verificó anteriormente con SHA256 `6e799191c7237145b30459ba201bca261e9517fefcfee223d92a36a27c29b7b3` fuera de Git; pendiente definir su tratamiento de entrega/retención.

## Estado y próximo corte

- **G0–G3 acreditadas en laboratorio** (G3 incluyó postcheck OSPF FULL 4/2/2, rutas FIB 6/6, loopbacks 6/6, LAN 9/9 gateways y cruces 6/6, gestión intacta).
- **G4 PARCIAL:** histórico actual de Prometheus confirmado; falta verificación controlada tras reinicio y simulación segura de fuente UNKNOWN/scrape ausente, sin inducir fallo de WAN ni LAN.
- **G5/G6 ABIERTAS:** historial de alertas visible permanentemente en NOC, SLI/SLO, notificación por decisión de alcance, resultados adicionales y texto del informe único.
- Mantener exporter 9110 y NOC 9120, Prometheus 9091 y topología FRR/WAN/LAN activos hasta preparar verificaciones seguras. La próxima interrupción de Prometheus, si se hace, debe ser **controlada**, no reiniciar contenedores FRR; usar Terminal 3 y después validar retorno de datos e histórico. No fabricar métricas.
