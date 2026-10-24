# NETLAB360 S02 — Validación WAN y ruta de cierre (23/10/2026)

## Evidencia VERIFICADA del operador (no inferida)
- Archivo de salida real aportado por el usuario, 23/10/2026 19:19 -05. Compilación Python S02 WAN exit 0 y 4/4 tests plan WAN correctos.
- El primer validador IPAM live retornó 1 al ejecutar `sudo -n docker network ls` **antes de autenticar sudo**; esto NO fue un solapamiento. Después `sudo -v`, el `precheck` WAN devolvió 0.
- `python3 scripts/laboratorio/s02-wan-links.py up --snapshot-confirmado`: `S02_WAN_CREADA` en primaria/respaldo HQ–S1 y HQ–S2, loopbacks `10.79.0.1/32`–`.3/32`, `ip_forward=1` **solamente en los namespaces de routers**, `S02_WAN_LINKS_UP=4`, `S02_HOST_GESTION_INTACTO=SI`, exit 0.
- `validar-ospf-s02.py`: HQ cuatro OSPF Full, S1 dos, S2 dos. **6/6 decisiones de ruta FIB principal** y seis pruebas ICMP bidireccionales HQ↔S1, HQ↔S2, S1↔S2 con éxito, `RESULTADO_VALIDACION_OSPF=0`.
- `s02-wan-links.py status`: los cuatro enlaces estables y OSPF Full sin restos, gestión intacta `ens33=192.168.47.40/24` y default `192.168.47.2`, Git limpio en `c5f4b00` al verificar.
- **Captura PNG real adjunta al chat** `S02_06_WAN_OSPF_HQ_S1_S2_Cuatro_Enlaces.png`: visible Full=4/2/2, FIB 6/6, ICMP 6/6, resultado 0 y red administrativa intacta.
- PNG anteriores S02_01/S02_02/S02_03/S02_04/S02_05 también aportados al chat. **S02_05 del 17/10** corresponde al primer intento fallido (un solo router Up): mantener solo como artefacto diagnóstico, NO prueba de tres routers. **S02_05 de 23/10** muestra los tres y es la versión válida.
- Estos PNG se adjuntaron al chat, pero **todavía no se han incorporado físicamente a GitHub**. No inventar su ruta de repositorio.

## Estado operativo confirmado
- Tres contenedores FRR están encendidos, cuatro enlaces WAN + loopbacks funcionan. Mantenerlos activos hasta terminar S02 LAN/ACL.
- La WAN está desplegada; el IPAM sigue con `status: candidate` por pendientes LAN y pruebas. **No cambiar a `deployed` por una sola prueba WAN**.
- Todavía no hay nueve VLAN vivas ni HTTP multisedes/ACL probado. No declarar S02 cerrada.
- Faltan ensayos de falla y restauración real de WAN primaria para S1 y S2; documentar rutas de costo 100 durante falla, retorno a 10 y supervivencia de la otra sede.

## Ruta acelerada de cierre + arranque de S03
1. `sudo -v`, Git pull, py_compile de nuevos scripts, tests offline del plan LAN y SoT. Sin cambiar red administrativa.
2. `s02-failover-wan.py S1` y `S2`: cada ensayo parte de primaria, provoca fallo, confirma uso de respaldo y restaura primaria en `finally`. Registrar evidencia `S02_07_Conmutacion_WAN_S1_S2_Restauracion`.
3. Revalidar `validar-ospf-s02.py` (Full 4/2/2) tras ambos fallos.
4. `s02-lan-vlan.py plan/precheck/up --snapshot-confirmado/status`: crea 3 bridge VLAN-aware **en namespaces dedicados**, nueve VLAN etiquetadas entre switches y subinterfaces `trunk0.<VID>` de FRR, un endpoint por VLAN. No conecta con ens33, no añade rutas al host. Respaldar con `validar-lan-s02.py`, 9 gateways y seis comunicaciones entre VLAN/sedes. Evidencia `S02_08_Tres_Switches_Nueve_VLAN_Trunk_8021Q`.
5. `s02-http-acl-demo.py`: cuatro servicios HTTP temporales (8080 HQ/S1/S2, 8081 S1); comprobar 8081 ACTIVO antes de ACL; añadir regla nft **solo al namespace R-HQ**, bloquear HQ VLAN110→S1 VLAN220 TCP8081, mantener 8080 permitido; al finalizar borrar únicamente la tabla temporal y parar servidores. Evidencia `S02_09_HTTP_Real_y_ACL_Entre_Sedes`.
6. Prueba de integración final WAN/OSPF + LAN + servicios/ACL + host, y solo entonces valorar cierre técnico S02; LACP en S05 y SDN/observabilidad en fases futuras **siguen abiertos**, aunque el issue #2 histórico diga LACP: dejar trazabilidad y no clasificar S02 globalmente completo si corresponde.
7. `s03-generar-sot.py` produce JSON deseado + inventario Ansible local en directorio externo, 3 routers/9 VLAN/8 extremos WAN. **No es compliance aplicado**, no toca Docker/FRR; tests offline. Base para issue #16–#18 y primera evidencia S03.
8. Revisión en Teams **30/10/2026** (issue #47) se prepara **en paralelo** desde el borrador maestro institucional, sin diapositivas.

## Prohibiciones operativas
- No ejecutar `docker compose down` mientras existan WAN/LAN. Para revertir caso integral: detener prueba HTTP, `python3 scripts/laboratorio/s02-lan-vlan.py down` si LAN fue creada, luego `python3 scripts/laboratorio/s02-wan-links.py down`, y solo finalmente Compose.
- Nunca `docker system prune`, `ip link del ens33`, `ip route flush`, ni limpiar namespaces globalmente.
- No asumir que archivos publicados o pruebas no ejecutadas en Ubuntu ya funcionaron.


## Segundo corte real — 23/10/2026 19:42 (-05), failover/LAN y bloqueo HTTP
- **WAN failover S1:** primaria `s1p` down, ambas FIB HQ/S1 usan `s1b`, otra sede estable, al restaurar retorna `s1p`, `RESULTADO_FAILOVER_S1=0`.
- **WAN failover S2:** primaria `s2p` down, ambas FIB HQ/S2 usan `s2b`, S1 estable y vuelve a `s2p` al restaurar, `RESULTADO_FAILOVER_S2=0`.
- OSPF después de fallas `RESULTADO_OSPF_POSTFAILOVER=0`, cuatro FULL HQ, dos FULL S1/S2 y seis rutas principales. Captura **S02_07** comunicada tomada.
- **LAN S02:** plan/precheck 0; `up --snapshot-confirmado` termina 0, tres bridges, nueve VLAN etiquetadas por sede y nueve hosts, host sin cambios; `validar-lan-s02.py` confirma **9/9** ping a gateways, **6/6** ICMP inter-VLAN y entre sedes y resultado 0; `status` muestra trunk etiquetado y subinterfaces `trunk0.<VID>`. Captura **S02_08** comunicada tomada.
- **HTTP/ACL NO validado:** `s02-http-acl-demo.py` imprimió `S02_SERVIDOR_INICIADO` para HQ 8080, S1 8080, S2 8080, S1 8081; al hacer primer `curl` en HQ VLAN110 hacia `10.71.20.20:8080`, exit **7** (Could not connect to server). Exit global **1**. **No se ejecutó instalación nftables ACL**; sin resultado de denegación y sin captura S02_09. El script imprimió cierre de servidores, pero no se validó por `ss`.
- Los pasos **66–69 (incluido SoT S03)** no se realizaron por decisión correcta de detenerse al código no cero. No asumir S03 iniciada; archivos de código remoto están preparados, ejecución y evidencia pendientes.
- **Próximo diagnóstico:** conservar routers WAN y LAN; leer cuatro logs `S02_HTTP_Server_{HQ,S1,S2}_8080.log` y `S02_HTTP_Server_S1_8081.log`; verificar listeners TCP en namespaces y reglas `nft` en R-HQ/S1; examinar si el servidor llegó a enlazar el puerto antes de repetir la prueba. No introducir ACL a ciegas, no eliminar recursos.
