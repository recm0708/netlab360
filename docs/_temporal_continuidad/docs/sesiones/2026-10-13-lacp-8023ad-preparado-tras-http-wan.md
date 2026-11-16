# NETLAB360 — Seguimiento B2-L3 verificado y preparación LACP 802.3ad

**Fecha de corte:** 2026-10-13, ~19:45 Panamá (UTC−05).  
**HTTP WAN:** DEMOSTRADO. **LACP:** SCRIPT CREADO, NO EJECUTADO EN VM.  
**S01:** 59% técnico estimado, sin marcar como aprobados requisitos integrales.

## Resultado REAL aportado por el operador

En `b2-l3-http-clientes-wan.sh --snapshot-confirmado` a 19:42:54, tras un `git pull` hasta `6a3e50f`, `wait_remote_routes` confirmó FIB simétrica WAN-P después del establecimiento OSPF Full. Se ejecutaron **tres peticiones HTTP** desde host HQ `10.70.10.10/32` hacia servidor Python en S1 `10.71.10.20/32:8080`, todas con el contenido `NETLAB360_HTTP_S1_SERVICIO_REAL_OK`: WAN-P normal, WAN-B durante `fail`, WAN-P restaurada después de `restore`. Las FIB de **los dos routers** confirmaron la selección WAN-P→WAN-B→WAN-P y el script cerró código0. La limpieza B2 terminó código0, contenedores y namespaces vacíos, `ESTADO_B2_LIMPIO: SI`, gestión ens33 `192.168.47.40/24` y GW `192.168.47.2` conservados. `B2_L3_HTTP_TRES_ESTADOS=OK`, `RESULTADO_B2_L3_HTTP_WAN=0`.

Se imprimieron y extrajeron tres bloques completos B2_L3_01/02/03 y B2_L3_04_FINAL, **se presumen capturados** según regla del usuario, pero **no se recibieron ni auditaron archivos PNG**. El B2_L3_04 del intento anterior es un postcheck diagnóstico distinto y se conserva. Log original `~/netlab360-bootstrap/evidencias/b2-l3-http-wan-20261013-194254.log` permanece local. Esta prueba de tres estados **no mide interrupciones instantáneas de HTTP durante la propia transición** y utiliza hosts por enlaces P2P separados del trunk VLAN probado anteriormente.

## Plan de laboratorio LACP (NUEVO, NO EJECUTADO)

Archivo versionado `scripts/laboratorio/b2-lacp-8023ad-dos-enlaces.sh`, en dos namespaces propios `nl360-lacpa` y `nl360-lacpb`; cada extremo crea `bond0` con `mode 802.3ad`, `miimon 100`, `lacp_rate fast`, y conecta dos parejas `veth` esclavas (`a1↔b1`, `a2↔b2`). La IP de ensayo `198.18.250.1/30 ↔ 198.18.250.2/30` es local aislada; no toca rutas ni nftables del host.

1. Guarda snapshot y exige `--snapshot-confirmado`; prechecks de hostname, cuenta no-root, `sudo -v`, IP/GW de gestión, namespaces inexistentes y dependencias básicas. Si driver bonding no soportado, el intento debe fallar y limpiar los namespaces propios; no instalar paquetes a ciegas.
2. Inicia servidor HTTP en extremo B. **B2_LACP_01:** `cat /proc/net/bonding/bond0` en cada namespace debe indicar **IEEE 802.3ad**, **2 puertos en el agregador activo**, y HTTP de A a B correcto.
3. Apaga exclusivamente **`a1`** en namespace A. **B2_LACP_02:** se exige **1 puerto en agregador activo**, HTTP accesible por el enlace sobreviviente, tras espera y reintentos acotados.
4. Restaura `a1`. **B2_LACP_03:** se exige volver a **2 puertos**, y respuesta HTTP correcta.
5. `trap EXIT`: termina solamente procesos dentro de sus propios namespaces, retira las dos namespaces y compara IP y todas las rutas del host. El resultado de éxito será `LACP_8023AD_TRES_ESTADOS=OK` y `RESULTADO_B2_LACP=0`. **B2_LACP_04_FINAL** es postcheck separado.

**Límites importantes:** dos enlaces virtuales independientes más modo bonding IEEE 802.3ad **no equivalen a dos adaptadores VMware físicos ni redundancia de un switch real**. Es una prueba local de negociación LACP; la parte de servidor dual-NIC/backup de equipo permanece pendiente. Comprobar que el archivo pase `bash -n` y el soporte del módulo en Ubuntu antes de ejecutar. La ausencia previa de `/sys/module/bonding` no demuestra falta de soporte; `ip link add ... type bond` puede cargar el módulo desde el kernel, sujeto a disponibilidad.

**Estado al corte:** última salida usuario mostró Docker/netns vacíos, B2 sin marcador, ens33/GW intactos y Git sincronizado `6a3e50f` **antes de los nuevos commits de GitHub**. Ningún porcentaje LACP acreditado por crear script.
