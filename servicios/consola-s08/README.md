# Consola interactiva — Fase 08

## Descripción

Integramos progresivamente las fuentes operacionales del
laboratorio en una aplicación local, sin sustituir los servicios
aceptados de las fases anteriores.

## Componentes

| Componente | Función |
|---|---|
| [api/main.py](api/main.py) | Servidor HTTP de arranque y rutas públicas mínimas |
| [api/models.py](api/models.py) | Esquemas Pydantic de metadatos públicos |
| [Pruebas de API](../../tests/test_s08_api.py) | Validación HTTP y restricciones de arranque |
| [api/contracts.py](api/contracts.py) | Contrato puro de metadatos de fuentes |
| [Pruebas de contratos](../../tests/test_s08_contracts.py) | Validación offline de vigencia, estado y límites de confianza |

## Alcance

El contrato no ejecuta consultas ni concede privilegios.
Incorporamos un servidor de arranque con dos rutas públicas
de metadatos, sin datos operacionales ni autorización.
La persistencia, autenticación, interfaz gráfica y adaptadores
requieren implementación y validación independientes.

## Ejecución de desarrollo

Desde `servicios/consola-s08`, con el intérprete del entorno
científico de las fases 06–08 y sin elevar privilegios:

```bash
"$HOME/netlab360-bootstrap/entornos/netlab360-s06-s08/bin/python" -B -m api.main
```

El proceso escucha exclusivamente en 127.0.0.1:9140.
No se instala una unidad systemd en esta etapa. Se detiene
mediante Ctrl+C. El contrato HTTP de arranque ofrece:

| Ruta GET | Alcance |
|---|---|
| /healthz | Disponibilidad del proceso; infraestructura UNKNOWN |
| /api/v1/capabilities | Funciones disponibles y deshabilitadas |

La API no admite escrituras, documentación OpenAPI pública,
consultas de fuentes ni acceso a datos privados.
La ejecución sin autenticación solo corresponde a estos
metadatos de arranque. No constituye una consola autenticada.

## Validación

Ejecutamos las pruebas HTTP con las dependencias científicas.
El job dedicado de CI instala únicamente FastAPI, Uvicorn,
Pydantic y HTTPX con las restricciones de versiones del
inventario científico, sin instalar los modelos históricos.
La prueba de reconstrucción del entorno completo permanece
pendiente.

## Documentación relacionada

- [Diseño de la consola](../../docs/diseno/s08-consola-interactiva-y-acciones.md).
- [Contrato histórico de eventos S07](../../docs/diseno/s07-contrato-eventos-e-incidentes.md).
