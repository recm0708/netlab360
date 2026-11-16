# NETLAB360 — B4: auditoría real de fuentes, regresión y CI verificados

**Ensayo real:** 13/10/2026, 22:58–23:00 Panamá (UTC−05). **Fuente:** salida íntegra del operador pasos 181–191 y ejecución GitHub Actions comprobada por job. **No se recibieron aún PNG** (el usuario enviará las capturas de varios bloques posteriormente). **No se entrenó IA/ML.**

## Resultados objetivos

- `git pull --ff-only` terminó sin conflictos en commit `a6eaa91`; rama `main...origin/main` limpia. Ubuntu Python 3.14.4, OpenTofu 1.13.1, Ansible Core 2.20.1.
- Suite local `unittest discover`: **11/11 tests exitosos**, rc0, cubriendo inspección Docker B3, parser CSV/JSONL B4, compliance FRR y drift controlado de test.
- Se inspeccionaron 4 archivos físicos B4 en `~/netlab360-bootstrap/evidencias/` y se validaron SHA256:
  1. `17-b2-convergencia-20261013-115141.csv`: **76 filas**, SHA256 `349643e93c3e5f69cd529508d2349be0ef570a3e0291d144344413fc2b373eb5`, columnas `fecha_local,segundos_desde_inicio,sondeo,fase,interfaz_fib,icmp_ok,rtt_ms,codigo_ping`.
  2. `b3-resumen-convergencia.json`: **76 muestras derivadas, NO independientes**; SHA256 `7e929b087dbe2bb798702301ce6e20af9e9f0770831726d6e738f54a55e268d6`.
  3. `b3-wan-live-events-20261013-181205.jsonl`: **5 eventos**, SHA256 `0df023a04cf406bcdd8bf7fdfda6a51ad324da69d6522b99d8df259361b34332`.
  4. `b3-wan-live-events.jsonl`: **7 eventos**, SHA256 `6d665b853ad90e530521b97bdb86524b3ac815589afce52ca928633d8365c2ec`.
- Distribución 12 eventos observados en dos sesiones JSONL: `TOPOLOGY_STARTED=1`, `TOPOLOGY_STOPPED=2`, `WAN_PRIMARY_DOWN=2`, `WAN_PRIMARY_RESTORED=2`, `WAN_ROUTE_CHANGED=5`.
- Auditor `b4-auditar-fuentes-reales.py --save` terminó `AUDITORIA_B4_DATOS=OK`, exit0; JSON `~/netlab360-bootstrap/analitica/b4/inventario-fuentes-reales.json` válido y con permisos **0600**.
- La verificación de librerías encontró `numpy` disponible; `pandas`, `sklearn` y `matplotlib` no instaladas, sin necesidad de instalar ahora.
- **CI real verificada**: GitHub Actions run [38508522760](https://github.com/recm0708/netlab360/actions/runs/38508522760), job `offline-regression` id `115671442438`, `status=completed`, `conclusion=success`; cada paso Python syntax, IPAM, unittest y Bash syntax tiene conclusión success. El usuario intentó `gh run view --workflow` (flag no válido) y sustituyó el ID de ejemplo literalmente (404); **no son fallos de CI**. Comando correcto: `gh run view 38508522760 -R recm0708/netlab360 --exit-status`.
- Postcheck 23:00:02: Docker/netns vacíos, red ens33 `192.168.47.40/24`, GW `192.168.47.2`, servicios activos, Git limpio.

## Lectura metodológica y valoración

**No** existe corpus suficiente para evaluar un modelo supervisado: hay un único ensayo de 76 ICMP con fases operativas, más dos JSONL que **registran transiciones y no intervalos normales**. Las sesiones B2/B3 no están sincronizadas para fusión fila a fila. Tampoco hay etiquetas normales y anomalías independientes de las mismas reglas del exporter. No atribuir precision/recall/F1 ni 88 casos de entrenamiento. Se preservan hashes y fechas sin publicar automáticamente archivos reales en GitHub.

**Matriz:** documentación/CI 2→3 de 5 puntos por **CI real exitosa y tests regresivos**, S01 **71→72/100 estimado**. B4 sigue 0/5 hasta existir indicador diagnóstico evaluado; inventariar datos solamente no acredita IA. No cerrar S01 ni issues B4.

## Próxima fase preparada, NO ejecutada

- `scripts/analitica/b4-perfil-estadistico-real.py`: lectura validada de CSV según inventario hash, conteo ICMP por fase, media/mediana/p95 nearest rank/max de RTT, rutas FIB, desviaciones de FIB frente a expectativa operativa **en fases estables**; guardas de duplicados, tiempo y NaN, más reporte JSON 0600 externo.
- `tests/test_b4_perfil_estadistico.py`: cinco tests con fixtures **artificiales exclusivos de tests**, nunca se suman al dataset real.
- Ejecutar nueva regresión (esperado total 16 tests), `b4-perfil-estadistico-real.py --save`, verificar cifras/JSON y CI; comprobar que ninguna inferencia confunde fases de transición con anomalías independientes. Capturas `B4_04_Perfil_Estadistico_Real` con delimitadores.
- Luego diseñar recolección real con etiquetas externas de corte/restore, ventanas temporales y partición de train/test por **ensayo completo**. No provocar otra caída WAN ni instalar ML preventivamente; primero evaluar perfil.
