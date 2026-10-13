# NETLAB360 — Preparación B2-L2 trunk, ACL y clientes reales (13/10/2026, 18:51 Panamá)

## Auditoría recibida y verificada (solamente precheck, no trunk)

A 18:51:04 operador ejecutó y compartió `bash scripts/validacion/precheck-b2-l2-trunk-acl.sh`, tras pull hasta `6e6d500`; `bash -n` sin errores, `RESULTADO_PRECHECK_L2=0`, `B2_L2_PREFLIGHT=OK`.

- Siete herramientas requeridas `ip,bridge,nsenter,python3,ping,sudo,git` disponibles. `nftables v1.1.6` disponible (solo detección). `bridge utility 6.19.0`, kernel Linux `7.0.0-38-generic`.
- `MODULO_VISIBLE=bridge`; `MODULO_NO_VISIBLE=8021q` y `MODULO_NO_VISIBLE=bonding` **no implican que falte soporte ni que haya que instalar o cargar módulos de forma ciega**. La prueba de trunk se hace con `bridge vlan_filtering`; bonding se auditará cuando corresponda.
- `VALIDACIÓN B1: OK`, 3 sedes/9 VLAN/2 WAN y 15 prefijos, sin solapamientos internos; SoT/IPAM `status: draft` todavía.
- Docker sin contenedores, `ip netns list` vacío; `ens33 UP 192.168.47.40/24`, gateway `192.168.47.2`; `git status --short --branch` = `## main...origin/main` limpio al corte.
- Log original local `~/netlab360-bootstrap/evidencias/b2-l2-precheck-20261013-185104.log`, **NO respaldado automáticamente en GitHub**. Evidencia de captura futura precheck según guía, no reclamar PNG subido.

## Próxima ejecución planificada, NO realizada en la salida actual

Se versionó [`scripts/laboratorio/b2-l2-trunk-8021q.sh`](../../scripts/laboratorio/b2-l2-trunk-8021q.sh), PoC **sin contenedores ni cambios de rutas del host**:

1. Requiere `--snapshot-confirmado`, hostname `netlab360-lab`, cuenta normal, `sudo -v`, IP/GW de administración intactos e IPAM OK.
2. Verifica que ninguno de sus **seis namespaces propios** `nl360-ta,tb,t110a,t110b,t120a,t120b` exista, y crea dos switches Linux bridge aislados `SW-HQ-A/B`.
3. Puertos de acceso para VLAN 110 (HQ-USUARIOS `10.70.10.0/24`) y 120 (HQ-SERVICIOS `10.70.20.0/24`), con un **trunk etiquetado** que permite VLAN 110/120 sin PVID/untagged. Esto es **dos switches dentro de HQ**, **NO un trunk extendido artificialmente entre HQ y S1** que rompería el modelo IPAM.
4. Pruebas positivas: pings 3/3 H110→B110 y H120→B120 cruzando el troncal, inspección `bridge vlan show`. Evidencia solicitada `B2_L2_02_Trunk_8021Q_VLAN110_120.png` delimitada.
5. Prueba negativa técnicamente válida: configurar **alias diagnóstico temporal** `10.70.10.12/24` en un host de VLAN 120 para que el origen VLAN110 tenga ruta on-link al destino; ping desde VLAN110 debe fallar por aislamiento de capa 2 y no por falta de ruta. Volver a comprobar 2/2 ICMP dentro de VLAN 110 y VLAN 120. Evidencia `B2_L2_03_Aislamiento_Trunk_Dos_VLAN.png`. El alias es SOLO diagnóstico, no modificación del SoT.
6. Trap EXIT borra **exclusivamente namespaces de propiedad de este ensayo**, revisa IP/rutas de gestión, imprime `RESULTADO_B2_L2_TRUNK=0` si todo fue bien. Si algo falla, revisar `RESIDUO_NAMESPACE` y postcheck antes de continuar. **Nunca borrar namespaces ajenos.**

La prueba **NO acredita aún ACL**, inter-VLAN routing, conexión HQ↔S1 por WAN, servidores reales, LACP ni monitorización integrada; esas pruebas siguen pendientes. El script de trunk está en GitHub pero **todavía NO se ha ejecutado en la VM ni tiene resultados**, así que S01 permanece **53% técnico estimado**.

## Secuencia próxima

1. `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`, `bash -n scripts/laboratorio/b2-l2-trunk-8021q.sh`, verificar limpieza Docker/netns/red host.
2. Ejecutar **una vez** `bash scripts/laboratorio/b2-l2-trunk-8021q.sh --snapshot-confirmado`. Si código no es 0, detener y diagnosticar antes de repetir.
3. Postcheck de namespaces, Docker/ens33/GW/Git. Sólo acreditar nuevos puntos L2 después de comprobar stdout y captura en la VM; conservar las imágenes solicitadas como tomadas por convención sin atribuir inspección visual no efectuada.
4. Siguiente incremento tras trunk: ACL L3 sobre router o firewall en namespace aislado, servicio HTTP entre VLAN/sedes y cliente real, sin modificar reglas `nft` del host.

[Plan de recuperación semana académica 9](../control/02-plan-recuperacion-semana-09.md) · [Avance S01](../control/01-avance-s01.md) · [Issue L2 #30](https://github.com/recm0708/netlab360/issues/30).
