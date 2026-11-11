# NETLAB360 S05 · Diseño controlado de HA de servicios multisede

**Estado:** propuesta técnica, **no desplegada**; fase 5, issue #32. **Actualizado:** 2026-11-11. No asignar recursos hasta validar el precheck de la VM real.

## Alcance y propósito

Demostrar **alta disponibilidad lógica de un servicio HTTP** con dos instancias independientes y mecanismo de comprobación de salud y conmutación. Este trabajo es distinto del failover de WAN S1/S2 ya aprobado (conmutación OSPF por FIB). Se busca comprobar acceso HTTP desde otra sede antes, durante y después de detener una instancia, conservando el servicio mediante otra instancia. Una sola VM **no** prueba tolerancia a la pérdida física de la máquina VMware.

## Topología de referencia (candidata; NO operativa aún)

El inventario S02 y el precheck del 11/11 documentan tres sedes, tres FRR, tres switches por netns y nueve VLAN. Los siguientes elementos **no existen todavía en el diagrama del NOC**:

| Función | Namespace propuesto | Sede/VLAN | IP candidata | Estado |
| --- | --- | --- | --- | --- |
| Backend HTTP A (preferido) | `nl360-s05-ha-hq` | HQ / 120 | `10.70.20.21/24` | No creado |
| Backend HTTP B (reserva) | `nl360-s05-ha-s1` | S1 / 220 | `10.71.20.21/24` | No creado |
| Proxy de supervisión/frontal | `nl360-s05-ha-fe` | HQ / 120 | `10.70.20.23/24` | No creado |
| Cliente test intersede **existente** | `nl360-s02-h-s2-320` | S2 / 320 | `10.72.20.20/24` | Observado |

Los gateways S02 existentes son `10.70.20.1`, `10.71.20.1` y `10.72.20.1`. El backend alterno situado en **S1** exige comunicación real sobre los enlaces WAN OSPF ya observados; separar lo que prueba redundancia de servicio de lo que prueba HA física de infraestructura.

**No reservar definitivamente** esas direcciones por leer un inventario: validar presencia de asignaciones en todos los namespaces, tres routers FRR, IPAM, ARP/vecinos y cualquier proceso externo. La falta de una respuesta ICMP tampoco confirma que una IP esté libre.

## Diseño de implementación (solo después de auditoría)

1. Comprobar ownership `NETLAB360_S02_WAN_LINKS_V1`, `NETLAB360_S02_LAN_8021Q_V1`, IDs de routers, y `ens33=192.168.47.40/24` sin nuevas rutas host.
2. Crear exclusivamente tres namespaces de propiedad S05 y sus extremos `veth` con nombres únicos (sin borrar ni renombrar `tr-sw`, `trunk0`, `br0`, `ens33`). Integrarlos bajo una operación transaccional, con rollback propio, como puertos nuevos etiquetados en switches existentes **solo si la revisión técnica de VLAN filtering lo permite**.
3. Mantener backends independientes con comprobación HTTP de identidad, respuesta y salud. Frontal con política preferencia A y respaldo B por healthcheck; evitar respuestas cacheadas; registrar destino efectivo en cabecera o cuerpo JSON.
4. Desde S2 y/o HQ verificar: A responde → A detenido temporalmente → B responde por el mismo endpoint → A restaurado → política de retorno verificada. Recoger tasa de éxito, indisponibilidad observable y límites de frecuencia de sondeo. **No afirmar cero interrupción si no se midió**.
5. Limpiar procesos de prueba de modo explícito, o conservar servicios con `systemd` controlado y documentado solo después de éxito. Los artefactos de S05 se mantienen fuera de S02 y fuera de datos S04.
6. Actualizar `inventario/topologia-extensiones-s05.json` **después**, no antes, de desplegar y verificar, con origen de datos y estados verificables.

## Riesgos y límites arquitectónicos

- Frontal en HQ puede ser un **punto único de falla**. Una prueba de redundancia de backends no demuestra HA del frontal ni tolerancia a pérdida completa de HQ. La redundancia de router/switch/host físico se tratará como una demostración separada o una limitación explícita.
- El tráfico de backends comparte recursos CPU, NIC y almacenamiento de una única VM; la medición no se extrapola a una infraestructura física.
- No tocar `ens33`, VMnet8, default gateway, Docker `network_mode:none` de FRR, bases S04, puertos NOC `9130` y exporter `9110`, ni el snapshot manual `NETLAB360_S05_PreLAN_20261110`.
- **No desplegar por el mero resultado de precheck**: primero validar addresses, puertos, rutas OSPF de VLAN de servicios y plan de rollback; luego implementar por lotes con capturas precisas.

## Módulo de red HA versionado (sin ejecutar en la VM)

**Implementación lista para validación operativa:** [`scripts/laboratorio/s05-ha-red-servicios.py`](../../scripts/laboratorio/s05-ha-red-servicios.py) ofrece acciones `plan`, `precheck`, `up --confirm-isolated`, `status` y `down --confirm-isolated`. La CI [run 42974399828](https://github.com/recm0708/netlab360/actions/runs/42974399828) aprobó tests de contrato de recursos y sintaxis; **CI offline no certifica despliegue real**.

Al ejecutarse `up`, el módulo comprueba el precheck S05 HA, ownership S02, Git limpio, dirección `ens33` y puertos sin ocupar. Reserva estado local en `~/netlab360-bootstrap/s05/ha/state.json` con owner `NETLAB360_S05_HA_RED_V1`; crea **tres namespaces exclusivos S05** y puertos `ha-hq21`, `ha-s121`, `ha-hq23` en switches S02, cada uno con VLAN de acceso 120/220 y ruta por defecto **dentro de su propio namespace**. Comprueba gateway local y conectividad desde S2 a cada IP. No crea ni modifica router FRR, `ens33`, rutas host, puertos `tr-sw/trunk0` ni servicios HTTP. Solo pasa a `status=active` después de validar; ante fallo intenta revertir únicamente interfaces y namespaces nuevos.

La retirada `down` exige reconocer el estado HA y **rechaza borrar namespaces con procesos vivos**. Una vez implementados servidores HTTP, habrá que detener solo sus procesos antes de cualquier `down`. En caso de error de limpieza, conservar estado y revisar antes de reintentar; no usar `ip netns del` manualmente.

**Condición de avance:** la CI resultó exitosa y los lotes 81–83 de VM registraron 40/40 tests S05, precheck `OK_DISENO_PENDIENTE`, comunicación S2→HQ/S1 (2/2 ICMP por destino). Falta ejecutar lote 84 plan/precheck del nuevo módulo, luego lote 85 `up` y lote 86 `status`. **No se ha desplegado red HA todavía.** Las direcciones IP son candidatas hasta que `up` confirme su asignación y el registro de IPAM sea actualizado.

## Validación siguiente

Ejecutar `python3 scripts/validacion/s05-ha-precheck.py --check` con `sudo -v` previo en T3. El script tiene únicamente inspecciones y NO crea namespaces ni redes. Si emite `S05_HA_PRECHECK=OK_DISENO_PENDIENTE`, pasar al diseño del despliegue y pruebas; cualquier fallo obliga a revisar antes de introducir un nuevo recurso.

**Lotes completados:** 79 (JSONL 119 muestras, principal 55 / respaldo 64, SHA-256 y TAR técnico) y 80 (tres routers FRR activos, 12 namespaces S02, recursos 8 vCPU / 15 GiB RAM total / 132 GiB disco libre, gestión intacta). La captura S05_32 requiere confirmación de guardado por el operador.
