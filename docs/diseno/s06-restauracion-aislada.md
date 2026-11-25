# Restauración de qdisc en namespace aislado

## Antecedente

S06-038A aprobó en Ubuntu 21 pruebas específicas y 499 globales, instalación root 0750 de guardia protegida, temporizador independiente `netlab360-s06-guard-cf7b78e1daea9747` y transición `EXPIRED_NOOP` a estado final `NONE`. `ens33 192.168.47.40/24`, gateway `192.168.47.2`, `nl360-s02-h-hq-120/eth0` con qdisc noqueue, 21 namespaces, cuatro contenedores y siete servicios permanecieron intactos.

La prueba NOOP no demuestra una restauración real de qdisc. S06-038B introduce una **prueba aislada** antes de cualquier intervención en clientes o enlaces reales de NETLAB360.

## Alcance físico y lógico

Se crea solo el namespace temporal **nl360-s06-isotest**, con una interfaz **dummy0** tipo dummy, sin dirección IPv4/IPv6 asignada, ruta default, veth, bridge ni salida de red. No se conecta a ninguna de las 21 redes namespace de producción, a VMware, Docker, FRR ni LACP/SDN.

Una copia root-owned del ejecutor se instala en `/usr/local/libexec/netlab360/s06-rollback-isotest.py` con permisos `0750`. Está fijada a los nombres anteriores: no recibe nombre de interfaz, namespace, IP, comando shell o parámetros de netem desde usuario o interfaz web.

El único cambio de colas permitido será agregar en **dummy0** una qdisc netem con identificador `106:` y latencia nominal de 20 ms; sin tráfico de aplicación. El watchdog independiente de systemd se programa **antes** de agregarla, con TTL fijo de 20 segundos. Al vencer, un proceso privilegiado independiente contrasta namespace, interfaz y qdisc con el registro de propiedad root; únicamente si `kind=netem` y `handle=106:` coinciden, ejecuta la eliminación de la raíz sobre dummy0, confirma retorno a `noqueue` y registra `RESTORED`. Si la qdisc es ajena o hay ambigüedad, deja `ESCALATED` sin eliminarla.

La qdisc no lleva un campo de propietario real en el kernel. El registro root y handle `106:` proporcionan una **comprobación operativa restringida** al namespace nuevo; no serían suficientes por sí solos para autorizar degradaciones en interfaces productivas. S06-038B no otorga esa autorización.

## Contrato de estados y pasos

| Acción | Condiciones | Resultado |
|---|---|---|
| prepare | Gestión intacta, inventario 21 namespaces, namespace de prueba ausente y sin estado root previo | Crea namespace temporal aislado y dummy0; qdisc inicial noqueue; estado PREPARED |
| start | Estado PREPARED, namespace propio, qdisc noqueue, gestión intacta | Arma timer de 20 s, comprueba timer activo, agrega netem 106: en dummy0 y registra APPLIED |
| expire (solo timer) | Token generado y estado ARMADO/APLICADO, identidad de namespace coincidente | Elimina únicamente netem propio en dummy0; RESTORED. Si no hay cambio: RESTORED_NO_CHANGE. Estado extraño: ESCALATED |
| status | Solo lectura | Devuelve estado, token y qdisc aislada |
| cleanup | Estado RESTORED o RESTORED_NO_CHANGE, identidad y qdisc basal verificadas | Elimina dummy0 y únicamente nl360-s06-isotest; conserva lock y elimina estado efímero |

Los archivos privados de estado y lock viven en `/run/netlab360-s06-isotest/`, propiedad root y modos 0700/0600. No se agregan reglas sudoers ni cuentas nuevas.

## Condiciones de aborto

- No ejecutar `prepare` si el namespace temporal ya existe o la topología no tiene los 21 namespaces esperados.
- No ejecutar `start` si el temporizador no pudo programarse y verificarse activo. El estado queda preparado para inspección.
- Si el watchdog no confirma RESTORED, **NO ejecutar cleanup**, **NO borrar el namespace** y **NO intervenir manualmente qdiscs ajenas**; conservar bitácora y estado para diagnóstico.
- El estado de ARMING/APPLY_UNKNOWN/ESCALATED requiere revisión. No apagar ni reiniciar la VM durante el experimento; el timer es transitorio.
- Nunca ejecutar las opciones en un namespace que no sea el temporal aislado. El ejecutor aislado no debe utilizarse en el cliente HQ.

## Procedimiento de validación

1. Sincronización de `main`, prueba sintáctica, pruebas específicas y regresión global.
2. Comprobar gestión, 21 namespaces y estado de qdisc noqueue en el cliente HQ; comparar servicios.
3. Instalar una copia exacta del nuevo script root-owned modo 0750, sin reemplazar la guardia de S06-038A.
4. `prepare` y comprobar dummy0 sin IP, sin ruta default, qdisc noqueue y **22 namespaces temporalmente**.
5. `start` y verificar que el timer se arma ANTES de agregar la qdisc netem 106: en dummy0.
6. Esperar `RESTORED` o `RESTORED_NO_CHANGE`, que deberá documentarse como comportamiento observado y no asumido. Confirmar `noqueue` en dummy0.
7. `cleanup` y verificar que los namespaces vuelven a 21, sin residuos del namespace temporal, topología original intacta, 4 contenedores, 7 servicios, NOC, Prometheus y `ens33` intactos.
8. Guardar bitácora y verificación privada, incluyendo datos del estado y del temporizador. Si no llega a RESTORED, abortar sin cleanup.

## Resultados y limitaciones

S06-038B confirmó 24/24 pruebas específicas y 523/523 offline. El temporizador de 20 s se armó antes de aplicar netem al dummy0, registró RESTORED y verificó noqueue. La limpieza devolvió el inventario a 21 namespaces, con cuatro contenedores y gestión intactos. La prueba aislada no autoriza una intervención en el cliente HQ ni genera etiquetas de entrenamiento. [Auditoría del cliente](s06-auditoria-preintervencion.md).
