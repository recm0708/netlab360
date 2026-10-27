**ESTADO VIGENTE 27/10 — borrador 4.4 de 110 páginas:** apartado 5.6 y capítulo de pruebas 6.9.1–6.9.6 incorporados, **Figuras 16–20 y Tabla 13** presentes. No repetir correcciones de capítulos 5 y 6. Próximo bloque académico: revisar y actualizar capítulo 7, especialmente apertura con «tres primeras fases», añadir 7.10 de S04; actualizar conclusiones/recomendaciones del capítulo 8; sustituir conteos de capturas en Tabla 12 por **83 S01, 9 S02, 8 S03, 22 S04, total 122**, tras la depuración del catálogo oficial. La VM se apagó desde Ubuntu y SSH cerró; VMware no confirmado externamente. El texto histórico inferior corresponde a versiones previas.

---

**ÚLTIMO PDF 27/10/2026: BORRADOR 4.3 (99 páginas).** Comprobado: 4.7 corregido, cierre 5.5.9 modificado, apartado **5.6 y cinco subapartados íntegros en pp.66–70**. **No volver a corregir 4.7 ni a insertar 5.6**. Siguiente paso: corregir apertura de capítulo6 (p.70) y añadir 6.9 al final de 6.8, seguido de capítulo7/8 y Tabla12. Última figura actual 15 y tabla 12; próximas numeraciones tentativas 16/13. El host ejecutó `poweroff` y cerró SSH, VMware Powered Off pendiente de confirmación. [Bitácora](../sesiones/2026-10-27-s04-poweroff-solicitado-borrador43.md).

**CONTROL DE PDF ACTUAL 27/10/2026 — borrador 4.2 (95 páginas):** Correcciones 1–13 verificadas en el Word exportado, incluidas las ocho del último lote. **Solo ajuste de redundancia antes de insertar S04:** en `4.7`, p.32, borrar el párrafo antiguo completo que empieza «Las funciones de automatización, observabilidad y diagnóstico se desarrollan progresivamente y no constituyen todavía un sistema completamente integrado». Mantener el párrafo actualizado inmediatamente anterior y `4.7.1`. **No repetir ninguna corrección de 1–13.** Las inserciones pendientes 5.6, 6.9, 7.10 y ajustes 8/Tabla12 se encuentran debajo; la numeración de figuras (posterior a Figura15) debe recalcularse en Word. La VM está desmontada y lista para poweroff, pero no está confirmada apagada. Ver [bitácora](../sesiones/2026-10-27-s04-borrador42-desmontaje-validado.md).

**AVISO VIGENTE 27/10: PDF 4.1 auditado (95 páginas).** Están incorporados exactamente los cinco primeros cambios del guion: Introducción, 3.6, 3.6.1, 4.7.2 y la fila S04 de Tabla 5. El siguiente lote debe corregir p.11 2.4.1; p.23 3.8/4; pp.24–25 Tabla1; p.32 apertura 4.7; pp.33–34 4.8/4.8.1; pp.35–38 apertura 5, preámbulo/nota/cierre Tabla5, antes de crear 5.6. Se documenta en [bitácora](../sesiones/2026-10-27-s04-borrador41-preapagado.md). **No volver a sustituir las cinco secciones ya corregidas.**

# NETLAB360 — Texto de integración de S04 en el borrador académico 3.2

**Versión de trabajo interna actualizada el 27/10/2026.** No sustituye ni altera el Word/PDF maestro. Se verificó contra **el PDF realmente adjuntado más reciente** `1457-Proyecto Semestral_borrador4.0.pdf` (94 páginas, exportado 27/10 desde Microsoft Word): mantiene el esquema anterior de fases S01–S03, todavía sin inserciones S04. La última figura publicada en ese PDF es la **Figura 15** y la última tabla localizada es la **Tabla 12**. Cualquier numeración adicional se recalculará tras edición del documento maestro y no se adelantará como definitiva.

**Normas editoriales:** redactar como trabajo del grupo, no como manual de comandos; distinguir implementaciones probadas, medidas y mejoras futuras; mantener APA7, preámbulos y notas de figuras, evitar redundancias; conservar la estructura 5–8 y los apartados originales S01–S03. No crear sección de anexos: el TAR técnico es independiente. Citas/referencias nuevas solo al comprobar fuentes y su uso real.

## Inserción A — Capítulo 5, después de 5.5.9

### 5.6. Fase 4: implementación de observabilidad centralizada y gestión de incidentes

La cuarta fase amplió la infraestructura multisede con un mecanismo de observabilidad centralizada capaz de examinar el estado de los enlaces WAN, los segmentos VLAN y los componentes de supervisión. A diferencia de los ensayos iniciales de métricas ejecutados de manera aislada, esta implementación se verificó sobre una topología operativa compuesta por tres routers FRRouting, cuatro enlaces WAN principales y de respaldo, y nueve VLAN distribuidas entre HQ, S1 y S2. El alcance se delimitó a la recopilación, representación y evaluación de eventos comprobables, sin modificar automáticamente las configuraciones de los routers ni afirmar la existencia de un sistema de diagnóstico inteligente.

#### 5.6.1. Arquitectura del colector, Prometheus y NOC

Se implementó un colector de métricas de solo lectura, accesible en `127.0.0.1:9110`, que relacionó el inventario declarativo de la tercera fase con las observaciones obtenidas de los recursos operativos del laboratorio. La fuente de información se conservó explícitamente en condición `candidate`, por lo que su utilización como referencia no implicó declarar aprobado un contrato definitivo de aprovisionamiento. El colector diferenció la presencia de los recursos, la actualización de las observaciones y los estados administrativos de las interfaces, generando 25 series asociadas a tres sedes, ocho extremos WAN y nueve interfaces VLAN.

Prometheus 3.7.0 consultó el colector desde una instancia independiente en `127.0.0.1:9091`. Las reglas diferenciaron fallas de lectura de métricas, estados desconocidos, indisponibilidad administrativa de WAN y VLAN, y activación de alertas bajo condiciones comprobables. Por su parte, el NOC web en `127.0.0.1:9120` reunió una vista central y vistas por sede con indicadores de enlaces, segmentación, disponibilidad de fuente y eventos de supervisión. El acceso desde Windows se efectuó mediante reenvío local de SSH, manteniendo los servicios publicados únicamente en el entorno de loopback de Ubuntu.

La arquitectura mantuvo separadas la red administrativa de VMware, identificada mediante `ens33` y la dirección `192.168.47.40/24`, y las conexiones utilizadas por el escenario empresarial. Esta separación permitió ejecutar las comprobaciones sin depender de publicar los servicios de observabilidad directamente en la red externa.

#### 5.6.2. Activación sobre la red multisede y control de incidentes

Después de validar los módulos con la infraestructura experimental desmontada, se desplegaron nuevamente los tres routers, sus enlaces y los segmentos VLAN. Se comprobó el establecimiento de cuatro adyacencias OSPF en HQ y dos en cada sucursal, así como la preferencia por los enlaces principales en seis rutas evaluadas. El colector y el NOC actualizaron sus estados de acuerdo con los dispositivos activos, manteniéndose ocho extremos WAN y nueve interfaces VLAN administrativamente habilitados.

Para evaluar las transiciones de una alerta real, se desarrolló un procedimiento protegido que desactivó temporalmente `HQ/s1p`, correspondiente al enlace principal hacia S1. El procedimiento verificó las condiciones del escenario antes de intervenirlo, impidió operar sobre la red de gestión e incorporó una restauración del enlace mediante un bloque de ejecución protegido. Durante los 60 segundos de observación se registró la transición de la alerta `NETLAB360S04WANAdminDown` de `pending` a `firing`, al tiempo que se confirmó la utilización del enlace alterno `s1b`. La comunicación con S2 conservó su enlace principal `s2p`. Una vez rehabilitado `s1p`, se verificó el retorno a las rutas preferidas, la conectividad y la ausencia de la alerta entre las activas.

#### 5.6.3. Persistencia de mediciones e historial del NOC

Se comprobó la conservación de datos históricos al reiniciar exclusivamente el proceso de Prometheus, sin detener los routers ni la red LAN. La verificación comparó las muestras originales de la interfaz `HQ/s1p` y de su alerta de falla antes y después del reinicio, e incorporó el cambio de marca de tiempo de inicio del servicio como comprobante de una ejecución nueva. El resultado permitió acreditar la recuperación del historial en la base de datos de series temporales durante el período de retención configurado, sin confundirla con un archivo permanente de incidentes.

Como ampliación del NOC se incorporó un registro SQLite, almacenado fuera del repositorio, destinado a conservar transiciones de alertas observadas y a permitir consultas por sede y exportación en CSV. La lógica distingue eventos `pending`, `firing` y `resolved`, evita registros duplicados y no interpreta la pérdida de la fuente de supervisión como una recuperación de la WAN. Los tres estados del incidente ya ocurrido se incorporaron de manera explícita desde el log original, después de verificar su SHA-256, identificando su origen documental en lugar de atribuirlos al registrador recién activado. El almacenamiento y los identificadores de estos eventos permanecieron iguales después de reiniciar el proceso NOC.

#### 5.6.4. Indicadores de observabilidad y trazabilidad

La implementación se complementó con una herramienta de consulta de Prometheus capaz de calcular indicadores de éxito de recolección en ventanas de 15, 30 y 60 minutos. Se utilizaron contadores de muestras registradas y de valores exitosos, además de una fórmula de presupuesto de errores asociada a un objetivo propuesto. El parámetro de 99 % se identificó como un **SLO académico candidato**, no como un compromiso aprobado ni como un SLA de conectividad para usuarios finales.

Los scripts, las configuraciones y las capturas se integraron mediante repositorios y solicitudes de cambio en GitHub. Para la fase 4 se incorporaron tres lotes de evidencias con manifiestos SHA-256 y validación automática de integridad; los registros dinámicos y la base SQLite se conservaron fuera del código versionado.

## Inserción B — Capítulo 6, después de 6.8

### 6.9. Pruebas de observabilidad y gestión de incidentes correspondientes a la fase 4

#### 6.9.1. Validación de la topología y de la recolección multisede

Las pruebas iniciales se realizaron con la infraestructura desmontada para comprobar que la ausencia esperada de routers y VLAN no generara falsas alertas de enlaces. Posteriormente se repitieron las consultas con la red desplegada, verificando tres routers FRRouting, cuatro conexiones WAN, nueve gateways VLAN y la disponibilidad de las vistas central y por sede del NOC. El colector registró 25 series, ocho extremos WAN y nueve interfaces VLAN; Prometheus reportó su objetivo de recolección operativo y el NOC mostró una fuente confiable y actualizada.

La verificación se complementó con las pruebas regresivas del enrutamiento OSPF y de la LAN. Se obtuvieron cuatro vecindades `FULL` en HQ y dos por sucursal, seis rutas preferentes, seis pruebas ICMP entre routers, nueve gateways VLAN correctos y seis comunicaciones de LAN entre segmentos y sedes. Estos controles permitieron establecer que la observabilidad se efectuaba sobre una infraestructura activa y no únicamente sobre contenedores existentes.

**Figura propuesta A (con numeración definitiva pendiente).** Tablero del NOC con las sedes HQ, S1 y S2 y enlaces activos. Evidencia sugerida: `S04_09_NOC_Tres_Sedes_Enlaces_Activos-1` (más partes solo cuando añadan información no repetida). Preámbulo: «La Figura [n] muestra la representación centralizada de las tres sedes a partir de observaciones actualizadas del colector y Prometheus». Nota sugerida: «Nota. Elaboración propia a partir del NOC de NETLAB360, con tres sedes y ocho extremos WAN observados sobre la topología operativa».

#### 6.9.2. Incidente controlado, conmutación de WAN y recuperación

Se ejecutó una interrupción administrativamente controlada de `HQ/s1p` a las **06:05:04 UTC del 27 de octubre de 2026**. Prometheus registró el estado `pending` a las **06:05:07 UTC** y la condición `firing` a las **06:05:13 UTC**. Durante el evento se confirmó la utilización del enlace alterno `s1b` entre HQ y S1, la permanencia de S2 sobre `s2p` y la continuidad de las pruebas de comunicación. El enlace principal se rehabilitó a las **06:06:07 UTC**; las rutas preferentes regresaron a su configuración inicial y a las **06:06:18 UTC** se verificó que la alerta ya no figuraba entre las activas. Estas observaciones acreditan la detección, presentación y recuperación del evento en el NOC, sin demostrar un tiempo universal de convergencia ni entrega de notificaciones fuera del tablero.

**Figura propuesta B.** Comparación de alerta `firing` y recuperación, a partir de `S04_10` y `S04_11`. La nota debe distinguir fallo y recuperación comprobados y evitar atribuir un envío externo.

#### 6.9.3. Indisponibilidad de fuente y preservación histórica

La prueba de indisponibilidad se delimitó a detener temporalmente el colector de métricas, sin intervenir los routers o sus interfaces. El NOC identificó correctamente el estado `UNKNOWN`, Prometheus reportó `scrape=down` y la alerta de indisponibilidad del exporter alcanzó `firing`. No se observaron falsas alertas de caída de enlaces WAN o VLAN. Después de restaurar el servicio, el NOC volvió al estado `active`, con fuente actualizada y cero alertas activas. Las capturas `S04_13` y `S04_14` documentan ambas condiciones.

En la prueba de persistencia, la consulta histórica de Prometheus conservó **68 de 68** muestras de WAN y **28 de 28** muestras `firing` después del reinicio del servidor de métricas. Posteriormente se verificó la persistencia del diario SQLite del NOC mediante el cambio de PID del proceso, de `248883` a `263894`, y la igualdad de los tres eventos G3 antes y después del reinicio. El historial permaneció consultable por sede y exportable a CSV, sin declarar una retención indefinida de la TSDB.

**Figura propuesta C.** Evidencia de persistencia del historial, según `S04_12` y `S04_16`, priorizando solo una si el documento requiere economía de figuras.

#### 6.9.4. Evaluación de SLI y objetivo de observabilidad propuesto

Los indicadores se calcularon a partir de muestras realmente registradas por Prometheus, utilizando como numerador los scrapes exitosos y como denominador todos los scrapes presentes en cada ventana. Se examinó además la métrica de fuente confiable, cuya interpretación debe ser condicional porque puede quedar ausente cuando el propio scrape falla.

**Tabla propuesta (numeración definitiva pendiente).**
| Indicador | Ventana de 15 minutos | Ventana de 60 minutos |
|---|---:|---:|
| Scrapes exitosos/registrados | 450/450 | 1698/1740 |
| SLI de scrape | 100,000 % | 97,586 % |
| Fallos de scrape registrados | 0 | 42 |
| Presupuesto permitido al SLO candidato 99 % | 4 | 17 |
| Presupuesto restante | +4 | −25 |
| SLI condicional de fuente | 450/450 (100 %) | 1698/1698 (100 %) |
| Evaluación del 99 % propuesto | Cumpliría | No cumpliría |

**Preámbulo sugerido:** «La Tabla [n] contrasta las mediciones de éxito de recolección en dos ventanas temporales y su relación con el presupuesto de errores del objetivo académico candidato». **Nota sugerida:** «Nota. Elaboración propia con consultas reproducibles a Prometheus. El SLO de 99 % es una propuesta no ratificada; los porcentajes representan muestras registradas, no disponibilidad continua de la red empresarial». La ventana de una hora incluyó pruebas controladas de observabilidad, pero las cifras disponibles no permiten atribuir exactamente todos los fallos a un único evento.

**Figura propuesta D.** Captura `S04_17_Indicadores_SLI_SLO_Observabilidad`, únicamente si muestra información complementaria a la tabla y no repite innecesariamente todos los números.

#### 6.9.5. Validación final, integridad y trazabilidad

Tras completar los ensayos se verificaron nuevamente las adyacencias OSPF `FULL` (4/2/2), la preferencia de rutas WAN (6/6), la conectividad ICMP entre routers (6/6), los gateways VLAN (9/9) y las comunicaciones entre segmentos LAN (6/6). El exporter permaneció actualizado; Prometheus y el NOC estuvieron disponibles y sin alertas activas; el historial conservó tres transiciones auténticas de G3. La interfaz administrativa mantuvo `192.168.47.40/24` con puerta de enlace `192.168.47.2`.

Las evidencias de S04 quedaron organizadas en **22 imágenes PNG**, distribuidas en tres lotes de 7, 8 y 7 archivos, cada uno acompañado de su manifiesto de integridad. Los controles automáticos comprobaron tamaño, dimensiones y SHA-256; las acciones de integración continua verificaron las reglas del inventario. El repositorio alcanzó **129 PNG** acumuladas de las fases 1 a 4, sin atribuirlas a fases posteriores.

## Inserción C — Capítulo 7

### 7.10. Interpretación de la observabilidad multisede y sus limitaciones

La incorporación del colector y del NOC permitió convertir una infraestructura de comunicación previamente validada en un escenario donde los estados operativos podían interpretarse conjuntamente con alertas y registros históricos. En la falla de `HQ/s1p`, la secuencia temporal comprobada relacionó la desactivación administrativa del enlace, la activación de una regla en Prometheus, la selección de una ruta secundaria y la restauración de las condiciones iniciales. Esta correlación constituye un resultado más específico que la simple presencia de un indicador de disponibilidad en pantalla.

Las pruebas también demostraron la importancia de distinguir la caída real de un recurso de la falta de información suficiente para evaluarlo. Cuando se interrumpió el colector, la respuesta correcta del sistema fue clasificar la observación como `UNKNOWN`, no declarar que todas las WAN habían fallado. El diario de eventos persistente reforzó esta distinción al registrar resoluciones solamente cuando la fuente recuperaba condiciones confiables.

La comparación de indicadores permitió reconocer otra limitación metodológica. Aunque ambas ventanas reportaron 100 % de éxito en las muestras disponibles de `source_up`, la ventana de 60 minutos registró 42 fallas de scrape, equivalentes a un SLI de 97,586 %. Esto demuestra que el análisis exclusivo de una serie dependiente del scrape puede ocultar períodos sin datos. De igual manera, las posiciones nominales ausentes respecto de la cadencia configurada no fueron clasificadas automáticamente como fallas, al no contar con una identificación individual de su causa.

El objetivo del 99 % debe interpretarse como una referencia académica candidata para evaluar el método, y no como una garantía. El incumplimiento de ese candidato en la ventana de 60 minutos constituye un resultado que debe conservarse, especialmente porque el laboratorio se utilizó para realizar interrupciones controladas de observabilidad. Las mediciones no establecen disponibilidad contractual, latencia de aplicaciones, tiempo de recuperación de todos los servicios ni calidad extremo a extremo percibida por los usuarios.

Aunque el NOC incorporó alertas visibles e historial exportable por sede, no se configuró un servicio de mensajería externo ni se verificó la recepción de avisos por correo u otros canales. Además, la base SQLite conserva transiciones y la TSDB mantiene muestras bajo una retención limitada, sin constituir todavía un sistema distribuido de respaldo o una solución de diagnóstico inteligente. El diagrama de topología animado con semántica ampliada de estados y rutas queda reservado para la siguiente etapa de la plataforma, en lugar de atribuirlo retroactivamente a S04.

## Inserción D — Capítulo 8

**Añadir a 8.1 Conclusiones, antes de la síntesis final existente, sustituyendo o ajustando la frase anterior que declaraba pendiente la integración NOC:**

Durante la cuarta fase se consolidó un mecanismo de observabilidad centralizada de la red multisede, mediante un colector de solo lectura, Prometheus y un NOC con vistas de HQ, S1 y S2. Las pruebas efectuadas sobre la topología activa permitieron relacionar métricas administrativas, condiciones de la fuente y alertas con el comportamiento de las rutas principales y de respaldo. El incidente controlado de `HQ/s1p` confirmó que el sistema podía mostrar la condición de falla y su posterior recuperación, mientras que la verificación de estados `UNKNOWN` evitó interpretar la pérdida del colector como la caída general de las redes supervisadas.

La incorporación de un diario SQLite permitió conservar y consultar el historial de incidentes por sede después del reinicio del NOC, complementando la persistencia de series temporales comprobada en Prometheus. Asimismo, los indicadores obtenidos en ventanas de 15 y 60 minutos facilitaron evaluar la confiabilidad del proceso de recolección mediante resultados reproducibles, incluyendo un incumplimiento del objetivo candidato de 99 % en la ventana más extensa. En consecuencia, se amplió la capacidad de supervisión y análisis de la plataforma sin afirmar todavía capacidades de disponibilidad contractual, notificaciones externas, redundancia física o diagnóstico inteligente autónomo.

**En 8.2.2 «Integrar la observabilidad centralizada multisede», modificar la recomendación anterior (ahora implementada) para enfocarla en mejoras:**

**8.2.2. Fortalecer el historial y la presentación de la observabilidad multisede**

Se recomienda extender las capacidades de visualización del NOC mediante una topología interactiva que represente de manera diferenciada los enlaces principales, las rutas secundarias disponibles y los caminos efectivamente utilizados. La representación debe basarse en mediciones reales, con estados visibles de falla, degradación, desconocimiento y recuperación, evitando utilizar animaciones que sugieran tráfico si no se dispone de los contadores correspondientes. También conviene definir políticas de conservación y respaldo de la base histórica, junto con mecanismos de consulta y exportación adecuados para la revisión de incidentes.

Como complemento futuro podrá evaluarse la incorporación de canales de notificación externa con confirmación verificable de recepción, así como indicadores de disponibilidad orientados al servicio y a la experiencia del usuario. Estas ampliaciones requieren diseño y ensayos adicionales, por lo que se mantienen separadas de las funciones técnicamente demostradas durante S04.

## Ajustes editoriales obligatorios fuera de los apartados nuevos

1. El PDF 3.2 todavía dice **«tres primeras fases»**, **«hasta la fase 3»**, «observabilidad multisede pendiente» en Introducción, 7.1, 7.6, 7.8, 7.9, 8.1 y 8.2.2. No cambiarlas con sustitución global: cada oración puede referirse legítimamente al corte histórico de S01–S03. Revisar contextos y actualizar solo las afirmaciones de **estado actual** obsoletas.
2. La **Tabla 12** de objetivos (p. 88) tiene una fila «Desarrollar observabilidad» evaluada como desarrollo parcial pendiente de NOC. Debe actualizarse para reconocer el **NOC multisede funcional y G4 completada**, manteniendo límites de notificaciones externas y cobertura de servicio. La fila «Validar y documentar la plataforma» debe actualizar conteo de **107 a 129 PNG** si se mantiene indicador acumulado al corte S04; no presentarlo como un cumplimiento final de S08.
3. La última figura actual es la Figura 15. Numerar las nuevas figuras **solo al insertarlas y actualizar índice**, y ajustar preámbulos, títulos, notas y menciones cruzadas. Una figura compuesta de dos capturas debe evitar pequeños textos ilegibles.
4. Revisar introducción, objetivos y problema para la reunión Teams del **30/10/2026** en la issue #47, sin atribuir aprobación docente anticipada. No ampliar las conclusiones generales de S05–S08 como capacidades implementadas.
5. APA7: no añadir referencias ficticias por ser componente nuevo; en fundamento técnico utilizar referencias actuales ya documentadas cuando proceda (Prometheus, RFC 2328 y documentación de software), verificando que las citas y la lista coincidan. Si se añaden SQLite/TSDB como sustento teórico, verificar fuentes y datos editoriales aparte.
6. No publicar material sensible de la VM, contraseña, llaves, state OpenTofu ni datos operativos completos en GitHub por el solo hecho de documentar una fase. La evidencia ampliada corresponde al TAR técnico final cuando se apruebe su contenido.

**Condición de cierre:** esta guía no modifica el PDF 3.2, no certifica la revisión editorial de figuras ni ratifica el SLO candidato. Es material listo para integrar en el Word maestro con las comprobaciones indicadas. G0–G4 aceptadas técnicamente; G5 por ratificación interna y G6 por integración académica.

## Revisión adicional del borrador 4.0 (94 páginas, recibida 27/10)

- [x] Borrador 4.0 no incorpora aún fase 4 en capítulo 5 (`5.6`), pruebas (`6.9`) ni análisis (`7.10`); última figura 15 y última tabla 12. **No** afirmar que es informe S04 terminado.
- [x] **Introducción (p. 7–8)**: cronología dice que las fases posteriores *contemplan* observabilidad centralizada; actualizarla para decir que S04 está implementada y probada, sin atribuir SDN/ML o entrega final. No cambiar objetivos como si se hubiesen aprobado por la docente.
- [x] **3.6–3.6.1 (pp. 20–21)** y **3.8 (p. 22)**: diferencia legítima entre los ensayos iniciales B3 y el NOC implementado S04; actualizar las declaraciones generales que todavía lo presentan como un proyecto exclusivamente futuro.
- [x] **Tabla 1 (p. 24)**: fila «Supervisión central — Interfaz NOC» dice «Presentar ... cuando se complete su integración»; cambiar a «Presentar estados por sede, eventos y cronología confirmada; módulo central validado durante S04». Nota de tabla debe distinguir notificaciones externas, redundancia avanzada y diagnóstico ML futuro.
- [x] **4.7–4.7.2 (pp. 31–32)**: el texto actual deja NOC multisede pendiente. Incorporar interfaces localhost 9110/9091/9120 y SQLite (sin declarar funcionalidades externas de Alertmanager). Revisar **4.8** y 4.8.1 para evitar contradicciones.
- [x] **5. IMPLEMENTACIÓN (p. 35)**: el párrafo introductorio limita el corte a «tres primeras fases»; actualizar a cuatro fases validadas técnicamente. **Tabla 5 (pp. 36–37)**: reemplazar «Fase 4 — Planificada» por «Observabilidad multisede implementada y técnicamente validada; SLI registrados, SLO académico 99 % candidato pendiente ratificar; redacción y aceptación en curso»; mantener S05–S08 planificadas. Nota inferior y párrafos posteriores actualizados.
- [x] **7.1, 7.6, 7.8, 7.9, 8.1 y 8.2.2** aún se refieren a observabilidad NOC como pendiente; actualizar el **estado actual** sin borrar la cronología de fases anteriores.
- [x] **Tabla 12 (p. 88)** conserva «métricas iniciales» y «107 capturas», y presenta el NOC pendiente; actualizar a NOC multisede G0–G4 y 129 PNG verificadas al corte, manteniendo alcances del diagnóstico y AVISO externo sin implementar.
- [x] **Maquetación observada**: la Tabla 12 cabe en p.88, pero su nota continúa separada en p.89; la nota de Figura 1 está al comienzo de p.26 después de la figura p.25; comprobar también separación de otras figuras/notas e indentación de índice 6.5. Ajustar opciones de párrafo «Mantener con el siguiente», «Mantener líneas juntas» en Word, sin reducir textos a ilegibilidad.
- [x] **Citas/referencias**: la lista de referencias es la misma versión de base; verificar concordancia después de insertar 5.6/6.9/7.10; no inventar referencia específica para evidencia interna de terminal ni afirmar SLO formal.
- [ ] Textos correctivos se entregarán en conversación para copiar y pegar; la verificación de un PDF **actualizado tras copia** aún no existe. Fecha Teams 30/10 es revisión futura, no aprobación.
