# NETLAB360 — B4 perfil real y diagnóstico contextual (registro)

**Estado de ejecución 13/10/2026 23:12:45, Panamá:** operador completó pasos 192–201; evidencia proveniente de la salida de Ubuntu. Capturas PNG nuevas se enviarán después; no se recibieron en esta tanda.

## Perfil estadístico ejecutado y comprobado

- Pruebas Python: **16/16 OK**, código0.
- CSV original: 17-b2-convergencia-20261013-115141.csv, SHA-256 349643e93c3e5f69cd529508d2349be0ef570a3e0291d144344413fc2b373eb5, confirmado.
- Perfil: 76 muestras ICMP, 76 éxitos, 0 pérdidas detectadas por sondeo, 0 FIB inesperadas en fases estables. JSON local externo al repositorio, permisos 0600; validación exit0.
- NORMAL: n=14, ruta wan-p:14; RTT medio 0.031071 ms, p95 nearest-rank 0.049 ms.
- CAMBIO_RESPALDO: n=1, ruta wan-b:1; RTT medio 0.028 ms, p95 0.028 ms.
- RESPALDO: n=16, ruta wan-b:16; RTT medio 0.03075 ms, p95 0.041 ms.
- CAMBIO_PRINCIPAL: n=29, rutas wan-b:27 y wan-p:2; RTT medio 0.028793 ms, p95 0.038 ms.
- RESTAURADA: n=16, wan-p:16; RTT medio 0.028625 ms, p95 0.037 ms.
- Los 12 eventos JSONL B3 son de otras sesiones. **NO** son nuevas filas ICMP sincronizadas con B2.
- CI: runs 38509420496 y 38509454510 mostradas ✓ en consola del operador. Run 38508522760 comprobada además con gh run view --exit-status.
- Avisos anteriores: acciones GitHub con runtime Node20 obsoleto (no error) y futura migración ubuntu-latest. Workflow actualizado a actions/checkout@v5 y actions/setup-python@v6 (Node24), pero versión nueva pendiente de comprobar en Actions.
- Postcheck 23:12:45: Docker/netns sin residuos, gestión ens33 192.168.47.40/24, gateway .2, tres servicios activos, Git limpio.
- **S01 sigue 72/100 provisional**; no incrementar puntuación por estadística descriptiva ni por preparar código no ejecutado. B4 ML 0/5.

## Preparado en GitHub, no ejecutado

- scripts/analitica/b4-diagnostico-reglas.py: analiza el CSV original mediante referencia P95 de fase normal y tres reglas contextuales (ICMP fallido, FIB inesperada en fase estable, RTT sobre 3×P95 normal). Transiciones entre fases se registran como eventos operativos y NO como anomalías. Guardas SHA256, consistencia con perfil, salida JSON 0600 fuera del repo; jamás aplica cambios de red.
- tests/test_b4_diagnostico_reglas.py: 8 casos de prueba con datos artificiales exclusivos de tests. Se esperan 24 unit tests después de importar ambos archivos, sujetos a ejecución real.
- Regla RTT de referencia derivada de los mismos 14 datos normales de la misma sesión; es una **heurística in-sample** y NO un umbral estadístico poblacional confiable.
- **No** es IA/ML ni se han medido precision/recall/F1. El número de señales no es una tasa de falsos positivos.

## Protocolo futuro de datos para IA, aún no ejecutado

Para análisis ML defendible, se necesitan múltiples sesiones independientes con muestreo periódico real y marcas externas de intención de corte/restauración; RTT, ICMP, FIB y estado OSPF sincronizados; separación train/test por ensayo completo, nunca por filas contiguas; y comparación justa con detector determinista. Eventos exporter no pueden servir como ground truth si usan las mismas reglas evaluadas. No hace falta nueva falla WAN ni instalar sklearn para el siguiente bloque solo-lectura.

**Evidencias pendientes:** usuario enviará más tarde capturas IaC/B4; no pedirlas antes ni crear nuevo ZIP incompleto. Mantener issue #43 abierta.
