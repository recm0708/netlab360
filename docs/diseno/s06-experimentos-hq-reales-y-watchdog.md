# Intervención controlada y watchdog del cliente HQ — Fase 06

## Descripción y alcance

S06-041 está **ejecutado y aprobado en Ubuntu**: `S06-041_DATASET_Y_ML_VALIDADO=OK`, RC 0, 60 ventanas NORMAL de egreso HQ verificadas (120 mediciones ICMP reales), dos IsolationForest (HQ→S1/S2) entrenados en sesiones A/B con 40 observaciones por destino y evaluados en sesión TEST distinta con 20 observaciones por destino. FPR normal HQ→S1: IF 5 % vs regla P95 15 %; HQ→S2 ambos 5 %. No existe recall/F1 válido hasta tener degradaciones reales.

El experimento S06-040B probó un watchdog tras caída SIGKILL en una veth **aislada** y sus recursos ya fueron eliminados. La infraestructura real del proyecto es la topología S02–S05 formada por 21 namespaces, routers FRR, VLANs, WAN, HA/LACP/SDN y clientes con comunicación multisede. La petición actual es **NO crear interfaces dummy, namespaces nuevos, veth ficticias ni más redes de prueba**. S06-042 actúa sobre un **único cliente ya existente** de esa topología: `nl360-s02-h-hq-120/eth0`, IPv4 `10.70.20.20/24`, gateway `10.70.20.1`, peer switch `nl360-s02-sw-hq`. No interviene `ens33`, routers, switches ni otros clientes.

## Política de intervención

Una copia instalada y cotejada del ejecutor Python `scripts/s06/controlador_hq_protegido.py` debe ser propiedad root y modo 0750 en `/usr/local/libexec/netlab360/s06-hq-controlador.py`. El usuario no pasa namespace, dispositivo, dirección, handle o retardo: están **fijados en código**. Aprobación por ejecución mediante la cadena literal `AUTORIZO_HQ_VLAN120_NETEM_40MS_35S`. Esta autorización corresponde exclusivamente al ensayo de latencia durante 35 segundos; no permite acceso al host de gestión, ni cambios posteriores automatizados.

**Antes de tocar tc:** comprobar gestión `ens33 192.168.47.40/24`, gateway `192.168.47.2`, exactamente 21 namespaces originales, qdisc root `noqueue`, tipo `veth` y peer esperado, IP y rutas efectivas hacia `10.71.20.20`/S1 y `10.72.20.20`/S2, siete servicios y NOC saludables. Bloquear si hay un estado anterior o qdisc existente/ajena. Se instala un timer systemd root independiente y **se comprueba activo** antes de añadir exactamente `netem handle 142:` `delay 40ms` en `eth0` del cliente HQ. TTL de 35 segundos. No se agregan pérdidas ni cortes de enlaces. El estado/lock están en `/run/netlab360-s06-hq` como root 0700/0600.

El watchdog (`expire --token`) espera lock, valida identidad del namespace e identidad de qdisc (tipo, handle y delay), elimina solo la cola identificada y comprueba retorno a `noqueue`, registrando `RESTORED`. Nunca depende de NOC/Prometheus para decidir restaurar, porque el propio estímulo podría afectar su salud. Si la qdisc fue modificada de forma ajena se registra `ESCALATED`, no se elimina a ciegas. **No borrar el estado si el experimento no está restaurado.** Se incluye el comando protegido de emergencia `restore-now --token <token> --approve AUTORIZO_HQ_VLAN120_NETEM_40MS_35S`, que invoca el mismo rollback con registro `restoration_trigger=MANUAL_APPROVED`; no permite elegir interfaz ni borrar qdisc ajena. El timer sigue siendo independiente como respaldo. El token se obtiene exclusivamente del estado del ensayo actual; no reutilizarlo.

`cleanup` solo retira el archivo de estado protegido tras validar `RESTORED` o `RESTORED_NO_CHANGE`, qdisc basal, rutas y NOC sanos; **nunca elimina interfaces ni namespaces**.

## Etiquetado independiente

`scripts/s06/capturar_ventanas_controladas.py` es observacional. Captura dos rutas de ICMP de bajo volumen antes/durante/después de la intervención, con autorización root separada. Por ventana, registra el estado firmado operacionalmente por el controlador root y las rutas de salida tanto **antes como después** de la medición.

- `DEGRADED`: ambos extremos de la ventana presentan estado root `APPLIED`, qdisc `OWN_NETEM`, token/identidad constantes, marca de aplicación del controlador y rutas correctas; mediciones válidas. El RTT **no determina** esta etiqueta.
- `RECOVERY`: ambos extremos muestran `RESTORED`, qdisc `BASELINE`, marcas UTC de aplicación y expiración reales, ruta correcta y observaciones válidas. No se inventa recuperación desde un estado `RESTORED_NO_CHANGE`.
- Si cualquiera de las condiciones falta, se etiqueta `UNKNOWN`. En particular, cuando el temporizador expira DURANTE una medición, su ventana se conserva pero no se utiliza como ground truth supervisado.
- La clase previa `NORMAL` tiene alcance operacional restringido a egreso HQ sin netem y estado de rutas/NOC esperado. La clase `FAULT` no está autorizada aún; no se infiere por RTT alto.

Las observaciones contienen features de RTT, pérdidas y variación independientes de las etiquetas y de la información del controlador. Ningún token, estado root, qdisc, ventana temporal o campo de etiqueta puede alimentar el modelo como feature. Todos los JSONL originales se conservan privados e íntegros.

## Procedimiento seguro

1. **Auditoría sin cambio** de restos de los laboratorios antiguos: buscar `nl360-s06-*` y tipos dummy en host y 21 namespaces; si hay elementos inesperados, detenerse antes de cualquier borrado, identificar propietario y dependencias. No eliminar recursos legítimos.
2. Verificar `main`, sintaxis, pruebas CI y pruebas específicas, red management, qdisc HQ y salud de servicios.
3. Instalar el controlador y comprobar propietario/mode/digest, ejecutar `audit` de solo lectura. Si falla, detener la intervención.
4. Confirmar las ventanas NORMAL verificadas de referencia.
5. Ejecutar **una primera intervención autorizada**, capturar 3 a 5 ventanas DEGRADED mientras el timer de 35 s continúa activo. No repetir automáticamente la prueba si existe anomalía.
6. Verificar transiciones `APPLIED`→`RESTORED`, qdisc `noqueue`, rutas y Prometheus, capturar ventanas RECOVERY, archivar reporte root y bitácora.
7. Solo al comprobar restauración real, ejecutar `cleanup` y validar gestión, 21 namespaces, 4 Docker y NOC 18 nodos/21 enlaces.
8. Analizar las etiquetas y ventanas; repetir ciclos separados con aprobación nueva y sin mezclar entrenamiento y test únicamente después de aceptar el primero.

## Seguridad y limitaciones

El cambio actúa sobre un cliente de la topología de laboratorio; **no es una red empresarial real**, pero sí es tráfico y configuración reales del proyecto. Se tolera una latencia temporal breve de 40 ms desde el cliente HQ VLAN120; no es un corte WAN, fallo de OSPF ni pérdida de paquetes deliberada. No ejecutarlo si hay trabajo sensible o servicios críticos en ese cliente.

La qdisc de Linux no almacena propietario de la aplicación. La comprobación del handle y del retardo es una restricción del entorno, no defensa frente a modificaciones concurrentes arbitrarias de root. Es imprescindible no usar simultáneamente otras herramientas tc sobre el mismo dispositivo. Frente a `ESCALATED`, conservar estado y diagnosticar; no lanzar `tc qdisc del` a ciegas.

Las primeras sesiones permitieron observar **DEGRADED/RECOVERY reales del cliente de laboratorio**. Para entrenar y medir generalización se requieren varias sesiones independientes por clase, split por sesión/tiempo y TEST no visto; no calcular F1/recall sobre un solo experimento. La inferencia se mantiene de solo lectura; la actuación supervisada requiere aprobación individual y catálogos de acciones autorizadas.

## Validación

El lote completo S06-042 terminó en `S06-042_EXPERIMENTO_REAL_VALIDADO=OK`, RC 0, con fuente `main=2ffe8fd`, script root íntegro, 26 pruebas de guardia y 16 del recolector correctas, CI previa de 644 pruebas. Se verificaron 21 namespaces, cuatro Docker, ausencia de dummy/S06 temporal, `ens33 192.168.47.40/24` gateway `.2` y `eth0` de cliente HQ conectado a switch original; 7 servicios y Prometheus siguieron disponibles.

El token usado `b3484afcd16995a4` solo identifica el **experimento histórico**; no es válido para nuevas sesiones. El timer se armó antes de `netem 40ms` handle `142:`, expiró autónomamente y registró `RESTORED` a `2026-11-23T07:04:20.031+00:00` y `final_qdisc_state=BASELINE`, seguido de `cleanup=OK` y `state=NONE`. El estímulo generó `S06_WINDOW_DEGRADED_20261123T070344Z_984563` con 4/4 ventanas, 8 mediciones ICMP, RTT medio 40.440 ms. La fase posterior `S06_WINDOW_RECOVERY_20261123T070420Z_6c4e05` produjo 6/6 ventanas, 12 ICMP, RTT 0.070 ms. Ninguna de estas ventanas se ha presentado como puntuación F1 o recall sobre test externo.

Los registros originales se conservan fuera del repositorio. [Evidencias S06](../../evidencias/capturas/fase6/README.md).

La extensión multisesión se documenta en [adquisición experimental multisesión](s06-lotes-multisesion-hq.md).
