# S05 — Corrección de evidencia 60 y pausa VMware (15/11/2026)

El operador confirmó el lote 134A OK: 10/10 tests, OpenFlow conectado, 25 reglas, segmentación funcional, ens33 192.168.47.40/24 y Git limpio.
El lote 134B NO terminó: el ping negativo A→C devolvió RC1 y `10 packets transmitted, 0 received, +10 errors, 100% packet loss`, pero el verificador esperaba `2 transmitted` y omitía el campo `+10 errors`; el marcador FIN_CAPTURA_60/LOTE134B OK no se generó. Reintentos posteriores encontraron el mismo caso y uno sufrió desconexión SSH. El lote 134C sigue pendiente.

**Corrección:** el parser de iputils reconoce opcionalmente `+N errors`; para tráfico denegado exige que ping termine RC1, `received=0`, pérdida 100%, y entre 2 y 32 paquetes enviados (pueden aumentar cuando el kernel reintenta ARP/host unreachable). Para A→B mantiene enviados=2, recibidos=2, RC0 y 0% pérdida. RC124, RC2 y timeouts no se consideran bloqueo. Tests adicionales reproducen literalmente la salida de 10 paquetes/10 errores y rechazo de RC124.

**Solicitud de operación:** el usuario necesita reiniciar Windows antes de completar la práctica. No realizar `reboot` dentro de Ubuntu: los namespaces S02/HA/LACP/SDN son efímeros. Una suspensión completa de `netlab360-lab` mediante VMware Workstation puede preservar RAM y procesos, pero depende de que VMware guarde correctamente `.vmss`/`.vmem` y del espacio libre en el volumen host. Riesgo residual de imagen suspendida corrupta y necesidad de reconvergencia de red tras reanudar; no prometer 100% de preservación.

**Antes de suspender**: confirmar que no hay tareas activas, guardar baseline y `sync` en guest, comprobar Git, Faucet active/OpenFlow, ens33 y namespaces, recursos de disco libres. En Windows comprobar espacio libre en el volumen de la VM mayor a RAM asignada + margen, suspender completamente desde VMware y esperar estado `Suspended`. Evitar `Pause`, `Power Off`, `Reset` y cierre forzado. Si existen otras VM en ejecución, dejarlas también seguras antes de reiniciar Windows. No borrar .vmss/.vmem/.lck.

**Tras reiniciar Windows**: abrir VMware, reanudar VM existente, reconectar SSH, comprobar hora, ens33, route via .2, FRR tres contenedores, namespaces, controlador OpenFlow, 3 agregadores HQ/S1/S2, seis servicios HA/NOC y los archivos de evidencia; detener cualquier automatización si hay diferencias. No ejecutar `up` ni `down` ni restaurar desde snapshots por defecto.

**Siguiente trabajo práctico**: ejecutar pruebas offline actualizadas, validación de captura 60 en un archivo NUEVO (no sobrescribir log 14 incompleto), obtener captura desde INICIO a FIN tras RC1/0 respuestas/100% pérdida, y completar regresión global / SHA256 con pruebas reales. No cerrar S05 ni declarar #105 completado hasta auditar PNG originales.

Fuente VMware: Workstation Pro documentación de vmrun suspend soft/hard; documentación Broadcom de estado suspendido y conservación de memoria. La suspensión hard evita scripts guest que modifican temporalmente la red, pero requiere especificar VMX correcto.
