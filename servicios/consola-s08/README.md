# Consola interactiva — Fase 08

## Descripción

Integramos progresivamente las fuentes operacionales del
laboratorio en una aplicación local, sin sustituir los servicios
aceptados de las fases anteriores.

## Componentes

| Componente | Función |
|---|---|
| [api/main.py](api/main.py) | Servidor HTTP de arranque y rutas públicas mínimas |
| [api/security.py](api/security.py) | Identidades locales, roles y derivación scrypt |
| [Pruebas de identidades](../../tests/test_s08_identity.py) | Migración y verificación de cuentas sintéticas |
| [api/storage.py](api/storage.py) | Inicialización y comprobación de SQLite privado |
| [Pruebas de persistencia](../../tests/test_s08_storage.py) | Migración, permisos y conservación de bases |
| [api/models.py](api/models.py) | Esquemas Pydantic de metadatos públicos |
| [Pruebas de API](../../tests/test_s08_api.py) | Validación HTTP y restricciones de arranque |
| [api/contracts.py](api/contracts.py) | Contrato puro de metadatos de fuentes |
| [Pruebas de contratos](../../tests/test_s08_contracts.py) | Validación offline de vigencia, estado y límites de confianza |

## Alcance

El contrato no ejecuta consultas ni concede privilegios.
Incorporamos un servidor de arranque con dos rutas públicas
de metadatos, sin datos operacionales ni autorización.
Incorporamos una base SQLite privada de inicialización explícita.
La conexión de la persistencia a la API, autenticación, interfaz
gráfica y adaptadores requieren implementación independiente.

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

## Persistencia local

Desde el mismo directorio y sin root, con el directorio
`~/netlab360-bootstrap/s08` ya preparado:

```bash
"$HOME/netlab360-bootstrap/entornos/netlab360-s06-s08/bin/python" -B -m api.storage init
"$HOME/netlab360-bootstrap/entornos/netlab360-s06-s08/bin/python" -B -m api.storage check
```

La base se conserva en `~/netlab360-bootstrap/s08/estado/consola.sqlite3`,
fuera de Git. Exigimos directorio privado 0700, archivo 0600,
propietario actual y ausencia de enlaces en ambos recursos.
El directorio padre inmediato debe pertenecer al usuario y no
ser escribible por grupo u otros. Se presupone un árbol de runtime
administrado por el mismo usuario; no protege frente a ese usuario
ni frente a root. La migración inicial registra su versión y un evento
de inicialización. Los trabajos permanecen vacíos hasta disponer de
un coordinador autorizado. Una base desconocida o una migración
interrumpida se rechaza sin borrar ni sobrescribir datos.
El comando de comprobación utiliza SQLite en modo solo lectura.
La API todavía no abre esta base ni expone su contenido.

## Identidades locales

La migración explícita `python -m api.storage migrate` amplía
el esquema v1 a v2 sin reemplazar trabajos ni eventos anteriores.
Añade usuarios y sesiones, inicialmente vacíos. Las cuentas
locales admiten VIEWER y OPERATOR, ninguno autoriza mutaciones.
El alta local mediante `python -m api.security create-user nombre VIEWER`
lee la contraseña sin eco y exige al menos 15 caracteres.
Guardamos únicamente sal aleatoria y verificador scrypt
(N=131072, r=8, p=1), nunca la contraseña. La verificación
rechaza cuentas deshabilitadas y credenciales incorrectas.
No se habilita todavía el inicio de sesión HTTP ni la emisión
de sesiones. Antes de esa integración se requieren límites de
intentos y concurrencia, expiración y controles CSRF.

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
