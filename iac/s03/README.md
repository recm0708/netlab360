# Infraestructura declarativa con OpenTofu

## Descripción

Utilizamos OpenTofu 1.13.1 para representar metadatos de las sedes, enlaces y VLAN definidos en el inventario de NETLAB360.

## Componentes

| Categoría | Objetos locales |
|---|---:|
| Protección de administración | 1 |
| Sedes HQ, S1 y S2 | 3 |
| Enlaces WAN | 4 |
| VLAN | 9 |
| **Total** | **17** |

## Resultados

Comprobamos la inicialización, validación, planificación y aplicación de los **17 recursos locales**, sin modificaciones ni destrucciones posteriores. La siguiente planificación confirmó que no existían cambios declarativos pendientes.

## Limitaciones

Los objetos `terraform_data` representan metadatos; **no crean routers, interfaces ni VLAN externas**. La configuración activa de FRRouting se gestiona mediante Ansible. El estado de ejecución de OpenTofu se conserva fuera del repositorio.

## Documentación relacionada

[Inventario multisede](../../inventario/ipam/topologia-s02.yaml) · [Ansible de la fase 03](../../ansible/s03/README.md) · [Validación de las fases 01–04](../../docs/validacion/s01-s04-resultados.md).
