# Automatización FRRouting

## Descripción

Implementamos auditoría y reconciliación con Ansible sobre los routers FRRouting de HQ, S1 y S2 a partir del inventario candidato multisede.

## Componentes

- [Playbook de cumplimiento](compliance-frr.yml).
- [Verificación del estado FRR](../../scripts/validacion/s03_frr_compliance.py).
- [Pruebas automatizadas](../../tests/test_s03_frr_compliance.py).
- [Topología declarativa](../../inventario/ipam/topologia-s02.yaml).

## Resultados

Comprobamos ocho costos OSPF configurados, con valores de 10 para enlaces principales y 100 para respaldos. Introdujimos una desviación controlada de costo **100 → 150** en S1 y confirmamos su detección. La reconciliación restauró el costo **150 → 100** y una ejecución posterior no requirió cambios.

## Limitaciones

Ansible administra la configuración FRRouting del laboratorio. La fuente de información tiene carácter de configuración candidata y no representa aprobación para un entorno productivo.

## Documentación relacionada

[Validación de entorno, red y observabilidad](../../docs/validacion/s01-s04-resultados.md) · [OpenTofu](../../iac/s03/README.md).
