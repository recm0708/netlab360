# S06-040 — Recuperación de veth aislada tras caída del controlador

## Evidencia que habilita el diseño

S06-039 se ejecutó en Ubuntu con `S06-039_AUDITORIA_VALIDADA=OK`, RC 0, 19 pruebas propias y **542 globales** aprobadas. El cliente real `nl360-s02-h-hq-120` usa `eth0`, tipo **veth**, peer en `nl360-s02-sw-hq`, IPv4 `10.70.20.20/24`, gateway `10.70.20.1`; las rutas a S1 `10.71.20.20` y S2 `10.72.20.20` utilizan ese gateway. Qdisc noqueue, NOC, Prometheus y administración intactos. Seis controles de seguridad siguen pendientes y el auditor **no autorizó** intervenciones productivas.

En S06-038B el watchdog devolvió una qdisc netem real a noqueue en una interfaz dummy sin conectividad. Dado que el cliente real es veth, el siguiente gate requiere ensayar veth, con pérdida del proceso principal, sin tocar el cliente productivo.

## Aislamiento estrictamente acotado

El programa `scripts/s06/rollback_veth_aislado.py` crea **dos namespaces nuevos y separados de las 21 entidades NETLAB360**:

- `nl360-s06-veth-a` con `s06va0`, IPv4 `10.255.239.1/30`.
- `nl360-s06-veth-b` con `s06vb0`, IPv4 `10.255.239.2/30`.

Solo existe un **veth directo entre estos dos namespaces**. No hay veth al host inicial, al switch HQ, a FRR, Docker, HA, Faucet u otra sede. No se crean rutas default; IPv6 se desactiva en ambos extremos de prueba. IPAM productivo `10.70`, `10.71`, `10.72` y gestión `192.168.47` permanecen intactos.

La copia ejecutable es root-owned y modo 0750 en `/usr/local/libexec/netlab360/s06-veth-rollback.py`, con estado/lock root privado en `/run/netlab360-s06-veth/`. Se usan nombres e IP fijados por el código; no se aceptan argumentos arbitrarios de interface, root qdisc, ruta o dirección. No crear ni modificar este par si existe estado previo o si el inventario no contiene exactamente 21 namespaces originales.

## Operación prevista

1. `prepare`: comprobar gestión, namespace temporal inexistente, crear pareja veth y direcciones locales, revisar ausencia de rutas default, qdisc noqueue e ICMP entre extremos; inventario temporal 23 namespaces.
2. `start --crash-controller`: validar el entorno, generar y activar un timer independiente systemd con TTL **25 s** antes de agregar netem handle `140:` y latencia nominal 40 ms solo en `nl360-s06-veth-a/s06va0`. Después de guardar el estado APPLIED, matar deliberadamente **solo el proceso del controlador de este ensayo con SIGKILL**. Esto NO mata SSH, NOC, systemd ni procesos de red.
3. Medir ICMP desde A hacia B mientras netem está aplicado; observar el cambio de RTT sin presentarlo como degradación de la topología productiva.
4. Dejar vencer el timer systemd; este espera el lock si es necesario, valida token, identidad de ambos namespaces, interfaz y qdisc propia y restaura `noqueue`; si detecta configuración ajena o no puede restaurar registra `ESCALATED` y conserva estado.
5. `cleanup`: únicamente al comprobar `RESTORED`, qdisc noqueue y conectividad ICMP, elimina la pareja y **solo** esos dos namespaces; retorno a 21. No borra archivos originales S06 ni modifica servicios.

## Condiciones de aborto

**No ejecutar cleanup** cuando el estado sea `APPLIED`, `APPLY_UNKNOWN`, `ESCALATED`, `ARMED` o cualquiera diferente de `RESTORED`. No eliminar namespaces ni qdisc manualmente sin diagnosticar identidad y propiedad. Un fallo del timer debe conservar el estado, ser reportado y no debe provocar un cambio en los recursos originales de NETLAB360.

El ensayo no produce ground truth de sedes; `ground_truth_verified=false`. Se conserva la medición del par aislado exclusivamente como aceptación del mecanismo de seguridad, no como datos de entrenamiento. **Ninguna degradación de cliente HQ está autorizada.**

## Requisitos previos y posteriores

- Sintaxis, pruebas específicas, CI completa y estado Git limpio.
- Estado del cliente real HQ sigue noqueue, rutas y servicios correctos, ens33 .40 y gateway .2.
- Ejecutable protegido e idéntico a la versión de Git.
- El timer se programa ANTES de tc. SIGKILL afecta solo al controlador temporal; el sistema recupera por vía independiente.
- Confirmar RTT pre/intervención/post con sondas IP locales, un estado verificable RESTORED, archivo privado, cleanup a 21 namespaces, NOC 18/21, 4 Docker y 0 servicios fallidos.
- Prohibido habilitar automáticamente S07/S08 o etiquetas NORMAL/DEGRADED/RECOVERY en producción a partir de este ensayo.

Al superar S06-040 se podrá diseñar posteriormente el **verdadero ejecutor para un cliente veth productivo**, con aprobación humana por escenario, ensayos adversos de producción, control de ownership real y plan de contingencia manual. La prueba aislada por sí sola no concede autorización.
