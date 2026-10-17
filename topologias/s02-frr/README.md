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

1. Mantener consola VMware disponible y snapshot **confirmado por el usuario**.
2. Git limpio, `precheck-s02.sh` cero, segunda conexión SSH probada desde Windows. No endurecer ni reiniciar SSH en esta fase.
3. Crear **solo en el directorio externo de runtime** las tres carpetas de FRR, copiar `frr.conf` generado, obtener plantilla `daemons` de imagen FRR y habilitar `zebra=yes`, `ospfd=yes`; añadir `vtysh.conf`; aplicar permisos/grupos compatibles con imagen previamente probada.
4. Ejecutar `sudo docker compose -f topologias/s02-frr/docker-compose.yml config --quiet` para verificar estructura. Confirmar `docker compose version` disponible.
5. Solo después de validar carpetas/configs y ausencia de los tres contenedores, ejecutar `sudo docker compose -f topologias/s02-frr/docker-compose.yml up -d`.
6. Validar `sudo docker compose -f topologias/s02-frr/docker-compose.yml ps -a`, logs y `sudo docker exec nl360-s02-r-hq vtysh -c 'show version'`; **0 vecinos OSPF es esperado SIN WAN veth**.
7. Verificar `ens33=192.168.47.40/24`, default GW `192.168.47.2`, `ip netns list`, contenedores propios y Git limpio.
8. Si se necesita detener **esta etapa SIN veth**, `sudo docker compose -f topologias/s02-frr/docker-compose.yml down` retira el stack Compose específico; conservar runtime y logs para análisis. Nunca usar `docker system prune`, `docker network prune`, `ip link delete` ni limpiezas globales.

## Próxima iteración

Preparar un plan de enlaces veth por namespace con nombre y pertenencia explícitos, comprobación OSPF cuatro adyacencias Full desde HQ y dos desde S1/S2, selección de rutas principales, falla/restauración controlada y rollback limitado a recursos propios. Solo después integrar VLAN y HTTP. **No ejecutar scripts B2 en presencia de estos routers S02**. La ejecución y sus resultados deben anotarse en la issue #2 y el informe académico-técnico único (7 Implementación, 8 Pruebas y 9 Análisis).
