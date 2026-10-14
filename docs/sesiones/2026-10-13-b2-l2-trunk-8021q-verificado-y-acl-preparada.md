# NETLAB360 — Validación real de trunk 802.1Q y nuevo ensayo ACL/HTTP preparado

**Corte:** 13/10/2026, 19:00–19:01 hora Panamá.  
**Fuentes:** salida completa de tres comandos del operador (pasos 84, 85, 86). Se validó la ejecución **real** del trunk. El próximo ensayo ACL/HTTP fue versionado, **sin ejecutar aún en la VM**.

## 1. Prueba trunk 802.1Q REAL ejecutada y validada

- `git pull --ff-only origin main` actualizó al commit `a52391a`; `bash -n scripts/laboratorio/b2-l2-trunk-8021q.sh` = `RESULTADO_SINTAXIS_TRUNK=0`. Docker y namespaces vacíos en precheck. `ens33=192.168.47.40/24`, gateway `192.168.47.2`.
- En 19:00:00, ejecutó `bash scripts/laboratorio/b2-l2-trunk-8021q.sh --snapshot-confirmado`. `VALIDACIÓN B1: OK`, IPAM 3 sedes/9 VLAN/2 WAN `draft`. **Topología intra-HQ:** `SW-HQ-A`, `SW-HQ-B`; enlaces etiquetados `tr-a` y `tr-b` transportando **VID 110/120** y puertos de acceso `a110/b110` PVID 110 untagged, `a120/b120` PVID 120 untagged. `bridge vlan show` evidencia ambas VID en troncal, sin afirmar un trunk entre HQ y S1.
- **`B2_L2_02` a 19:00:01:** ping entre puertos de VLAN110 `10.70.10.10→10.70.10.11`, **3/3 recibidos**, RTT medio 0.073 ms; VLAN120 `10.70.20.10→10.70.20.11`, **3/3 recibidos**, RTT medio 0.066 ms; `PRUEBA_TRUNK_VLAN110=OK` y `PRUEBA_TRUNK_VLAN120=OK`.
- **`B2_L2_03` a 19:00:06:** alias temporal `10.70.10.12/24` sobre puerto de VLAN120; origen en VLAN110 tiene ruta on-link hacia esa IP pero el ping reportó `Destination Host Unreachable`, **3/3 transmitidos, 0 recibidos, 100% de pérdida**, `AISLAMIENTO_INTERVLAN_L2=OK`. En seguimiento, VLAN110 conserva **2/2** y VLAN120 **2/2** positivos. Resultado `B2_L2_TRUNK_Y_AISLAMIENTO=OK`. Un fallo por pérdida de ruta L3 simple no explica el negativo, ya que la ruta on-link fue mostrada.
- **Limpieza automática** código `RESULTADO_B2_L2_TRUNK=0` y `RESULTADO_EJECUCION_TRUNK=0`, `RED_GESTION_INTACTA=SI`. Log local `~/netlab360-bootstrap/evidencias/b2-l2-trunk-20261013-190000.log`. `B2_L2_04` postcheck 19:01:44: Docker y namespaces **vacíos**, IP/GW intactos, servicios docker/ssh/open-vm-tools `active`, Git `## main...origin/main` limpio a ese corte.
- Evidencias **B2_L2_02_Trunk_8021Q_VLAN110_120.png**, **B2_L2_03_Aislamiento_Trunk_Dos_VLAN.png**, **B2_L2_04_Postcheck_Trunk_8021Q.png** consideradas tomadas por regla del usuario, **no se han recibido PNG para revisión visual ni subido a GitHub**.

## 2. Alcance comprobado y puntuación

- Queda probado **trunk etiquetado 802.1Q con dos VLAN en switches virtuales dentro de HQ**, aislamiento entre VLAN y conservación de conectividad intravlan. NO se ha probado ACL de capa 3, enrutamiento inter-VLAN, cliente/servidor HTTP, ni tránsito intersedes.
- [Matriz S01](../control/01-avance-s01.md): se acredita **B2-L2 3→5 de 10 (+2)** y global **S01 53→55 de 100**; estimación técnica, no nota oficial. Criterios integrales de #1 y #30 abiertos.

## 3. Siguiente ensayo ACL/HTTP VERSIONADO, pero SIN resultado de runtime

Nuevo [`scripts/laboratorio/b2-l2-acl-http-real.sh`](../../scripts/laboratorio/b2-l2-acl-http-real.sh) (solo versión GitHub, **aún no ejecutado**):

1. Exige snapshot confirmado, hostname, IP/GW, validador IPAM y cinco namespaces propios ausentes; nunca modifica firewall/rutas del host.
2. Dos bridges con VLAN110/120 y trunks, router Linux virtual por interfaces etiquetadas `eth0.110` = `10.70.10.1/24`, `eth0.120` = `10.70.20.1/24`, cliente `10.70.10.10/24`, servidor `10.70.20.20/24`.
3. Dos servidores Python HTTP reales en namespace del servidor escuchando **8080 y 8081**. Baseline previo a ACL comprueba que ambos son accesibles desde cliente y que hay ruta inter-VLAN: captura `B2_L2_05_Routing_y_HTTP_Sin_ACL.png`.
4. Regla `nftables` **exclusivamente en namespace router**: permite TCP 8080 desde VLAN110 a VLAN120 y bloquea TCP 8081; acepta tráfico establecido relacionado. Prueba después de ACL: HTTP8080 responde, HTTP8081 está realmente activo en servidor pero cliente queda bloqueado; inspección de contadores nftables: captura `B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png`.
5. Trap de salida elimina únicamente cinco namespaces y termina servidores incluidos en ellos, compara ens33 y tabla de rutas originales, emite `RESULTADO_B2_L2_ACL_HTTP=0` en éxito. Captura postcheck `B2_L2_07_Postcheck_ACL_HTTP.png`.
6. **No implica conectividad HQ↔S1 ni FRR/OSPF**; clientes y servicios se añadirán a topología WAN en un bloque posterior. `nft` de host y VMware VMnet8 permanecen intocados.

Siguiente operación: `git pull --ff-only`, `bash -n` nuevo script, comprobar Docker/netns vacíos y gestión intacta, ejecutar **una sola vez** `bash scripts/laboratorio/b2-l2-acl-http-real.sh --snapshot-confirmado`, capturar bloques y postcheck. Si falla, **no repetir**: enviar salida, revisar limpieza y corregir script de forma trazable. **No incrementar 55% hasta comprobar resultados reales de ACL.**
