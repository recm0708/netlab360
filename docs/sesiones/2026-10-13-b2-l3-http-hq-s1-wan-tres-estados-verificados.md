# NETLAB360 — B2-L3 servicio HTTP real HQ→S1 por las dos WAN, validado

**Fuente:** salida real aportada por operador desde Ubuntu `netlab360-lab` el 13/10/2026 entre 19:42:54 y 19:44:57 (Panamá). **No se han recibido PNG**, solo texto de consola y el registro de sus bloques de captura.

## Precheck, corrección y arranque

- `git pull --ff-only origin main` alcanzó `6a3e50f`. `bash -n` de `b2-dualwan-ospf.sh` y `b2-l3-http-clientes-wan.sh` ambos 0; función `wait_remote_routes` presente y llamada después de `wait_full`.
- Precheck limpio: Docker y netns vacíos, marcador B2 ausente, ens33 `192.168.47.40/24` y gateway `192.168.47.2` intactos, Git limpio. B2 FRR precheck RC0, ambos routers arrancaron con dos vecinos OSPF Full y espera explícita de FIB en ambos sentidos satisfactoria `RUTAS_OSPF_BIDIRECCIONALES_WAN_P=OK (sondeo 1)`. `RESULTADO_B2_DUALWAN_UP=0`.
- Corrección funcionó para el síntoma específico de inicio: el `up` anterior abortaba al consultar rutas remotas inmediatamente tras Full. El nuevo flujo esperó a tener ambas rutas `dev wan-p` y avanzó a crear hosts.

## Resultados reales por fase

| Evidencia solicitada | Hora | Camino FIB en HQ y S1 | HTTP del cliente a servidor | Resultado |
|---|---|---|---|---|
| B2_L3_01 | 19:43:17 | WAN-P, rutas bidireccionales `10.71.10.20` y `10.70.10.10` | `NETLAB360_HTTP_S1_SERVICIO_REAL_OK` | `HTTP_WAN_PRINCIPAL=OK` |
| B2_L3_02 | 19:43:17 | WAN-B, rutas bidireccionales tras `fail`, `CONMUTACION_WAN_B: OK` | `NETLAB360_HTTP_S1_SERVICIO_REAL_OK` | `HTTP_WAN_RESPALDO=OK` |
| B2_L3_03 | 19:43:28 | WAN-P restaurada, rutas bidireccionales tras `restore`, `RESTAURACION_WAN_P: OK (sondeo 11)` | `NETLAB360_HTTP_S1_SERVICIO_REAL_OK` | `HTTP_WAN_RESTAURADA=OK` |

Los extremos son **namespaces de hosts reales**, cliente `10.70.10.10/32` y servidor Python HTTP `10.71.10.20/32:8080`, conectados a routers FRR mediante veth punto a punto `169.254.70.0/30` y `169.254.71.0/30`. **No están conectados al trunk VLAN 802.1Q anterior**; no confundir con un servicio final integrado de una LAN multisede. Se demostró acceso HTTP en tres estados estabilizados y recuperación de selección de ruta; **no se midió disponibilidad HTTP continua durante las ventanas de conmutación ni tiempo exacto de convergencia**.

## Limpieza y evidencias

- `B2_L3_HTTP_TRES_ESTADOS=OK`, `RESULTADO_B2_L3_HTTP_WAN=0`, `RESULTADO_EJECUCION_E2E=0`, `RESULTADO_B2_LIMPIEZA=0`, `RED_GESTION_INTACTA=SI`.
- Captura B2_L3_04_FINAL a **19:44:57**: Docker sin contenedores, `ip netns list` vacío, `ESTADO_B2_LIMPIO=SI`, `ens33 UP 192.168.47.40/24`, default vía `192.168.47.2`, servicios docker/ssh/open-vm-tools activos. Git `## main...origin/main` limpio al commit `6a3e50f` antes de los nuevos commits de esta actualización.
- Los tres bloques B2_L3_01/02/03 sí aparecieron en el log original, `BLOQUES_CAPTURA_ENCONTRADOS=3`, y se extrajeron correctamente. Las capturas se presumen tomadas al solicitarlas según convención, **pero todavía no se ha recibido ni revisado visualmente ningún PNG**. La captura B2_L3_04 anterior de intento fallido se conserva separadamente de B2_L3_04_FINAL.
- Log original en `~/netlab360-bootstrap/evidencias/b2-l3-http-wan-20261013-194254.log`, no respaldado aún en GitHub.

## Valoración y siguiente bloque

El porcentaje técnico estimado S01 pasa **58→59/100 (+1 B2-L3; bloque 17→18/18)** por HTTP real en ambas WAN y retorno, sin declarar cierre de los 11 criterios académicos ni integración full L2/FRR. Próximo objetivo prioritario: **LAG/LACP 802.3ad, caída de uno de los dos enlaces y recuperación**; luego host dual-NIC/servicio, OpenTofu+Ansible, IA y entrega. Construir laboratorio aislado de namespaces que no toque VMnet8/ens33/gateway ni redes Docker del host. **No ejecutar otra prueba HTTP E2E solo por documentación.**
