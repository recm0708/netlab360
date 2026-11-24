# Catálogo de comandos de NETLAB360

## Descripción

Organizamos los procedimientos de operación por fase.
Reutilizamos los scripts y configuraciones versionados,
sin mantener implementaciones duplicadas.

Los comandos se ejecutan desde la raíz del repositorio,
salvo cuando el procedimiento indique una copia
administrativa independiente y protegida.

## Comandos transversales

Para consultar los requisitos y los planes disponibles:

```bash
bash operacion/verificar.sh
bash operacion/instalar.sh --plan
bash operacion/configurar.sh --plan
bash operacion/preparar-runtime.sh --plan
bash operacion/instalar-protegidos.sh --plan
python3 operacion/instalar_servicios.py --plan
bash operacion/desplegar.sh --plan
python3 operacion/reconstruir.py --plan
python3 operacion/ciclo_vida.py shutdown-plan
```

Para consultar una instalación activa:

```bash
sudo -v
bash operacion/estado.sh
```

## Procedimientos por fase

| Fase | Procedimiento |
|---|---|
| 01 | [Entorno y línea base](s01-entorno-y-linea-base.md) |
| 02 | [Red multisede](s02-red-multisede.md) |
| 03 | [Automatización](s03-automatizacion.md) |
| 04 | [Observabilidad](s04-observabilidad.md) |
| 05 | [HA, LACP y SDN](s05-ha-lacp-sdn.md) |
| 06 | [Diagnóstico inteligente](s06-diagnostico-inteligente.md) |
| 07 | [AIOps supervisado](s07-aiops-supervisado.md) |

## Criterios de ejecución

Diferenciamos las consultas, las pruebas offline,
la adquisición experimental, la instalación y las
intervenciones sobre recursos activos.

No ejecutamos todos los comandos como una secuencia
indiscriminada. Cada procedimiento conserva sus
precondiciones, controles de propiedad y autorización.

Los scripts de experimentación histórica se utilizan
en escenarios independientes y no como instaladores
de la topología integrada.

No reutilizamos autorizaciones, sesiones, identidades,
tokens ni estados privados de otras instalaciones.

La reconstrucción desde un sistema limpio y la
recuperación automática después de apagar Ubuntu
requieren validación independiente.

## Documentación relacionada

- [Instalación y operación](../README.md).
- [Arquitectura multisede](../../docs/arquitectura/arquitectura-multisede-implementada.md).
- [Convenciones del proyecto](../../.github/CONTRIBUTING.md).
