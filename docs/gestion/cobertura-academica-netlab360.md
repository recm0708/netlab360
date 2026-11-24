# Cobertura académica y criterios de aceptación de NETLAB360

## Alcance

Este documento relaciona los contenidos académicos de Tópicos Especiales II con las funcionalidades propias de NETLAB360 y establece los criterios de seguimiento para las fases restantes.

Los materiales docentes, los laboratorios individuales y el parcial constituyen referencias metodológicas. Sus datos, configuraciones y resultados no se presentan como mediciones propias de NETLAB360.

## Criterios académicos de entrega

- Informe académico acumulativo de al menos 40 páginas.
- Redacción técnica propia, organizada y sustentada mediante resultados verificables.
- Citas y referencias conforme a APA 7 y al formato institucional aplicable.
- Figuras y tablas contextualizadas mediante su interpretación técnica.
- Presentación PowerPoint derivada del informe.
- Demostración en vivo de los componentes implementados.
- Archivo TAR técnico independiente, conforme a la modalidad registrada para NETLAB360.
- El informe termina en Referencias, sin capítulo de anexos.
- El paquete técnico debe contener únicamente recursos pertinentes del proyecto, sin credenciales, datos personales, archivos temporales ni materiales docentes ajenos.
- La obligatoriedad de entregar una OVA continúa pendiente de confirmación docente.

El título comunicado para el proyecto es «Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede».

## Estructura del informe

El documento comprende portada, introducción, objetivos, planteamiento del problema, fundamento técnico, diseño, implementación, pruebas, análisis de resultados, conclusiones, recomendaciones y referencias.

Las comprobaciones deben identificar las condiciones iniciales, el estímulo experimental, el resultado observado, la recuperación y las limitaciones correspondientes.

## Convenciones editoriales

La documentación se redacta desde la perspectiva del equipo del proyecto, con terminología técnica precisa y una distinción explícita entre diseño, implementación, validación y planificación.

Cada resultado identifica las condiciones del ensayo, el comportamiento observado, su interpretación y sus limitaciones. Las pruebas automatizadas no sustituyen las demostraciones operativas.

Se mantiene un único informe académico acumulativo. La numeración de figuras del informe es independiente de los identificadores de las capturas.

Los documentos técnicos se organizan por función, evitando duplicar cronologías, estados de avance y procedimientos.

## Matriz preliminar de cobertura

La siguiente matriz constituye una referencia de planificación al cierre de S06. Su revisión definitiva requiere contrastar nuevamente los capítulos, actividades, laboratorios y guías originales del curso.

| Fuente académica | Contenido relacionado | Estado preliminar en NETLAB360 | Seguimiento |
|---|---|---|---|
| Capítulo I y laboratorio 1 | SoT, intención, drift, reconciliación, idempotencia y OSPF | Implementado parcialmente mediante S02 y S03 | Ampliar mediante verificaciones de intención |
| Capítulo II y laboratorio 2 | OpenTofu, módulos, estado, locking, ownership y WireGuard | Recursos locales OpenTofu validados; túneles y proveedores externos no demostrados | Evaluar ampliación |
| Capítulos III–IV y laboratorio 3 | Ansible, roles, CI/CD, Policy as Code y rollback | Automatización FRR y GitOps implementados | Ampliar operación supervisada; evaluar multivendor |
| Capítulos V–VI y laboratorio 4 | Prometheus, Blackbox, SLI/SLO, error budget, burn rate y Grafana | Observabilidad, persistencia e incidentes WAN comprobados | Revisar cobertura individual de componentes |
| Capítulo VII y parcial 1 | Redes híbridas, Kubernetes, Cilium, Hubble y eBPF | Metodología experimental aprovechada; tecnologías adicionales pendientes de evaluación | Ampliación condicionada |
| Capítulo VIII | Calidad de datos, ventanas, particiones temporales y data leakage | Estudio uniforme V2 validado | Preservar metodología y trazabilidad |
| Capítulo IX y laboratorio 6 | IA/ML, reglas, modelos y diagnóstico | Comparación P95, Isolation Forest y regresión logística sobre ICMP | Integrar recomendaciones supervisadas |
| Capítulo X y laboratorio 7 | Anomalías y referencias históricas no intrusivas | Detección experimental de degradación y análisis retrospectivo | Ampliar correlación contextual |
| Capítulo XI y laboratorio 8 | Pronóstico, horizonte temporal, MAE, costo de alertas y QoS | Pronóstico futuro y MAE prospectivo no demostrados | Evaluar ampliación experimental |
| Capítulo XII y laboratorio 8 | Explicabilidad, overfitting, deriva y revisión humana | Evaluación cronológica y análisis descriptivo de deriva | Ampliar explicabilidad y validación de cambios de contexto |

## Estado técnico de referencia

Las fases S01–S06 se encuentran cerradas. La plataforma dispone de enrutamiento multisede, segmentación VLAN, automatización declarativa, observabilidad, LACP, disponibilidad lógica HTTP, SDN y detección experimental de anomalías.

El estudio V2 utiliza particiones cronológicas independientes, modelos congelados y un protocolo uniforme de medición ICMP. La falla HTTP fue evaluada como escenario independiente. No se atribuye a los resultados capacidad de pronóstico futuro, generalización automática entre protocolos ni remediación autónoma.

## Planificación de las fases restantes

S07 desarrollará la operación inteligente supervisada mediante correlación de eventos, diagnóstico, recomendación, aprobación humana, ejecución autorizada, comprobación y rollback.

S08 consolidará la aplicación interactiva, las pruebas reproducibles, la recuperación operativa y la preparación de la entrega según el alcance aprobado.

La eventual S09 constituye una ampliación condicionada, no una fase aprobada ni implementada. Su necesidad se determinará después de revisar esta matriz al cierre de S07 y S08.

Las tecnologías adicionales deberán responder a un caso de uso propio, contar con recursos suficientes y conservar el aislamiento de la red administrativa.

## Preparación del paquete técnico y demostración

El TAR reunirá configuraciones declarativas, inventarios, scripts, servicios, pruebas reproducibles, registros técnicos pertinentes y evidencias seleccionadas.

Incluirá un README con dependencias, versiones, compatibilidad y orden de ejecución. El paquete se preparará en un directorio independiente y se verificará mediante listado de contenidos y extracción de prueba.

Se excluyen credenciales, llaves privadas, tokens, estados sensibles de infraestructura, entornos virtuales Python completos, cachés, archivos personales y materiales docentes originales.

La demostración deberá acreditar el estado inicial, la intervención controlada, el resultado observado y la restauración. La reconstrucción automática después de apagar la VM continúa pendiente de validación.

## Revisión y aceptación

Cada tecnología se clasificará según su evidencia real: implementada y validada, parcial, experimental, limitada, condicionada o no demostrada.

La ampliación de funcionalidades exige pruebas independientes y no modifica retroactivamente los resultados alcanzados.

[Plan maestro y criterios técnicos](../diseno/s06-s08-plan-maestro-y-criterios.md).
