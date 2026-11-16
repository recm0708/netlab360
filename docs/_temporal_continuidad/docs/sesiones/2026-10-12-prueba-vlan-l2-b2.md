# Bitácora B2 — Ensayo funcional de VLAN aisladas

**Ejecución:** 2026-10-12 18:16:01 (Panamá, UTC−05:00).  
**Host:** `netlab360-lab`; Ubuntu Desktop 26.04.1 LTS, `ens33 192.168.47.40/24`.  
**Issue:** [#12](https://github.com/recm0708/netlab360/issues/12).

## Prueba realizada — evidencia recibida

- `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main` completó la actualización desde `cf586fb` a `6f145e9`; `bash -n scripts/laboratorio/b2-l2-aislado.sh` sin errores, árbol limpio.
- Se ejecutó `sync; sudo systemctl poweroff` y la conexión SSH terminó normalmente. Un intento de conexión posterior por Windows devolvió timeout durante el apagado; la siguiente conexión `ssh netlab360` **sí** funcionó tras encender la VM. El reinicio de la VM se comprobó operativamente; **la existencia/nombre del snapshot VMware no se puede determinar a partir de la salida**.
- Precheck posterior al arranque: `ens33 192.168.47.40/24`, gateway `192.168.47.2`, cero namespaces previos, Git limpio.
- `bash scripts/laboratorio/b2-l2-aislado.sh --snapshot-confirmado`: IPAM B1 OK (3 sedes, 9 VLAN, 2 WAN y 15 redes incluida VMnet8). El argumento `--snapshot-confirmado` es una declaración del operador; **no valida el Snapshot Manager**.

## Resultados observables

| Acción | Resultado |
|---|---|
| Crear namespaces `nl360-sw`, `nl360-a`, `nl360-b`, bridge `br-lab` y pares veth | Correcta |
| Puerto `sw-a` en VLAN 110; `sw-b` en VLAN 110 | Confirmado por `bridge vlan show` |
| Ping `10.70.10.10` a `10.70.10.11` | **3/3, 0% pérdidas**, RTT promedio **0.068 ms** |
| Cambiar `sw-b` a VLAN 120 | La prueba ICMP no recibió respuesta: separación observada |
| Regresar `sw-b` a VLAN 110 | **3/3, 0% pérdidas**, RTT promedio **0.044 ms** |
| Limpieza automática al finalizar | Namespaces eliminados, sin recursos L2 residuales |
| Ruta e interfaz host `ens33` | Sin cambios, IP estática `192.168.47.40/24` |
| Docker | Redes default bridge/host/none, sin contenedores |
| Salida | `PRUEBA B2-L2: OK`, `CODIGO_FINAL: 0`, `RESULTADO_B2=0` |
| Git | `## main...origin/main` limpio tras pruebas |

Log local **no cargado** al repo: `~/netlab360-bootstrap/evidencias/05-b2-l2-20261012-181601.log` (~1.6 KiB). No se ha confirmado una captura PNG de B2; las dos capturas que sí estaban confirmadas son las de B1.

## Alcance y límites

Esta prueba demuestra tres comportamientos de un Linux Bridge con puertos de acceso VLAN y cleanup idempotente mediante namespaces efímeros. **No demuestra** funcionamiento de trunk 802.1Q etiquetado entre switches, routing inter-VLAN, OSPF, failover WAN, LACP, redundancia de dispositivo, SDN/Faucet ni telemetría. Para validar aislamiento completo podrían ampliarse pruebas con inspección de tramas y firewall.

El diseño IPAM del laboratorio sigue en estado `draft`. El snapshot de recuperación `NETLAB360-BASE-HERRAMIENTAS` **no está confirmado desde la interfaz de VMware** por la evidencia recibida; verificar antes de iniciar la fase L3.

## Próximo avance

1. Revisar diseño B2 L3/OSPF para R-HQ y R-S1, enlazados por dos pares veth independientes con prefijos `10.78.0.0/30` y `10.78.0.4/30`, OSPF área 0, costos 10/100, loopbacks /32 y LAN anunciadas.
2. Preparar/inspeccionar imagen **FRRouting oficial Quay** (sin instalar daemon de routing en el anfitrión) y comprobar variante/version/tag y capacidades antes de provisionar routers.
3. Verificar snapshot VMware y conservar reversión; luego implementar PoC OSPF con captura previa, incidente y restauración de ruta.
4. Publicar pruebas y nuevos commits, actualizar #12 y el ancla `docs/00-estado-y-continuidad.md` antes de pausa.

**Seguridad:** no tocar `ens33`, VMnet8 ni redes Docker existentes, no versionar tokens, evitar ejecución de contenedores con `--privileged` sin justificación.
