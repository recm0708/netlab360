# NETLAB360 S02 — Validación WAN y ruta de cierre (23/10/2026)

## Evidencia VERIFICADA del operador (no inferida)
- Archivo de salida real conservado en la bitácora, 23/10/2026 19:19 -05. Compilación Python S02 WAN exit 0 y 4/4 tests plan WAN correctos.
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


## Diagnostico HTTP resuelto a nivel de causa y plan de prueba — 23/10/2026 19:54 (-05)

**Evidencia recibida del registro del proyecto:**
- Los cuatro archivos `S02_HTTP_Server_{HQ,S1,S2}_8080.log` y `S02_HTTP_Server_S1_8081.log` contienen únicamente `sudo: interactive authentication is required`. El script anterior ejecutaba el servidor mediante `subprocess.Popen(..., start_new_session=True)` a la vez que dependía de `sudo -n` y caché de autorización por TTY, por tanto el proceso hijo no obtuvo credencial. No existían sockets TCP 8080/8081 en namespace después del intento. **NO era prueba de ACL ni fallo IP.**
- HQ VLAN110 `10.70.10.10/24` y S1 VLAN220 `10.71.20.20/24` están UP; ping HQ→S1 2/2, ida y retorno vía sus gateways. nft `nl360_s02_acl` AUSENTE.
- Tres FRR running >52 min; `validar-ospf-s02.py` retorna 0, `validar-lan-s02.py` retorna 0; `ens33 .40/24` y GW `.2` intactas, Git limpio.
- SoT S03 **generado realmente** 19:53:25: 3 routers, 9 VLAN, 8 extremos WAN, source `candidate`; hash `inventory-s03.yml=33edfa992eb35ea5f99154365f149f62eee703305db924b50db854c025b16f0d`, `sot-s03.json=4f1a6d70b49918e08e4c51b398036e8c285f4d512bd7214d04a120fff075f09c`. Captura `S03_01` comunicada tomada. **Esto no acredita Ansible live o idempotencia todavía.**

**Corrección publicada en GitHub, no ejecutada en Ubuntu:** nuevo `s02-http-acl-demo.py` mantiene proceso sudo en misma sesión (sin setsid), comprueba autorización no interactiva antes de iniciar, verifica HTTP real local de cada uno de cuatro servidores, comprueba que S1:8081 continúa activo tras bloqueo HQ:110→S1:8081, que HTTP 8080 sigue permitido y que la regla nft registra paquetes. Limpieza apunta a PID HTTP propio y a tabla nft S02 exclusivamente, sin matar el grupo de sesión SSH. 6 tests nuevos `test_s02_http_acl.py`. **Aceptar captura S02_09 únicamente si test, HTTP/ACL, limpieza y postchecks dan salida 0.**

**S03 adicional preparado, no ejecutado en Ubuntu:** `s03-estado-observado.py` consulta 3 routers solo lectura por Docker/namespaces, confronta 3 loopbacks, 9 VLAN, 8 extremos WAN IPv4 y vecinos OSPF Full 4+2+2 con SoT candidate, exporta JSON observado estable; 3 pruebas offline `test_s03_estado_observado.py`. No aplica playbooks ni reconcilia; candidata captura `S03_02_SoT_Contra_Estado_Real_Tres_Sedes` con hashes de dos lecturas.


## Tercer corte real — 23/10/2026 20:10 (-05): HTTP/ACL aprobado y S03 auditoría live inicial

**Resultados enviados en los registros del proyecto (salida completa de los pasos 71–80, 404 líneas):**
- Python py_compile exit 0; pruebas 6/6 S02 HTTP/ACL y 3/3 S03 observado exitosas.
- S02 pre-HTTP sudo -n autentica, OSPF 0, LAN 0 y sin tabla nft previa.
- HTTP corregido arranca **4/4 servicios reales**: HQ `10.70.20.20:8080`, S1 `10.71.20.20:8080`, S2 `10.72.20.20:8080` y S1 `10.71.20.20:8081`, cada uno pasó comprobación HTTP local y devolución de cuerpo.
- Baseline HTTP intersedes **4/4 OK**; servicio TCP 8081 **ACTIVO PRE-ACL**; nftables tabla `nl360_s02_acl` solo en namespace R-HQ bloqueó tráfico específico HQ VLAN110→S1 `10.71.20.20:8081`, **2 paquetes /120 bytes** contados en la regla. Cliente S1 aún accede al mismo 8081; HTTP 8080 sigue PERMITIDO en 4/4 rutas. `S02_HTTP_MULTISEDE=VALIDADO`, `S02_ACL_SERVICIO_REAL=VALIDADO`, `RESULTADO_HTTP_ACL_CORREGIDO=0`.
- Postcheck ACL ausente, ningún listener TCP 8080/8081 en los tres endpoints, `S02_ACL_TEMPORAL_RETIRADA=SI` y `S02_SERVIDORES_TEMPORALES_FINALIZADOS=SI`. **La ACL y los HTTP fueron temporales: persistencia/operación de servicios queda para fases posteriores**.
- Regresión final WAN OSPF **0** y LAN **0**; tres FRR `running`, IP gestión `192.168.47.40/24`, gateway `192.168.47.2`, Git limpio `32c8fc0` en la VM.
- Se ejecutó bloque de terminal para evidencia `S02_09_HTTP_Real_y_ACL_Entre_Sedes` fechado 20:07:57; **no consta confirmación de archivo PNG guardado** (la salida visible sí es válida).
- S03 `s03-estado-observado.py` auditoría live sólo lectura exit 0, 3/3 loopback, 9/9 VLAN, 8/8 extremos WAN, OSPF Full 4+2+2. Segunda lectura exit 0 con **SHA256 idéntico** `2c902055a71eaf59bfeeea8db38b2b24e69be23ead4903e74bc1be3fbc37afd7`. `S03_APLICACION_ANSIBLE_EJECUTADA=NO`.
- Se ejecutó bloque de terminal para `S03_02_SoT_Contra_Estado_Real_Tres_Sedes` a 20:10:19; sin confirmación independiente de guardado PNG. Hash SoT `4f1a6d70b49918e08e4c51b398036e8c285f4d512bd7214d04a120fff075f09c`.
- Herramientas listas para S03: Ansible Core **2.20.1**, inventario `R-HQ,R-S1,R-S2` reconocido, OpenTofu **1.13.1**, Git limpio.

**Resultado del alcance S02 principal:** multisede integrada real con 4 WAN OSPF y failover/restauración S1/S2, 9 VLAN 802.1Q, 9 clientes de prueba, 4 verificaciones HTTP y ACL temporal discriminante entre sedes, redes del host intactas. **Este bloque funcional pasó sus pruebas.** La issue S02 general no puede cerrarse automáticamente porque su checklist histórico también abarca LACP, NOC, analítica, documentación final, OVA condicional y demás fases transferidas; estas siguen en S04-S08.

**Próxima fase S03:** playbook Ansible sobre 3 routers reales **de solo lectura** para costos OSPF WAN contra SoT; registrar changed=0/failed=0 por router; después, solo con precheck y snapshots, preparar experimento de drift en costo OSPF de backup (sin tocar primaria) con reconciliación y rollback acotado. OpenTofu state/lifecycle y CI quedan pendientes.
