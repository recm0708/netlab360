# Consola interactiva y acciones — Fase 08

**Estado:** diseño técnico aprobado como base de trabajo, **no código implementado**. El NOC de la fase 05 y la API protegida de la fase 07 son antecedentes comprobados; la consola aún no está implementada. Destino: demostración académica ejecutable sin escribir comandos frente a la profesora y funcionamiento reproducible en la VM.

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
| **10. Diagnóstico IA** | Detección, scores, explicación, confianza/UNKNOWN, baseline de reglas, pronóstico y deriva **pendientes de validación en la fase 10** | Inferencia solo lectura; consulta de evidencia |
| **11. Incidentes y AIOps** | Correlación de fuente, línea de tiempo, recomendación, riesgo y postcondición mediante la API de la fase 07 validada, con integración de la fase 08 pendiente | Crear solicitud, consultar estado y resultado; aprobación administrativa separada, ejecución protegida y retorno |
| **12. Copiloto RAG** | Respuestas con fuentes propias, incertidumbre y citas | Consultas de solo lectura; sin autorización de cambios (#198) |
| **13. Evidencias y sistema** | Historial de trabajos, logs sanitizados, versiones, tests, métricas y catálogo | Descargar resultados JSON/CSV, generar inventario técnico y comprobar salud |

**Diseño adaptable:** desktop en VMware/Windows con barra lateral fija; tarjetas en pantallas estrechas; secciones sin implementación muestran `PENDIENTE` explícitamente, nunca resultados ficticios. Mantener el NOC de la fase 05 accesible durante la migración.

## 2. Arquitectura escogida (preferencia práctica)

- **UI:** HTML/CSS/JavaScript con componentes sencillos y gráficas Plotly. Reutilizar modelos y SVG/visuales del `servicios/topologia-s05/index.html`; no crear un segundo NOC desconectado. Dash opcional solo si se acredita beneficio de integración, no necesario para un menú.
- **Backend:** Python FastAPI + Uvicorn usando entorno virtual de las fases 06–08. Endpoints tipados para estado, series, pruebas, catálogo, ejecuciones y evidencia. Servir API y frontend desde la misma aplicación (sin CORS público).
- **Fuentes:** adaptadores locales del exportador de la fase 04 `127.0.0.1:9110`, NOC de la fase 05 `127.0.0.1:9130`, Prometheus local `9091` si está activo, histórico SQLite, estados de operación y módulos de las fases 06 y 07.
- **Persistencia propia:** SQLite privado bajo `netlab360-bootstrap/s08/` con registros de trabajos/eventos, parámetros validados, acciones, estados previos y posteriores y artefactos; **no** dentro de Git.
- **Exposición:** por defecto solo `127.0.0.1:9140` en la VM. Demo desde Windows: túnel SSH `ssh -L 9140:127.0.0.1:9140 rc-aa-ec@192.168.47.40`; navegador Windows `http://127.0.0.1:9140`. Acceso externo solo tras revisar controles de autenticación, CSRF y autorizaciones.
- **Protocolo UI:** peticiones REST + actualización ligera por polling/SSE; límites de frecuencia y tiempo. Evitar WebSockets por defecto si no se justifican.

## 3. Organización del código y de los comandos

```text
servicios/consola-s08/
    api/
        main.py              # FastAPI y rutas publicas controladas
        models.py            # Esquemas de entrada/salida
        readers/             # Adaptadores S04/S05/Prometheus/SQLite
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

**Crítico:** NO pasar cadenas libres a `bash -c`, `shell=True`, `sudo` con rutas de scripts editables por el usuario o interpolaciones del navegador. Los scripts que requieran privilegios deben instalarse como ejecutores **propiedad root, no editables por usuario web**, y recibir únicamente acciones/argumentos autorizados; el observador de la fase 05 permanece read-only. Verificar política de ejecución y pruebas de intrusión antes de conectar botones que produzcan fallos.

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

1. **Esqueleto UI read-only**: inicio + topología de la fase 05 + estado WAN/HA/LACP/SDN + API propia. No modificar el NOC de la fase 05 estable hasta tener pruebas de paridad.
2. **Pruebas acotadas**: ping, traceroute, HTTP; luego iperf3 TCP/UDP con límites; gráficas, historial y exportación.
3. **Integración de la fase 06**: detección experimental, explicación y advertencias con datos propios verificados; pronóstico no demostrado.
4. **Integración de la fase 07**: catálogo de runbooks, aprobación, ejecución protegida, watchdog y recuperación controlada.
5. **Copiloto RAG (#198)**: corpus autorizado, generación con citas y abstención, evaluación de fidelidad, relevancia y seguridad; sin autorización ni ejecución de cambios.
6. **Demostración/aceptación**: escenarios de inicio sano → degradación → mediciones → detección/recomendación → autorización → cambio → verificación/retorno; contraste de métricas reales y evidencia.
7. **Observabilidad de servicio**: Blackbox, SLI/SLO, error budget, burn rate, Alertmanager y evaluación de Grafana especializado.
8. **Cierre técnico**: recuperación desde apagado, seguridad, regresión y evidencias de la fase 08. La entrega académica definitiva corresponde a la fase 10.

## 7. Cobertura académica y auditoría de inicio

La [matriz de cobertura académica](../gestion/cobertura-academica-netlab360.md) establece las capacidades visibles, los componentes de segundo plano, la evidencia histórica y las brechas. Antes de implementar, reanudar y auditar la VM sin modificar la infraestructura. Los escenarios mutadores del catálogo son propuestas: la API de la fase 07 acredita únicamente el costo OSPF delimitado de R-S1/s1b; WAN, HTTP, LACP, SDN y netem requieren aceptación individual de ejecutores y rollback. El navegador y el copiloto no adquieren privilegios de aprobación administrativa. La fase 09 incorpora ampliaciones tecnológicas y la fase 10 amplía la validación científica y consolida la entrega. La fase 08 debe ofrecer puntos de extensión sin presentar esas capacidades como implementadas.

**Principio UX:** el usuario elige **qué comprobar o simular**; la aplicación decide **qué procedimiento autorizado ejecutar** y registra **qué ocurrió realmente**. Nunca se presenta como una consola de comandos arbitrarios.
