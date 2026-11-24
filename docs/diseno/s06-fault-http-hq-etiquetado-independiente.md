# Falla HTTP HQ y etiquetado independiente — Fase 06

## Descripción y alcance

El cierre científico V2 verificó la clasificación de **degradación artificial de latencia ICMP de 40 ms**, pero esa perturbación no acredita una falla de servicio. Para evaluar una falla de servicio independiente, empleamos el backend HTTP propio de la fase 05, con frontal HQ, respaldo S1 y NOC de la fase 05 como fuente observacional, **sin intervenir WAN, FRR/OSPF, LACP, OpenFlow, Docker, namespaces ni `ens33`**.

El precheck no invasivo del 23/11/2026 fue satisfactorio (`S05_HA_INSTANCIA_PREFLIGHT=OK_SOLO_LECTURA`), con seis servicios HA/NOC y exporter activos, 21 namespaces, cuatro Docker, FIB `S1=s1p` / `S2=s2p` y guardia de experimentación HQ `NONE/BASELINE`. Dos ciclos HA de la fase 05 históricos del 11 y 15 de noviembre mostraron secuencia BACKEND_HQ → BACKEND_S1 → BACKEND_HQ y FIB conservada; son **contexto histórico, no nuevas muestras de la fase 06 ni TEST ML**.

## Procedimiento del ensayo de falla HTTP de la fase 06

Se utiliza el procedimiento ya validado `scripts/operacion/s05-lote-ha-instancia-con-watchdog.sh --run --confirm-fault`, **solo con autorización humana expresa en terminal y precheck vigente**. El script de la fase 05 arma **un temporizador systemd autónomo de 120 segundos** para arrancar `netlab360-s05-ha-backend-hq.service` incluso si se pierde SSH; durante el experimento apaga únicamente el backend HQ, observa la transición por NOC al respaldo S1 por ocho segundos y restaura HQ. Después verifica seis unidades activas, rutas de gestión, FIB, cancela el timer y registra los marcadores de éxito. Una eventual falla preserva el rescate; no repetir ni cancelar manualmente el temporizador ante `ESCALATED` o error. El experimento induce temporalmente una falla de **backend HQ**, no una caída completa del HTTP frontal, que debe permanecer disponible.

## Validación de evidencia externa y etiquetas

`scripts/s06/validar_fault_http_s06.py --log RUTA_LOG --save` es **de solo lectura** sobre el JSONL generado en `~/netlab360-bootstrap/s05/evidencias/ha-noc` y la bitácora de autorización/rescate de la fase 05. Comprueba que la evidencia es cronológicamente posterior al TEST V2 y proviene del procedimiento específico, con `systemctl stop` controlado, watchdog armado y cancelado, secuencia exacta BACKEND_HQ → BACKEND_S1 → BACKEND_HQ, tiempo UTC monotónico, frontal HQ activo, backend HQ no activo en fase S1 y FIB WAN conservada. Solo tras esta validación emite un JSON privado nuevo `~/netlab360-bootstrap/s06/estudio-uniforme-v2/fault-http-s06/S06_FAULT_HTTP_HQ_<UTC>.json` con tres grupos **NORMAL_HTTP_HQ**, **FAULT_HTTP_BACKEND_HQ**, **RECOVERY_HTTP_HQ**.

El archivo de procedencia es **una evaluación de estados del servicio distinta de los datos ICMP**. No se puede fusionar al TEST V2, hacer inferencia con LogisticRegression/P95 RTT sobre FAULT sin nuevos features/etiquetas ni presentar esta prueba como verificación de predicción futura. El ground truth proviene del control explícito del servicio y del NOC, no de los mismos valores RTT utilizados para clasificar.

El modo `--check` verifica posteriormente el JSON guardado frente a las fuentes originales, sin modificar los modelos ni los datos. Una validación fallida no elimina evidencia ni altera la red. No reutilizar archivos anteriores ni repetir una ejecución fallida sin diagnóstico.

## Criterios de aceptación

Se considera validado el segundo escenario si `S06_FAULT_HTTP_VERIFICADO=OK`, el informe presenta muestras normal/falla/recuperación con procedencia fiable, el watchdog recuperó HQ y se conservan NOC, Prometheus, LACP/SDN, qdisc noqueue, la ruta administrativa y los cuatro modelos V2 congelados. La cobertura real quedaría delimitada a **falla HA del backend HTTP HQ y latencia controlada del cliente HQ**. Otros fallos físicos y fallas de OSPF/WAN/SDN quedan no evaluados, así como pronóstico de horizonte futuro, MAE y concept drift inferencial.



## Resultados

**Ensayo realizado una sola vez y aceptado en VM.** El operador autorizó expresamente `AUTORIZO_FAULT_HTTP_HQ_CON_RESCATE_120S`; el procedimiento de la fase 05 armó un watchdog autónomo de 120 s, detuvo el backend HTTP HQ, observó el respaldo S1 y restauró HQ antes de cancelar el temporizador. La bitácora original informó `S05_HA_CICLO_RC=0`, `S05_HA_CICLO_INSTANCIA=HQ_S1_HQ_OK`, FIB S1 `s1p` y S2 `s2p`, frontal disponible y gestión intacta. El JSONL del NOC contiene **19 observaciones** en transición HQ → S1 → HQ: **2 NORMAL_HTTP_HQ, 15 FAULT_HTTP_BACKEND_HQ, 2 RECOVERY_HTTP_HQ**. Procedencia: `S05_HA_NOC_CICLO_20261123T173926Z.jsonl` bajo `~/netlab360-bootstrap/s05/evidencias/ha-noc/`.

La validación de los registros originales se efectuó mediante --save y --check; ambas verificaciones confirmaron S06_FAULT_HTTP_VERIFICADO=OK. No se repitió la intervención. El informe privado se conserva en fault-http-s06.

**Integridad y regresión verificadas:** comprobaciones de integridad de `TEST_Manifest.json`, `validation.json`, `test.json`, `auditoria-cientifica-final.json` y `S06_V2_Training_Freeze.json` todas OK; cuatro modelos V2 congelados y legacy conservados; seis unidades HA/NOC/exporter activas; `healthz` saludable; 21 namespaces, cuatro contenedores, `ens33 192.168.47.40/24`, ruta por `192.168.47.2`, controlador `NONE/BASELINE`, qdisc `noqueue` y repositorio limpio. La [regresión transversal](s06-estados-ia-y-observacion-lacp-sdn.md) verificó LACP/SDN, OSPF y Prometheus.

**Alcance y límites:** se verificó una clase FAULT del **backend HTTP HQ**, no caída del frontal ni del enlace WAN, ni falla de OSPF/LACP/SDN. Es ground truth adicional separado del TEST ICMP V2; no demuestra que P95, IsolationForest o LogisticRegression detecten este FAULT, ni pronóstico con horizonte, MAE o concept drift inferencial. [Evidencias de la fase 06](../../evidencias/capturas/fase6/README.md).
