# S06 — FAULT HTTP HQ real, recuperación y separación frente a IA de RTT

## Justificación y alcance

El cierre científico V2 verificó la clasificación de **degradación artificial de latencia ICMP de 40 ms**, pero esa perturbación no acredita una falla de servicio. S06 necesita una segunda evidencia independiente de FAULT. Se emplea el backend HTTP propio de S05, con frontal HQ, respaldo S1 y NOC S05 como fuente observacional, **sin intervenir WAN, FRR/OSPF, LACP, OpenFlow, Docker, namespaces ni `ens33`**.

El precheck no invasivo del 23/11/2026 fue satisfactorio (`S05_HA_INSTANCIA_PREFLIGHT=OK_SOLO_LECTURA`), con seis servicios HA/NOC y exporter activos, 21 namespaces, cuatro Docker, FIB `S1=s1p` / `S2=s2p` y guardia de experimentación HQ `NONE/BASELINE`. Dos ciclos HA S05 históricos del 11 y 15 de noviembre mostraron secuencia BACKEND_HQ → BACKEND_S1 → BACKEND_HQ y FIB conservada; son **contexto histórico, no nuevas muestras S06 ni TEST ML**.

## Procedimiento del experimento S06 FAULT

Se utiliza el procedimiento ya validado `scripts/operacion/s05-lote-ha-instancia-con-watchdog.sh --run --confirm-fault`, **solo con autorización humana expresa en terminal y precheck vigente**. El script de S05 arma **un temporizador systemd autónomo de 120 segundos** para arrancar `netlab360-s05-ha-backend-hq.service` incluso si se pierde SSH; durante el experimento apaga únicamente el backend HQ, observa la transición por NOC al respaldo S1 por ocho segundos y restaura HQ. Después verifica seis unidades activas, rutas de gestión, FIB, cancela el timer y registra los marcadores de éxito. Una eventual falla preserva el rescate; no repetir ni cancelar manualmente el temporizador ante `ESCALATED` o error. El experimento induce temporalmente una falla de **backend HQ**, no una caída completa del HTTP frontal, que debe permanecer disponible.

## Validación de evidencia externa y etiquetas

`scripts/s06/validar_fault_http_s06.py --log RUTA_LOG --save` es **de solo lectura** sobre el JSONL generado en `~/netlab360-bootstrap/s05/evidencias/ha-noc` y la bitácora de autorización/rescate S05. Comprueba que la evidencia es cronológicamente posterior al TEST V2 y proviene del procedimiento específico, con `systemctl stop` controlado, watchdog armado y cancelado, secuencia exacta BACKEND_HQ → BACKEND_S1 → BACKEND_HQ, tiempo UTC monotónico, frontal HQ activo, backend HQ no activo en fase S1 y FIB WAN conservada. Solo tras esta validación emite un JSON privado nuevo `~/netlab360-bootstrap/s06/estudio-uniforme-v2/fault-http-s06/S06_FAULT_HTTP_HQ_<UTC>.json` con tres grupos **NORMAL_HTTP_HQ**, **FAULT_HTTP_BACKEND_HQ**, **RECOVERY_HTTP_HQ**.

El archivo de procedencia es **una evaluación de estados del servicio distinta de los datos ICMP**. No se puede fusionar al TEST V2, hacer inferencia con LogisticRegression/P95 RTT sobre FAULT sin nuevos features/etiquetas ni presentar esta prueba como verificación de predicción futura. El ground truth proviene del control explícito del servicio y del NOC, no de los mismos valores RTT utilizados para clasificar.

El modo `--check` verifica posteriormente el JSON guardado frente a las fuentes originales, sin modificar los modelos ni los datos. Una validación fallida no elimina evidencia ni altera la red. No reutilizar archivos anteriores ni repetir una ejecución fallida sin diagnóstico.

## Aceptación y limitaciones

Se considera validado el segundo escenario si `S06_FAULT_HTTP_VERIFICADO=OK`, el informe presenta muestras normal/falla/recuperación con procedencia fiable, el watchdog recuperó HQ y se conservan NOC, Prometheus, LACP/SDN, qdisc noqueue, la ruta administrativa y los cuatro modelos V2 congelados. La cobertura real quedaría delimitada a **falla HA del backend HTTP HQ y latencia controlada del cliente HQ**. Otros fallos físicos y fallas de OSPF/WAN/SDN quedan no evaluados, así como pronóstico de horizonte futuro, MAE y concept drift inferencial.

Solo después se deben tomar las capturas finales necesarias y revisar el documento académico sin redundancia entre descripción metodológica, resultados y conclusiones; no cerrar issues S06 o milestone sin validar el evento real y el informe.

## Integración de código — antecedente previo a la ejecución

PR [#184](https://github.com/recm0708/netlab360/pull/184) fusionado como `215fa64`; **896 pruebas CI, 895 OK y una omitida**. El validador S06 registra estados de servicio NORMAL/FAULT/RECOVERY con procedencia `systemctl stop` + NOC + temporizador systemd de 120 s, y entonces el ensayo real permanecía pendiente. El resultado posterior se documenta en el cierre validado de este protocolo.

## Corrección del importador de sesiones (23/11/2026)

En la primera ejecución real, el lote se detuvo **antes de `--apply` de etiquetas y antes de FAULT**: `python3 -m unittest discover -s tests -p test_s06_fault_http_verificado.py` identificó dos errores `ModuleNotFoundError: auditar_gates_prospectivos`. El validador era importado por `importlib.util` en las pruebas aisladas y dependía erróneamente del PYTHONPATH. PR [#185](https://github.com/recm0708/netlab360/pull/185) fusionado como `12f7468`: se sustituyó la importación cruzada por un parser local de IDs UTC validado, se restauró y comprobó el patrón JSONL, y se agregaron tres pruebas. **CI 899 tests, 898 aprobados y uno omitido**. No se alteraron modelos, datasets, redes o servicios; la intervención todavía no se había realizado en esa primera ejecución.

## Ejecución S06 y aceptación real — 23/11/2026

**Ensayo realizado una sola vez y aceptado en VM.** El operador autorizó expresamente `AUTORIZO_FAULT_HTTP_HQ_CON_RESCATE_120S`; el procedimiento S05 armó un watchdog autónomo de 120 s, detuvo el backend HTTP HQ, observó el respaldo S1 y restauró HQ antes de cancelar el temporizador. La bitácora original informó `S05_HA_CICLO_RC=0`, `S05_HA_CICLO_INSTANCIA=HQ_S1_HQ_OK`, FIB S1 `s1p` y S2 `s2p`, frontal disponible y gestión intacta. El JSONL del NOC contiene **19 observaciones** en transición HQ → S1 → HQ: **2 NORMAL_HTTP_HQ, 15 FAULT_HTTP_BACKEND_HQ, 2 RECOVERY_HTTP_HQ**. Procedencia: `S05_HA_NOC_CICLO_20261123T173926Z.jsonl` bajo `~/netlab360-bootstrap/s05/evidencias/ha-noc/`.

El primer bloque S06 finalizó `RC=1` *después* de la recuperación por una comprobación textual `grep -Fxq` que no contemplaba los separadores del marcador `========== S05_LOTE_HA_INSTANCIA=OK ==========`; **no fue un fallo del ciclo HA y no se repitió**. Se reutilizó el registro original `~/netlab360-bootstrap/s06/estudio-uniforme-v2/S06_FAULT_HTTP_Ejecucion.txt` y se completó el validador S06 con `--save` y `--check`, ambos `S06_FAULT_HTTP_VERIFICADO=OK`, resultado final `S06_FAULT_RECUPERACION_FINAL=OK` y `RESULTADO_RC=0`. Informe privado: `~/netlab360-bootstrap/s06/estudio-uniforme-v2/fault-http-s06/S06_FAULT_HTTP_HQ_20261123T173926Z.json`; bitácora de cierre `~/netlab360-bootstrap/s06/cierre-fault-validacion-20261123T174603Z/S06_FAULT_Cierre_Validacion.txt`.

**Integridad y regresión verificadas:** comprobaciones de integridad de `TEST_Manifest.json`, `validation.json`, `test.json`, `auditoria-cientifica-final.json` y `S06_V2_Training_Freeze.json` todas OK; cuatro modelos V2 congelados y legacy conservados; seis unidades HA/NOC/exporter activas; `healthz` saludable; 21 namespaces, cuatro contenedores, `ens33 192.168.47.40/24`, ruta por `192.168.47.2`, controlador `NONE/BASELINE`, qdisc `noqueue` y repositorio limpio. La auditoría transversal actualizada de LACP/SDN, OSPF y Prometheus se realizará como comprobación posterior independiente.

**Alcance y límites:** se verificó una clase FAULT del **backend HTTP HQ**, no caída del frontal ni del enlace WAN, ni falla de OSPF/LACP/SDN. Es ground truth adicional separado del TEST ICMP V2; no demuestra que P95, IsolationForest o LogisticRegression detecten este FAULT, ni pronóstico con horizonte, MAE o concept drift inferencial. Las issues #6/#25/#26 y la milestone S06 siguen abiertas hasta reconciliar los criterios académicos, la regresión transversal y las evidencias.
