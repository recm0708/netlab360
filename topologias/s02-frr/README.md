# Topología FRRouting HQ/S1/S2 — S02

Implementamos y comprobamos una infraestructura virtual de tres sedes mediante [`docker-compose.yml`](docker-compose.yml) y configuraciones renderizadas desde [la SoT candidata](../../inventario/ipam/topologia-s02.yaml).

## Componentes

Los contenedores `nl360-s02-r-hq`, `nl360-s02-r-s1` y `nl360-s02-r-s2` emplean FRRouting 10.7.1 con `network_mode: none`; los scripts de laboratorio crean los enlaces aislados en la VM. El workspace de configuración generado se conserva fuera de Git, en `~/netlab360-bootstrap/s02/rendered/`.

Trabajamos con **cuatro WAN** (s1p/s1b/s2p/s2b), costos OSPF 10/100 y **nueve VLAN** distribuidas entre las tres sedes. Validamos OSPF Full **4/2/2**, rutas preferidas **6/6**, pruebas de loopback **6/6**, gateways de VLAN **9/9**, conectividad LAN **6/6**, failover y restricciones HTTP/ACL.

## Operación

Desplegamos con scripts controlados de [`scripts/laboratorio/`](../../scripts/laboratorio/) y retiramos los componentes en orden LAN → WAN → FRR al finalizar S04. Nunca conectamos redes experimentales a `ens33` ni modificamos la ruta administrativa VMware para simular fallos.

El mismo escenario sirvió de base para el [cumplimiento Ansible S03](../../ansible/s03/README.md) y la [observabilidad S04](../../servicios/observabilidad/README.md). Las validaciones originales no requieren repetir el despliegue para documentarse.

[Resultados y aceptación S02](../../docs/validacion/s01-s04-resultados.md).
