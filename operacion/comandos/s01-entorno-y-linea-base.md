# Entorno y línea base — Fase 01

## Descripción

Preparamos las dependencias, el aislamiento administrativo
y los componentes iniciales de FRRouting y observabilidad.

## Comprobaciones del sistema

```bash
hostnamectl
cat /etc/os-release
ip -br address
ip -4 route
nproc
free -h
df -h /
bash operacion/verificar.sh
```

## Validación declarativa y pruebas offline

```bash
python3 scripts/validacion/validar_ipam.py inventario/ipam/topologia-b1.yaml
python3 -m unittest discover -s tests -p 'test_s01_*.py' -v
```

## Instalación y experimentación

La instalación de dependencias se realiza mediante
el procedimiento central de operación.

Conservamos los ensayos históricos de la fase 01
como componentes independientes:

- [Comprobación inicial FRR](../../scripts/laboratorio/b2-frr-smoke-v5-demonios-verificados.sh).
- [WAN redundante y OSPF](../../scripts/laboratorio/b2-dualwan-ospf.sh).
- [Trunk IEEE 802.1Q](../../scripts/laboratorio/b2-l2-trunk-8021q.sh).
- [HTTP y ACL](../../scripts/laboratorio/b2-l2-acl-http-real.sh).
- [Agregación IEEE 802.3ad](../../scripts/laboratorio/b2-lacp-8023ad-dos-enlaces.sh).
- [Exporter inicial](../../servicios/observabilidad/live_exporter.py).

Estos ensayos pueden crear recursos virtuales y requieren
revisar su código, precondiciones y alcance. No forman
parte del arranque de la topología multisede vigente.

## Documentación relacionada

- [Instalación general](../README.md).
- [Topología FRRouting inicial](../../topologias/b2-frr/README.md).
- [Preparación de Ubuntu](../../docs/infraestructura/ubuntu-desktop-y-ssh.md).
- [Validación de las fases 01–04](../../docs/validacion/s01-s04-resultados.md).
