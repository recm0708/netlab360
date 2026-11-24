# Consola interactiva — Fase 08

## Descripción

Integramos progresivamente las fuentes operacionales del
laboratorio en una aplicación local, sin sustituir los servicios
aceptados de las fases anteriores.

## Componentes

| Componente | Función |
|---|---|
| [api/ui_http.py](api/ui_http.py) | Publicación de HTML y recursos visuales fijos |
| [ui/index.html](ui/index.html) | Estructura visual inicial y metadatos públicos |
| [api/advisory_reader.py](api/advisory_reader.py) | Resúmenes históricos de la API Unix S07 |
| [Pruebas del asesor](../../tests/test_s08_advisory.py) | Identidad del servidor, vigencia y límites de lectura |
| [api/inference_reader.py](api/inference_reader.py) | Inferencia exploratoria S06 mediante NOC |
| [Pruebas de inferencia](../../tests/test_s08_inference.py) | Abstención, vigencia y acceso HTTP |
| [api/prometheus_reader.py](api/prometheus_reader.py) | Métricas de scrapes mediante el adaptador S07 |
| [Pruebas de métricas](../../tests/test_s08_metrics.py) | Reutilización, vigencia y acceso HTTP |
| [api/readers.py](api/readers.py) | Lectura fija de exporter S04 y NOC S05 |
| [api/source_http.py](api/source_http.py) | Consulta de observaciones autenticada |
| [Pruebas de lectores](../../tests/test_s08_readers.py) | Transporte, vigencia y alcance de fuentes |
| [api/main.py](api/main.py) | Servidor HTTP de arranque y rutas públicas mínimas |
| [api/auth_http.py](api/auth_http.py) | Login, identidad, roles y cierre de sesión HTTP |
| [api/sessions.py](api/sessions.py) | Sesiones opacas, expiración y revocación |
| [Pruebas HTTP de autenticación](../../tests/test_s08_auth.py) | Validación con cuentas sintéticas |
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
Integramos la autenticación HTTP como modo explícito sobre SQLite v2.
Integramos los lectores de exporter, NOC, Prometheus, inferencia S06 y
asesor S07. Incorporamos la estructura visual y el acceso gráfico; la navegación
de detalle y las acciones requieren implementación independiente. La disponibilidad de una ruta no garantiza la de su fuente.

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

El modo de arranque no admite escrituras, documentación OpenAPI pública,
consultas de fuentes ni acceso a datos privados.
La ejecución sin autenticación solo corresponde a estos
metadatos de arranque. No constituye una consola autenticada.

## Interfaz gráfica inicial

En modo autenticado servimos la estructura HTML, CSS y JavaScript
en la raíz del mismo origen. No publicamos el árbol de archivos,
no utilizamos CDN ni abrimos rutas privadas sin sesión.
La pantalla inicial consulta healthz y capabilities sin credenciales.
El formulario utiliza login, me y logout del mismo origen, sin guardar
credenciales ni tokens en almacenamiento web. El comprobante CSRF queda
solo en memoria. Al recargar se exige otro login, que reemplaza la sesión
previa de la misma cuenta; la recarga no implica revocación remota.
La UI indica el rol y la expiración, pero no autoriza acciones. Los estados
operacionales no consultados permanecen UNKNOWN. La navegación de detalle
y Plotly se integrarán por separado. La política CSP permite solo scripts, estilos
y consultas del mismo origen, sin código inline.

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
El modo autenticado utiliza esta base para identidades y sesiones; no expone su contenido íntegro.

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
## Autenticación HTTP local

El modo de arranque anterior conserva sus dos rutas públicas.
Para habilitar identidades sobre la base v2, iniciamos el servidor con
`NETLAB360_S08_AUTH=1` antes del comando de ejecución.
La aplicación no crea cuentas por HTTP.

| Ruta | Control |
|---|---|
| POST /api/v1/auth/login | Origen local exacto, JSON acotado y credenciales |
| GET /api/v1/auth/me | Cookie de sesión vigente |
| GET /api/v1/auth/operator-check | Sesión con rol OPERATOR |
| POST /api/v1/auth/logout | Origen exacto, sesión y token CSRF |

Emitimos tokens opacos de 256 bits con verificadores almacenados,
una sesión por cuenta y expiración absoluta de 30 minutos.
La cookie es HttpOnly y SameSite Strict; la bandera Secure queda
pendiente de HTTPS, pues el modo de desarrollo utiliza HTTP local
sobre túnel SSH. El token CSRF se devuelve al iniciar sesión y no
se registra. La UI deberá conservarlo en memoria; al perderlo
se inicia sesión nuevamente. Las escrituras operacionales siguen
deshabilitadas. Limitamos el login a ocho intentos por minuto
por proceso y una derivación scrypt concurrente, sin cola.
Este límite local se reinicia con el proceso y no constituye
protección distribuida. No habilitamos acceso externo.

## Observaciones operacionales

En modo autenticado, GET /api/v1/sources devuelve observaciones
normalizadas del exporter S04 (existencia de routers) y NOC S05
(topología observada, LACP por sede, controlador SDN y HTTP HA).
El estado general permanece UNKNOWN. Conservamos fechas individuales;
los detalles no vigentes se omiten. Las lecturas utilizan destinos
loopback fijos, sin redirecciones ni proxies, con cuerpo máximo de
256 KiB y timeout de socket de tres segundos. Una adquisición concurrente por endpoint (hasta cuatro en el proceso);
los errores de una fuente no reemplazan los datos de otra. No se aceptan parámetros de consulta.
La topología gráfica, WAN/VLAN detalladas y la presentación científica
y asesora de detalle requieren integración posterior. No se expone el grafo bruto.

## Métricas Prometheus

GET /api/v1/metrics requiere sesión vigente y no admite parámetros.
Reutilizamos el [adaptador Prometheus S07](../../scripts/s07/adaptador_prometheus.py)
para la consulta fija de 120 segundos y la proyección de 23 observaciones
con fecha del scrape real. El transporte S08 conserva el límite de
512 KiB de esta fuente, sin proxy ni redirecciones. El endpoint tiene su propio límite de una adquisición concurrente.
El estado administrativo de WAN/VLAN no demuestra forwarding u OSPF.
No exponemos PromQL arbitrario ni series históricas completas.
La clave JSON schema conserva su nombre mediante un alias Pydantic.

## Diagnóstico exploratorio

GET /api/v1/diagnostics requiere sesión vigente y no admite parámetros.
Reutilizamos el adaptador de inferencia S07 sobre el gateway NOC S05,
sin iniciar el servicio S06 ni ejecutar mediciones. Conservamos dos
rutas HQ_A_S1 y HQ_A_S2, vigencia de 30 segundos, procedencia de
inferencia y ground truth UNKNOWN. Una indicación de degradación
o discrepancia de modelos no equivale a un incidente confirmado.
Si no existe una muestra utilizable se omiten los detalles y se
devuelve UNKNOWN; el resto de fuentes permanece independiente.
No se autoriza el despliegue productivo ni cambios de red.
La consulta asesora S07 permanece independiente de la inferencia.

## Consulta asesora S07

GET /api/v1/advisory requiere sesión vigente y no admite parámetros.
Consultamos exclusivamente incidents, hypotheses y runbooks mediante
el socket Unix protegido existente, verificando propietario root y
credenciales del servidor con SO_PEERCRED. No iniciamos el servicio
ni enviamos escrituras. Un socket ausente se representa como NOT_STARTED.
Proyectamos cantidades de candidatos, hipótesis, recomendaciones,
brechas y runbooks declarativos, no contenido bruto ni comandos.
El snapshot es histórico y nunca autoriza acciones ni acredita salud.
Si supera 60 segundos, omitimos los detalles y conservamos su fecha.
La presentación detallada y el acceso operacional con identidad
dedicada quedan pendientes. No ampliamos permisos del socket.

## Frontera de ejecución

La identidad de desarrollo no constituye la identidad del servicio.
La ejecución aislada deberá usar un UID sin privilegios, sin sudo,
sin grupo Docker y sin acceso al socket mutador S07. No concedemos
el UID del operador histórico a un servicio web para facilitar una
consulta. Cuando la identidad dedicada no pueda consultar S07,
la aplicación conservará UNAVAILABLE/MISSING/UNKNOWN; la futura
interfaz asesora separada y el ejecutor autorizado requieren validación.
Los indicadores de capacidades señalan rutas habilitadas, no fuentes
vigentes ni autorización administrativa.

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
