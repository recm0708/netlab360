# NETLAB360 S03 — Infraestructura como código OpenTofu

**Estado técnico al 27/10/2026: aplicado y validado en Ubuntu.** La implementación comprende **17 recursos `terraform_data`**: guarda de red administrativa (1), sedes (3), enlaces WAN (4) y VLAN (9).

Se comprobaron `tofu init`, `validate`, plan de 17 adiciones, `apply` **17 added / 0 changed / 0 destroyed**, manifiesto de 3 sedes/4 WAN/9 VLAN y segundo plan **sin cambios**. El archivo `iac/s03/main.tf` consume el inventario declarado, en condición SoT `candidate`.

**Límite:** OpenTofu **administra metadatos y estado declarativo**, no crea los contenedores FRRouting, dispositivos, interfaces, VLAN ni enlaces. Los cambios de parámetros FRRouting en ejecución se evaluaron con Ansible en S03. No atribuir a los 17 recursos aprovisionamiento de una red externa.

Los estados, planes con datos operativos y el workspace se mantienen **fuera de Git**, bajo `~/netlab360-bootstrap/s03/`, y requieren manejo prudente. No usar `tofu destroy` ni volver a aplicar el estado existente para editar el informe. La decisión sobre data sources y ownership de recursos externos continúa abierta en [#17](https://github.com/recm0708/netlab360/issues/17).

[Sesión verificada](../../docs/sesiones/2026-10-25-s03-opentofu-metadata-ci.md) · [Continuidad](../../docs/REANUDAR-AQUI.md).
