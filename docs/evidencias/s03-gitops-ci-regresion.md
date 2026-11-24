# Evidencia GitOps y CI — Fase 03

## Descripción

La tercera fase incorporó control de versiones para las configuraciones candidatas de la red multisede, junto con pruebas de integración continua que permiten detectar regresiones antes de consolidar cambios.

## Implementación

Los cambios se gestionaron mediante ramas de desarrollo y solicitudes de incorporación en GitHub. Los flujos de CI ejecutaron comprobaciones de Python, herramientas declarativas, sintaxis Bash y contratos de FRRouting y topología.

## Validación

Tras integrar la automatización, comprobamos que la configuración de FRRouting continuaba disponible y que la infraestructura multisede podía mantener sus tres sedes, cuatro enlaces WAN y nueve VLAN. La reconciliación de configuración y las pruebas de regresión se realizaron sobre los recursos definidos para la fase 03.

El estado local de OpenTofu conservó **17 objetos de metadatos**, sin que se atribuya a estos recursos la creación de enlaces o routers externos.

## Evidencias

Las capturas de SoT, compliance, reconciliación de cambios y ejecución de GitOps se encuentran en la [fase 03](../../evidencias/capturas/fase3/README.md).

## Limitaciones

La integración continua no sustituye una prueba operativa del laboratorio VMware y no certifica el estado de servicios que requieran contenedores o namespaces activos.

## Documentación relacionada

[Automatización Ansible](../../ansible/s03/README.md) · [OpenTofu de la fase 03](../../iac/s03/README.md) · [Resultados de las fases 01–04](../validacion/s01-s04-resultados.md).
