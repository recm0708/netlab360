# NETLAB360 S02 — Enrutadores FRR aislados (Docker Compose)

**Estado:** manifiesto preparado, **no ejecutado en Ubuntu**. La configuración de origen es `inventario/ipam/topologia-s02.yaml` (candidate, 3 sedes, 9 VLAN, 4 enlaces WAN propuestos) y los archivos generados `~/netlab360-bootstrap/s02/rendered/R-*.frr.conf`.

## Intención

El archivo `docker-compose.yml` declara tres routers:
- `nl360-s02-r-hq` / `R-HQ`
- `nl360-s02-r-s1` / `R-S1`
- `nl360-s02-r-s2` / `R-S2`

Usan imagen probada `quay.io/frrouting/frr:10.7.1`, red **none** y directorios de configuración en `$HOME/netlab360-bootstrap/s02/runtime/R-<Sede>`. **No hay puertos publicados, interfaces hacia VMnet8, rutas del host ni cambios en ens33.** Se mantienen límites de memoria 512MB por router, procesos máximos 128 y capacidades similares a los laboratorios B2 validados, sin `--privileged`.

Las configuraciones FRR candidatas declaran interfaces `s1p`, `s1b`, `s2p` y `s2b` en los routers que correspondan. **No se crean tales interfaces por Docker Compose**; su aparición dependerá de una etapa posterior de pares veth en namespaces privados. Las interfaces `trunk0.<VLAN>` también son candidatas y **no existen aún**.

## Flujo de operación autorizado

1. Mantener consola VMware disponible y snapshot **confirmado en el registro**.
2. Git limpio, `precheck-s02.sh` cero, segunda conexión SSH probada desde Windows. No endurecer ni reiniciar SSH en esta fase.
3. Crear **solo en el directorio externo de runtime** las tres carpetas de FRR, copiar `frr.conf` generado, obtener plantilla `daemons` de imagen FRR y habilitar `zebra=yes`, `ospfd=yes`; añadir `vtysh.conf`; aplicar permisos/grupos compatibles con imagen previamente probada.
4. Ejecutar `sudo docker compose -f topologias/s02-frr/docker-compose.yml config --quiet` para verificar estructura. Confirmar `docker compose version` disponible.
5. Solo después de validar carpetas/configs y ausencia de los tres contenedores, ejecutar `sudo docker compose -f topologias/s02-frr/docker-compose.yml up -d`.
6. Validar `sudo docker compose -f topologias/s02-frr/docker-compose.yml ps -a`, logs y `sudo docker exec nl360-s02-r-hq vtysh -c 'show version'`; **0 vecinos OSPF es esperado SIN WAN veth**.
7. Verificar `ens33=192.168.47.40/24`, default GW `192.168.47.2`, `ip netns list`, contenedores propios y Git limpio.
8. Si se necesita detener **esta etapa SIN veth**, `sudo docker compose -f topologias/s02-frr/docker-compose.yml down` retira el stack Compose específico; conservar runtime y logs para análisis. Nunca usar `docker system prune`, `docker network prune`, `ip link delete` ni limpiezas globales.

## Próxima iteración

Preparar un plan de enlaces veth por namespace con nombre y pertenencia explícitos, comprobación OSPF cuatro adyacencias Full desde HQ y dos desde S1/S2, selección de rutas principales, falla/restauración controlada y rollback limitado a recursos propios. Solo después integrar VLAN y HTTP. **No ejecutar scripts B2 en presencia de estos routers S02**. La ejecución y sus resultados deben anotarse en la issue #2 y el informe académico-técnico único (7 Implementación, 8 Pruebas y 9 Análisis).


## Continuacion de WAN posterior al primer arranque correcto (23/10/2026)

**Primer arranque corregido VALIDADO en los registros del proyecto:** 3 routers FRRouting 10.7.1 operativos, `network_mode: none`, `S02_RESULTADO_ARRANQUE=0`, gestion `ens33=192.168.47.40/24` intacta. Captura de éxito confirmada `S02_05_FRR_Tres_Routers_Aislados_Validados`, PNG fisico aún no incorporado al repositorio.

**Siguiente procedimiento, de forma incremental:**
1. Ejecutar `python3 scripts/laboratorio/s02-wan-links.py plan` y `python3 -m unittest discover -s tests -p 'test_s02_wan_plan.py' -v` (solo lectura).
2. `sudo -v`, `python3 scripts/validacion/validar-ipam-s02.py`, `python3 scripts/laboratorio/s02-wan-links.py precheck`.
3. **Solo con instantanea VMware confirmada** y comandos anteriores correctos, `python3 scripts/laboratorio/s02-wan-links.py up --snapshot-confirmado`. Activa `net.ipv4.ip_forward=1` exclusivamente dentro de los tres namespaces FRR (recuerda sus valores previos para restaurarlos al desmontar); crea 3 loopbacks `10.79.0.1/32`–`.3/32`, cuatro pares veth `s1p,s1b,s2p,s2b` en contenedores FRR aislados, direcciones `10.78.0.0/30` a `10.78.0.12/30`, reaplica FRR. Cualquier fallo al crear enlaces hace rollback solo de los recursos propios si conserva identidad de contenedores.
4. `python3 scripts/validacion/validar-ospf-s02.py`: **prueba separada** hasta cuatro FULL en HQ, dos por sucursal, seis rutas FIB principales y seis pings de loopback incluyendo S1↔S2 vía HQ. **Si falla OSPF, no destruir los enlaces de inmediato: conservar estado y consultar vecinos, FIB, FRR/logs.**
5. `python3 scripts/laboratorio/s02-wan-links.py status` inspecciona interfaces/vecinos sin cambios. Evidencia `S02_06_WAN_OSPF_HQ_S1_S2_Cuatro_Enlaces` solo despues de resultados completos.
6. Para retirar **solo las cuatro WAN y loopbacks S02**, sin eliminar routers ni tocar VMnet8: `python3 scripts/laboratorio/s02-wan-links.py down`. Requiere estado de propiedad `~/netlab360-bootstrap/s02/wan-links-state.json` y tres IDs Docker originales; **NO ejecutar down si se quieren mantener WAN para LAN S02**.

**No ejecutar `docker compose down` si las WAN estan levantadas** sin retirarlas primero con el proceso propio. No ejecutar B2 sobre routers S02 y no usar comandos de limpieza global.
