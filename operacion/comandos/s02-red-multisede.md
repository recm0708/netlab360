# Red multisede

## Descripción

Integramos tres sedes, cuatro enlaces WAN y nueve VLAN
mediante FRRouting, OSPF, Docker y namespaces Linux.

## Validación y planificación

```bash
python3 scripts/validacion/validar_ipam_s02.py --static-only
python3 scripts/laboratorio/s02_wan_links.py plan
python3 scripts/laboratorio/s02_lan_vlan.py plan
python3 -m unittest discover -s tests -p 'test_s02_*.py' -v
```

## Consultas sobre la infraestructura activa

```bash
sudo -v
python3 scripts/laboratorio/s02_wan_links.py status
python3 scripts/validacion/validar_ospf_s02.py
python3 scripts/laboratorio/s02_lan_vlan.py status
python3 scripts/validacion/validar_lan_s02.py
```

Las comprobaciones de LAN pueden realizar sondas de
conectividad limitadas. No constituyen pruebas de carga.

## Construcción de una instalación nueva

Utilizamos la secuencia central de reconstrucción:

```bash
python3 operacion/reconstruir.py --plan
```

Los componentes de construcción son:

- [Generador FRR](../../scripts/automatizacion/render_frr_s02.py).
- [Preparación del runtime FRR](../../scripts/automatizacion/preparar_runtime_frr_s02.py).
- [Inicio de routers](../../scripts/laboratorio/s02-routers-start.sh).
- [Construcción WAN](../../scripts/laboratorio/s02_wan_links.py).
- [Construcción LAN](../../scripts/laboratorio/s02_lan_vlan.py).

No repetir operaciones de creación sobre una instalación
existente ni utilizar la interfaz administrativa como WAN.

## Ensayos de intervención

- [Conmutación WAN](../../scripts/laboratorio/s02_failover_wan.py).
- [Demostración HTTP y ACL](../../scripts/laboratorio/s02_http_acl_demo.py).

Estos ensayos requieren controles previos, autorización y
comprobaciones posteriores de restauración.

## Documentación relacionada

- [Topología multisede](../../topologias/s02-frr/README.md).
- [Inventario IPAM](../../inventario/ipam/topologia-s02.yaml).
- [Reconstrucción del laboratorio](../README.md).
