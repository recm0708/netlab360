# NETLAB360 — Estado consolidado de continuidad

**Actualizado: 01/11/2026.** Finalizamos por alcance técnico interno S01–S04. La profesora consideró adecuado el avance presentado el 30/10 y autorizó continuar con el siguiente entregable, según confirmó el equipo. El trabajo funcional y la aceptación final de S05–S08 continúan pendientes.

## Implementación comprobada

- **S01–S02:** base Ubuntu/VMware, FRRouting/OSPF, tres sedes, cuatro WAN, nueve VLAN, fallos y recuperación.
- **S03:** SoT `candidate`, auditoría y reconciliación Ansible FRR real, 17 recursos locales `terraform_data` y CI. Recursos externos OpenTofu: **no implementados**, reprogramados a S05+.
- **S04:** observabilidad NOC/Prometheus, eventos WAN, UNKNOWN, SQLite/TSDB persistentes; SLI 15m **100 %** y 60m **97,586 %**, por debajo de la referencia experimental 99 %.

## Entregables

Conservamos el informe único 4.6 de 113 páginas, 20 figuras, 13 tablas y 122 PNG oficiales bajo control criptográfico. La siguiente revisión por Teams es el **13/11/2026**; TAR, PowerPoint y defensa se prepararán durante S08.

## Infraestructura y seguridad

VM `netlab360-lab`, Ubuntu Desktop 26.04.1, gestión `ens33 192.168.47.40/24` y gateway `192.168.47.2`. SSH ED25519 sin contraseña remota, respaldo local protegido y consola VMware probados. La VM estaba encendida en la sesión del 01/11; verificar apagado real al finalizar.

[Reanudar](REANUDAR-AQUI.md) · [Tablero de fases](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md).
