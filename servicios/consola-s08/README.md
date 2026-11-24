# Consola interactiva — Fase 08

## Descripción

Integramos progresivamente las fuentes operacionales del
laboratorio en una aplicación local, sin sustituir los servicios
aceptados de las fases anteriores.

## Componentes

| Componente | Función |
|---|---|
| [api/contracts.py](api/contracts.py) | Contrato puro de metadatos de fuentes |
| [Pruebas de contratos](../../tests/test_s08_contracts.py) | Validación offline de vigencia, estado y límites de confianza |

## Alcance

El contrato no ejecuta consultas ni concede privilegios.
El servidor FastAPI, la persistencia, la autenticación, la
interfaz gráfica y los adaptadores requieren implementación
y validación independientes.

## Documentación relacionada

- [Diseño de la consola](../../docs/diseno/s08-consola-interactiva-y-acciones.md).
- [Contrato histórico de eventos S07](../../docs/diseno/s07-contrato-eventos-e-incidentes.md).
