# NETLAB360 B2-L3 — Primer intento E2E HTTP detenido antes de las capturas; corrección de espera FIB

**Registro real:** 2026-10-13 19:30:38–19:32:20, hora Panamá UTC−05.  
**Fuente:** salida completa del operador en archivo de texto de terminal.  
**Estado:** intento **NO SATISFACTORIO** para cliente HTTP HQ→S1; rollback satisfactorio. **Sin aumento de S01 (58% técnico estimado)**.

## Hechos observados

- `git pull --ff-only` actualizó hasta `722a347`; `bash -n scripts/laboratorio/b2-l3-http-clientes-wan.sh` → `RESULTADO_SINTAXIS_E2E=0`; Docker/netns vacíos, `estado-b2-dualwan` ausente, `ens33 192.168.47.40/24`, GW `192.168.47.2`.
- Inicio de `b2-l3-http-clientes-wan.sh --snapshot-confirmado` a **19:30:38**. B2 dual-WAN precheck OK, FRR `quay.io/frrouting/frr:10.7.1` disponible; `up` creó ambos contenedores y OSPF llegó a `OSPF_DUAL_FULL: SI` en el sondeo 5; cada router mostró **dos vecinos Full** (`wan-p` y `wan-b`).
- **Inmediatamente después de imprimir vecinos Full**, `up` terminó con `RTNETLINK answers: Network is unreachable` y exit code **2** antes de marcar `RESULTADO_B2_DUALWAN_UP=0`. La función original `up` de `scripts/laboratorio/b2-dualwan-ospf.sh` consultaba `ip -4 route get` de LAN remota en ambos routers inmediatamente tras `wait_full`. Las adyacencias Full no garantizan que zebra/FIB ya tengan instaladas las rutas a las LAN remotas. Esta **temporización es la causa más probable**, pero se confirmará al probar el cambio: si al esperar siguen sin rutas, inspeccionar tablas OSPF y zebra, no declarar resuelto.
- La rutina `on_exit` del orquestador detectó `UP_PENDING=1` y limpió ambos routers: `RESULTADO_B2_LIMPIEZA=0`. El script externo marcó `RESULTADO_B2_L3_HTTP_WAN=2`, `RESULTADO_EJECUCION_E2E=2`, `RED_GESTION_INTACTA=SI`. No llegó a crear los hosts ni a ejecutar HTTP.
- Por ello no salieron bloques `INICIO CAPTURA B2_L3_01/02/03`; al extraer el log, el operador vio solo encabezados vacíos. **Las capturas B2_L3_01/02/03 no se tomaron**, porque los correspondientes comandos no se ejecutaron. No registrar como tomadas ni pedir repetir la extracción de ese log.
- **Última captura B2_L3_04** fue tomada según confirmación directa del usuario y su consola 19:32:20 demuestra Docker/netns vacíos, `ESTADO_B2_LIMPIO: SI`, gestión preservada y servicios activos. Es **evidencia correcta del postcheck del intento fallido**; no hay que corregirla. Archivo PNG todavía no recibido ni inspeccionado para asegurar encuadre/integridad.
- Git quedó `GIT_SINCRONIZADO: SI` en `722a347` antes de la publicación del fix. Log real `~/netlab360-bootstrap/evidencias/b2-l3-http-wan-20261013-193038.log`, solo local.

## Corrección ya versionada (NO probada aún en Ubuntu)

Se actualizó [`scripts/laboratorio/b2-dualwan-ospf.sh`](../../scripts/laboratorio/b2-dualwan-ospf.sh) para insertar `wait_remote_routes` **después de `wait_full` y antes de los `ip route get` del despliegue**. Hace hasta 60 sondeos de 1 segundo a FIB de ambos routers y espera que HQ→`10.71.10.1` y S1→`10.70.10.1` usen `dev wan-p`. Si sigue sin rutas después del período, devuelve código4 y respeta el rollback existente; no fuerza rutas ni cambia redes del host.

No es una instalación de programas, ni un error de captura. El cambio está en GitHub, **sin ensayo real todavía**. Fase S01 sigue 58%; no declarar éxito de HTTP ni aumentar puntos por escribir corrección.

## Próximos pasos operativos

1. `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`; comprobar `bash -n` de **AMBOS** scripts B2 y E2E, `grep -n 'wait_remote_routes\|RUTAS_OSPF_BIDIRECCIONALES' scripts/laboratorio/b2-dualwan-ospf.sh`, Docker/netns vacíos, estado B2 ausente, ens33/GW originales.
2. Ejecutar **una sola vez** `bash scripts/laboratorio/b2-l3-http-clientes-wan.sh --snapshot-confirmado`; primero confirmar en stdout `RUTAS_OSPF_BIDIRECCIONALES_WAN_P=OK`. Si no aparece antes de HTTP, detener después del código de error, sin una repetición a ciegas.
3. Si el intento avanza, exigir `HTTP_WAN_PRINCIPAL=OK`, `HTTP_WAN_RESPALDO=OK`, `HTTP_WAN_RESTAURADA=OK`, `B2_L3_HTTP_TRES_ESTADOS=OK`, `RESULTADO_B2_L3_HTTP_WAN=0`; capturas B2_L3_01/02/03 se tomarán **ahora por primera vez**.
4. Ejecutar postcheck read-only en Terminal, Docker/netns vacíos, estado B2 ausente, servicios/gestión, Git. Captura **B2_L3_04_Postcheck_HTTP_WAN_Final.png** si el nuevo intento termina bien, para distinguirla de B2_L3_04 original de incidente.
5. Si falla otra vez, **no rehacer por defecto**: enviar últimas 50 líneas del log E2E y salida del postcheck para ajustar la nueva causa manteniendo evidencia histórica.

**No alterar** `ens33`, VMware VMnet8, gateway `192.168.47.2`, rutas/firewall del host. El endpoint E2E usa clientes por veth P2P detrás de FRR, no demuestra unión física al trunk de VLAN; esta limitación de alcance sigue explícita.
