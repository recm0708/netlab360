# Infraestructura declarativa OpenTofu — S03

Utilizamos **OpenTofu 1.13.1** para registrar y verificar metadatos derivados del [inventario candidato multisede](../../inventario/ipam/topologia-s02.yaml).

## Recursos implementados

| Categoría | `terraform_data` |
|---|---:|
| Resguardo de gestión administrativa | 1 |
| Sedes HQ, S1 y S2 | 3 |
| Enlaces WAN | 4 |
| VLAN | 9 |
| **Total** | **17** |

Completamos `tofu init`, `validate`, `plan` y `apply` (**17 recursos añadidos, 0 modificados y 0 destruidos**). Un segundo plan no detectó cambios. Conservamos el `state` y los archivos de trabajo operativos fuera de Git, en `~/netlab360-bootstrap/s03/`.

**Límite del componente:** nuestros `terraform_data` representan metadatos; no crean routers FRRouting, enlaces WAN, interfaces ni VLAN. La configuración FRR en ejecución corresponde a [Ansible](../../ansible/s03/README.md). La integración de `data sources` y propiedad de recursos externos **no se implementó** en S03 y se registró como ampliación futura en [#17](https://github.com/recm0708/netlab360/issues/17).

No utilizamos `tofu apply` ni `tofu destroy` para tareas documentales. [Registro técnico de S03](../../docs/sesiones/2026-10-25-s03-opentofu-metadata-ci.md).
