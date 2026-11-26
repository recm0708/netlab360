# Consola interactiva y acciones

**Estado:** backend, sesiones, dashboard, topología SVG, vistas por dominio, históricos Plotly y explorador Swagger implementados y validados incrementalmente. Conservamos el despliegue local de desarrollo; la equivalencia completa, inferencia activa, pruebas de red, sondas, actuación protegida, administración de identidades y reconstrucción permanecen pendientes.

## 1. Experiencia de usuario

Una sola aplicación local, con barra lateral, encabezado de estado general y panel central. Cada acción muestra origen/destino, alcance, parámetros seguros, coste/duración, estado anterior, resultado, gráficos, timestamps UTC/locale y evidencia descargable. Los estados **NORMAL, DEGRADED, FAULT, RECOVERY, UNKNOWN** se calculan a partir de señales reales y edad de observaciones; *sin datos* nunca equivale a *todo bien*.

### Menú propuesto

| Pantalla | Consultas y resultados | Acciones permitidas |
|---|---|---|
| **1. Inicio / Salud** | Sedes HQ/S1/S2, 21 namespaces, 4 contenedores, 7 servicios, salud de fuentes y acciones recientes; sin asumir cantidades fijas en runtime | Actualizar inventario; diagnóstico seguro |
| **2. Topología en vivo** | Diagrama NOC existente, 18 nodos/21 enlaces de referencia, rutas primarias/respaldo, colores por estado y tooltips | Seleccionar elemento para mediciones/diagnósticos |
| **3. Redes/WAN/OSPF** | Vecinos FULL, costos, FIB, cuatro enlaces, ruta efectiva y causa probable | Estado de FRR; escenarios conmutación/autorización y retorno |
| **4. LAN/VLAN/ACL** | Nueve VLAN, endpoints, conectividad permitida/denegada y segmentación | Ping y pruebas de política entre endpoints autorizados |
| **5. Servicios HTTP/HA** | Backend activo, latencia HTTP, errores, monitor y traza de selección | Prueba HTTP, conmutación HA controlada, restauración |
| **6. LACP** | Cada sede, miembros por extremo 2/2, velocidad/estado, degradación | Ensayo autorizado 2→1→2 con rollback |
| **7. SDN/OVS/Faucet** | Estado del controlador, puertos, VLAN410/420, reglas y aislamiento | Verificar comunicación y aislamiento; falla/retorno de puerto autorizado |
| **8. Pruebas de red** | Ping corto/extendido, traceroute, HTTP, iperf3 TCP/UDP con origen/destino permitido, pérdidas, RTT, tasa, jitter si se observa | Lanzar ensayo **acotado**, guardar resultado y compararlo |
| **9. Observabilidad** | Prometheus, Blackbox, SLI/SLO de servicio, error budget, burn rate, Alertmanager, históricos, latencia P50/P95, pérdida y calidad de fuente | Seleccionar ventana/servicio y exportar gráfica o evidencia |
| **10. Diagnóstico IA** | Detección, scores, explicación, confianza/UNKNOWN, baseline de reglas, pronóstico y deriva **pendientes de evaluación científica** | Inferencia solo lectura; consulta de evidencia |
| **11. Incidentes y AIOps** | Correlación de fuente, línea de tiempo, recomendación, riesgo y postcondición mediante la API protegida validada, con lector de resúmenes de la consola y presentación detallada pendiente | Crear solicitud, consultar estado y resultado; aprobación administrativa separada, ejecución protegida y retorno |
| **12. Copiloto RAG** | Respuestas con fuentes propias, incertidumbre y citas | Consultas de solo lectura; sin autorización de cambios (#198) |
| **13. Evidencias y sistema** | Historial de trabajos, logs sanitizados, versiones, tests, métricas y catálogo | Descargar resultados JSON/CSV, generar inventario técnico y comprobar salud |
| **14. Usuarios y seguridad** | Perfil propio, cuentas, roles, sesiones y auditoría de acceso (#242) | Cambios autorizados de identidad, contraseña y MFA; administración separada de privilegios operacionales |
| **15. Diagnóstico técnico** | Catálogo de API, salud de aplicación, respuestas y errores sanitizados (#243) | Consultas de lectura permitidas, copia y exportación delimitada; sin shell, proxy arbitrario ni cambios de red |

El diagnóstico técnico está implementado y reservado inicialmente a OPERATOR. La administración de identidades conserva su ruta, sin operaciones administrativas habilitadas. La administración
propia estará disponible a cada usuario; la administración de terceros
requiere un futuro rol ADMIN con MFA y reautenticación para operaciones
sensibles. La identidad ADMIN no implica privilegios de root ni permiso
operacional. El diagnóstico técnico se reserva inicialmente a OPERATOR.

**Diseño adaptable:** desktop en VMware/Windows con barra lateral fija; tarjetas en pantallas estrechas; secciones sin implementación muestran `PENDIENTE` explícitamente, nunca resultados ficticios. Mantenemos el NOC anterior accesible hasta verificar equivalencia y dependencias.

## 2. Arquitectura escogida (preferencia práctica)

- **UI:** HTML/CSS/JavaScript con componentes sencillos y gráficas Plotly. Reutilizar modelos y SVG/visuales del `servicios/topologia-s05/index.html`; no crear un segundo NOC desconectado. Dash opcional solo si se acredita beneficio de integración, no necesario para un menú.
- **Backend:** Python FastAPI + Uvicorn usando entorno virtual científico. Endpoints tipados para estado, series, pruebas, catálogo, ejecuciones y evidencia. Servir API y frontend desde la misma aplicación (sin CORS público).
- **Fuentes:** adaptadores locales del exportador de telemetría `127.0.0.1:9110`, NOC topológico `127.0.0.1:9130`, Prometheus local `9091` si está activo, histórico SQLite, estados de operación y módulos de diagnóstico y AIOps.
- **Persistencia propia:** SQLite privado bajo `netlab360-bootstrap/s08/` con registros de trabajos/eventos, parámetros validados, acciones, estados previos y posteriores y artefactos; **no** dentro de Git.
- **Exposición:** por defecto solo `127.0.0.1:9140` en la VM. Demo desde Windows: túnel SSH `ssh -L 9140:127.0.0.1:9140 rc-aa-ec@192.168.47.40`; navegador Windows `http://127.0.0.1:9140`. Acceso externo solo tras revisar controles de autenticación, CSRF y autorizaciones.
- **Protocolo UI:** peticiones REST + actualización ligera por polling/SSE; límites de frecuencia y tiempo. Evitar WebSockets por defecto si no se justifican.

### Compatibilidad y dependencias

Conservamos el entorno científico de referencia para la compatibilidad de la consola.
La comprobación previa se realizó con Python
3.14.4 sobre Ubuntu 26.04.1 LTS,
sin instalar ni actualizar paquetes.

| Biblioteca | Versión comprobada |
|---|---|
| NumPy | 2.5.5 |
| Pandas | 3.1.1 |
| SciPy | 1.18.1 |
| scikit-learn | 1.9.1 |
| Joblib | 1.6.0 |
| FastAPI | 0.165.0 |
| Uvicorn | 0.54.0 |
| Pydantic | 2.14.4 |
| Plotly | 7.1.0 |
| Dash | 4.5.1 |
| HTTPX | 0.28.1 |
| Prometheus Client | 0.26.0 |

Registramos las versiones de las distribuciones instaladas en
el [inventario de dependencias científicas](../../requirements-cientifico.txt).
Este archivo incluye dependencias directas y transitivas, pero
no constituye un lockfile con hashes de distribución ni acredita
una reconstrucción limpia del entorno.

Comprobamos la consistencia mediante `pip check`, las
importaciones principales y la suite de inferencia histórica
utilizando su intérprete científico. La prueba de rutas FastAPI
omitida en la regresión general se ejecutó satisfactoriamente
en este entorno.

Para reproducir el entorno utilizaremos inicialmente un entorno
virtual separado, verificando la versión de Python, disponibilidad
de distribuciones, procedencia y compatibilidad de las bibliotecas.
No actualizaremos el entorno histórico ni volveremos a entrenar
los modelos para satisfacer dependencias de la interfaz.

Las dependencias adicionales de la consola se incorporarán
durante su implementación, con versiones verificadas y pruebas
propias. La validación de reconstrucción completa permanece
pendiente.

## 3. Organización del código y de los comandos

```text
servicios/consola-s08/
    api/
        main.py              # FastAPI y rutas publicas controladas
        models.py            # Esquemas de entrada/salida
        readers.py           # Adaptadores S04/S05
        prometheus_reader.py # Scrapes de Prometheus
        inference_reader.py  # Inferencia S06
        advisory_reader.py   # Consulta asesora S07
        storage.py           # SQLite privado
        auth_http.py         # Autenticación HTTP
        sessions.py          # Sesiones opacas
        source_http.py       # Endpoints de lectura
        jobs.py              # Estado, colas y auditoria
        security.py          # Acceso, roles y confirmaciones
    ui/
        index.html
        static/              # CSS, JS y graficas
    README.md
config/s08/
    acciones.yaml            # IDs, permisos, limites, comandos de despliegue
scripts/s08/acciones/
    consultas/              # ping, traceroute, http, iperf, estados
    escenarios/             # WAN, HA, LACP, SDN, netem limitados
    recuperacion/           # rollback y validacion de postcondiciones
tests/
    test_s08_api.py
    test_s08_actions.py
    test_s08_security.py
    test_s08_ui.py
```

**Flujo de un clic:** usuario elige `action_id` + parámetros tipados → backend consulta registro `acciones.yaml` → verifica política/destinos y prechecks → autorización humana si cambia estado → ejecutor con permisos mínimos invoca **script revisado por ruta fija** → almacena resultados y hash → revalida red/NOC → UI presenta métricas y retorno.

**Crítico:** NO pasar cadenas libres a `bash -c`, `shell=True`, `sudo` con rutas de scripts editables por el usuario o interpolaciones del navegador. Los scripts que requieran privilegios deben instalarse como ejecutores **propiedad root, no editables por usuario web**, y recibir únicamente acciones/argumentos autorizados; el observador de topología permanece read-only. Verificar política de ejecución y pruebas de intrusión antes de conectar botones que produzcan fallos.

### Contrato de integración y fronteras de confianza

Separamos el transporte, la calidad temporal y el estado observado.
Una respuesta HTTP correcta no acredita el estado de un servicio;
una fuente ausente, inválida, futura u obsoleta se representa como
UNKNOWN. No sustituimos la fecha de la muestra por la hora de recepción.

| Fuente | Interfaz existente | Alcance |
|---|---|---|
| Exporter S04 | 127.0.0.1:9110/api/v1/state | Existencia de routers y flags administrativos |
| NOC S05 | 127.0.0.1:9130/api/v1/graph | Grafo y observaciones de WAN, VLAN, FIB, LACP, SDN y HA |
| Prometheus S04 | 127.0.0.1:9091/api/v1/query | Scrapes y métricas; reutilizamos el adaptador fijo S07 |
| IA S06 | 127.0.0.1:9130/api/v1/s06/diagnostics | Inferencias ICMP; depende de la API 9145 |
| AIOps S07 | Socket Unix /run/netlab360-s07-api/api.sock | Snapshot asesor y RFC; autorización administrativa separada |

El [contrato de fuentes S08](../../servicios/consola-s08/api/contracts.py)
define metadatos de recepción, fecha de observación, antigüedad,
calidad y estado. Reutilizamos la semántica temporal de S07
(60 segundos para observaciones y 30 para inferencias).
El límite de 60 segundos del snapshot asesor es una política
inicial de S08, no una garantía de adquisición periódica.
El timestamp global del grafo indica su generación, no la
vigencia de cada observación: los adaptadores deben comprobar
las fechas individuales de telemetría, LACP, SDN y HA.
Los eventos S07 conservan su contrato original; no los
reescribimos como eventos S08.

El backend se ejecutará sin root, con identidad de servicio
dedicada y sin acceso al grupo Docker ni sudo genérico.
La integración privilegiada se limita a los mecanismos
revisados de S07, con identidad Unix y autorización
administrativa independiente. No habilitamos esas capacidades
en el backend inicial. Los adaptadores resolverán fuentes
por identificador fijo, sin URLs, rutas o PromQL arbitrarios
suministrados por el cliente. Se rechazarán redirecciones,
proxies externos, respuestas excesivas y estructuras inválidas.

La persistencia S08 será independiente de las bases históricas,
con directorio privado 0700 y archivos 0600, inicialización
explícita, consultas parametrizadas y migraciones versionadas.
No se almacenarán contraseñas en texto plano ni tokens de
sesión en logs. La UI y la API compartirán origen y tendrán
sesiones opacas con expiración, cookies HttpOnly y SameSite,
control de origen y CSRF para escrituras, y roles de espectador
y operador. La autenticación local no equivale a autorización
root. HTTPS será requisito para exposición no local; la demo
inicial utilizará loopback y túnel SSH.

La versión inicial del contrato es offline: no abre sockets,
no crea bases, no inicia servicios y no concede permisos.
La integración FastAPI, persistencia, controles de sesión
y lectores se validan mediante pruebas independientes de la infraestructura.
La identidad de servicio se mantiene separada del operador S07;
no se amplían permisos de su socket mutador para permitir consultas.

### Servidor de arranque

El [componente de consola](../../servicios/consola-s08/README.md)
incorpora dos rutas GET de metadatos públicos, con modelos
Pydantic estrictos y arranque sin root en loopback. La salud
del proceso no representa salud de la red. Las operaciones
de fuentes, persistencia y autenticación se habilitan únicamente
mediante el modo autenticado sobre SQLite v2. Frontend, pruebas de red
y mutaciones permanecen deshabilitados. Los endpoints de lectura tienen
límites de concurrencia independientes. La disponibilidad de las rutas
no acredita la vigencia de sus fuentes.
No habilitamos CORS ni documentación OpenAPI pública.
Las pruebas HTTP no requieren Docker ni acceso privilegiado.

## 4. Catálogo inicial de acciones (IDs estables)

| ID | Tipo | Parámetros límite | Resultado esperado |
|---|---|---|---|
| `state.topology` | Lectura | ninguno | Inventario/health con timestamp y antigüedad |
| `state.ospf` | Lectura | sede enum HQ/S1/S2 | Vecinos y rutas observados |
| `test.ping.short` | Prueba | origen/destino del IPAM, 4 paquetes, timeout 2 s | Envíos, recibidos, pérdida y RTT |
| `test.ping.long` | Prueba | origen/destino permitidos, 20 paquetes como máximo | Estadística y p95 si hay muestras |
| `test.traceroute` | Prueba | origen/destino permitidos, máx. 12 saltos, timeout limitado | Saltos y tiempos |
| `test.http` | Prueba | URL o servicio **predefinidos**, timeout 5 s | Código HTTP, latencia, backend/errores |
| `test.iperf.tcp` | Prueba | endpoints registrados, máx. 10 s, 1 sesión concurrente | Throughput y retransmisiones si disponibles |
| `test.iperf.udp` | Prueba | endpoints registrados, máx. 10 s, techo 20 Mbit/s, 1 sesión concurrente | Throughput, jitter y pérdida si observados |
| `check.vlan` | Lectura/prueba | sede y política predefinidas | Verificación de segmentación |
| `check.sdn` | Lectura/prueba | A↔B y A↔C esperadas | Aislamiento observado |
| `scenario.wan.failover` | Cambio supervisado | solo WAN experimental, TTL y rollback | Ruta alternativa, FIB y restauración |
| `scenario.http.failover` | Cambio supervisado | backend HQ→S1→HQ, TTL y rollback | Traza/latencia HTTP |
| `scenario.lacp.member` | Cambio supervisado | HQ/S1/S2, miembro concreto permitido | 2→1→2 y convergencia |
| `scenario.sdn.port` | Cambio supervisado | puerto experimental definido, TTL y rollback | Conectividad, aislamiento y retorno |
| `scenario.netem` | Cambio supervisado | solo interfaz experimental allowlisted; <=60 s | Pérdida/latencia medida y reversión |
| `ml.infer` | Lectura | dataset/modelo aprobado, sin acciones | Score, explicación, confianza y fuente |
| `aiops.recommend` | Lectura | incidente identificado | Runbook sugerido y riesgos |
| `aiops.execute` | Cambio supervisado | ID runbook revisado + aprobación + nonce | Pre/post, eventos y rollback |

Los límites son **propuestas de diseño**, no capacidades ya desplegadas. `iperf3` debe usar servidor y cliente de endpoints virtuales autorizados, con limpieza de procesos y puertos y controles de consumo. `netem` nunca sobre `ens33`, gateway ni conexiones de gestión.

## 5. Controles y límites de operación

- **Modo inicial solo lectura** y simulaciones deshabilitadas hasta pruebas locales; separar roles de espectador y operador, con autenticación y confirmación para acciones de cambio.
- No permitir IP arbitraria, URLs externas, rutas de archivos libres, shells ni opciones de comando no enumeradas. Resolver origen/destino contra inventario/IPAM existente.
- Cola serial para acciones mutadoras, idempotencia, expiración, timeout y cancelación segura. Para pruebas en paralelo, imponer límites de carga y recursos.
- Registrar `job_id`, `action_id`, usuario/rol, timestamp UTC, host/contexto, parámetros, código de salida, output sanitario, hashes, estado de precheck y rollback.
- Validar ANTES y DESPUÉS `ens33`, gateway, OSPF, servicios afectados y fuente NOC; abortar si la condición inicial es ambigua. Un estado `UNKNOWN` no da permiso para actuar.
- Acciones disruptivas deben tener **watchdog de restauración externo al proceso web**, TTL, lógica de retorno probada e indicador visual de tiempo restante. No prometer rollback garantizado si no se ha probado apagado/crash.
- Cerrar UI/aplicación no debe dejar fallas activas por error; diseñar cancelación y recuperación determinista con auditoría.
- No almacenar tokens, secretos, credenciales, historial privado o comandos irreproducibles en el frontend.
- CI prueba esquema/casos/API/UI sin redes privilegiadas; validaciones disruptivas solo en VM de laboratorio con gate explícito.

## 6. Construcción incremental

1. **Esqueleto UI read-only**: inicio + topología multisede + estado WAN/HA/LACP/SDN + API propia. No modificar el NOC topológico estable hasta tener pruebas de paridad.
2. **Pruebas acotadas**: ping, traceroute, HTTP; luego iperf3 TCP/UDP con límites; gráficas, historial y exportación.
3. **Integración de diagnóstico inteligente**: detección experimental, explicación y advertencias con datos propios verificados; pronóstico no demostrado.
4. **Integración de AIOps supervisado**: catálogo de runbooks, aprobación, ejecución protegida, watchdog y recuperación controlada.
5. **Copiloto RAG (#198)**: corpus autorizado, generación con citas y abstención, evaluación de fidelidad, relevancia y seguridad; sin autorización ni ejecución de cambios.
6. **Demostración/aceptación**: escenarios de inicio sano → degradación → mediciones → detección/recomendación → autorización → cambio → verificación/retorno; contraste de métricas reales y evidencia.
7. **Observabilidad de servicio**: Blackbox, SLI/SLO, error budget, burn rate, Alertmanager y evaluación de Grafana especializado.
8. **Cierre técnico**: recuperación desde apagado, seguridad, regresión y evidencias de la consola. La entrega definitiva requiere la evaluación integral.

## 7. Cobertura académica y auditoría de inicio

La [matriz de cobertura académica](../gestion/cobertura-academica-netlab360.md) establece las capacidades visibles, los componentes de segundo plano, la evidencia histórica y las brechas. Antes de implementar, reanudar y auditar la VM sin modificar la infraestructura. Los escenarios mutadores del catálogo son propuestas: la API protegida acredita únicamente el costo OSPF delimitado de R-S1/s1b; WAN, HTTP, LACP, SDN y netem requieren aceptación individual de ejecutores y rollback. El navegador y el copiloto no adquieren privilegios de aprobación administrativa. Las ampliaciones tecnológicas y la evaluación científica requieren sus propias validaciones. La consola ofrece puntos de extensión sin presentar capacidades pendientes como implementadas.

**Principio UX:** el usuario elige **qué comprobar o simular**; la aplicación decide **qué procedimiento autorizado ejecutar** y registra **qué ocurrió realmente**. Nunca se presenta como una consola de comandos arbitrarios.

## Estado de integración de la interfaz

Validamos 204 casos específicos, topología de 18 nodos y 21 enlaces (vista resumida de 15 nodos y 14 enlaces), filtros por sede, selección persistente, zoom, pantalla completa y actualización incremental. Los intervalos de consulta configurables son 5, 10, 15, 30, 60 y 300 segundos; históricos y diagnóstico técnico se consultan manualmente. La documentación Swagger usa la sesión vigente, ambas paletas y consultas GET permitidas. La copia histórica de alertas conserva su procedencia y no equivale a un registro continuo. La equivalencia completa con las interfaces anteriores se comprueba antes de su retiro.

## Consolidación de la experiencia de usuario

El portal oficial permanece en 127.0.0.1:9140. Conservamos un único diagrama completo de 18 nodos y 21 enlaces, incluidos los tres servidores HA y cuatro enlaces WAN del grafo NOC. Retiramos los controles de vista resumida/detallada sin retirar el origen del grafo. Diferenciamos inventario, estado administrativo, FIB y observación HTTP en el inspector. Ampliamos la proyección visual a 26 nodos y 28 relaciones mediante el inventario S05 y las observaciones autenticadas de `/api/v1/sources`. Conservamos el contrato NOC de 18/21, con tres agregados LACP (dos miembros dibujados por agregado), tres accesos SDN y una relación OpenFlow. Las fuentes mantienen sus propios cortes; el estado de los hosts SDN y de los miembros individuales no se deduce de recuentos agregados. Las tablas permiten propagar la rueda al documento cuando no tienen recorrido interno.

La observabilidad carga al entrar; su temporizador independiente actualiza las sondas y los SLI, no los históricos ni las notificaciones. Estos últimos consultan por selección. Los trabajos conservan su historial y exportaciones, con resultados expandibles sin desplazamiento deliberado y sondeo de lectura. Normalizamos la fecha visible como MM/DD/AAAA · HH:mm:ss, hora de Panamá y formato de 24 horas. Conservamos los datos, los permisos y los contratos de ejecución; el retiro de las interfaces anteriores y la recuperación se acreditan mediante pruebas independientes.
