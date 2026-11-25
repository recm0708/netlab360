# Contexto topológico y correlación RCA

## Alcance

S07-002A desarrolla el contexto de correlación de la issue [#191](https://github.com/recm0708/netlab360/issues/191). El [módulo de contexto](../../scripts/s07/contexto_rca.py) verifica la ventana y las 58 identidades de señal, y organiza referencias en 18 contextos. No confirma incidentes ni propone cambios. Las [pruebas](../../tests/test_s07_contexto_rca.py) utilizan datos sintéticos.

## Dependencias y límites

Los contextos incluyen adquisición, tres sedes, cuatro WAN, seis selecciones FIB, dos inferencias ICMP, HTTP HA y SDN. Cada WAN relaciona el indicador NOC, dos extremos administrativos Prometheus y dos extremos OSPF. Los contextos de ruta consideran el primer salto local y sus enlaces principal y de respaldo; no demuestran el trayecto completo. Los contextos se superponen por diseño, sin duplicar las observaciones originales.

NOC y Prometheus pueden depender del mismo colector de telemetría: la coincidencia no es evidencia estadísticamente independiente. La observación FIB no prueba tráfico. El plano de control SDN, el servicio HTTP y la inferencia ICMP conservan ámbitos separados. La adquisición se evalúa en su cierre histórico, no como estado actual. Si la ventana no cumple los límites, ninguna referencia se considera utilizable.

Las hipótesis ordenadas, evidencias contradictorias, desviaciones de configuración y ensayos RCA se incorporarán en bloques posteriores. S07-002A fue aceptada en VM: 18 contextos, 58 señales, 56 elegibles y dos inferencias ausentes; 10 pruebas dirigidas y regresión de 1026 ejecutadas, una omitida. CI 45318910309 satisfactoria.

## Clasificación y proximidad temporal

S07-002B incorpora [correlación de evidencias](../../scripts/s07/correlacion_evidencias.py) y [pruebas](../../tests/test_s07_correlacion_evidencias.py). El módulo verifica nuevamente el contexto original y clasifica cada señal según su procedencia, alcance, detalles y consistencia de estado. Se distingue evidencia administrativa, operacional, de existencia, adquisición, servicio, plano de control e inferencia. Las señales no elegibles o inconsistentes no participan en pares.

Se relacionan dos señales solamente cuando pertenecen a un contexto común y sus fechas de observación difieren como máximo 10 segundos. Este umbral inicial es una decisión de diseño, no una garantía de simultaneidad ni una prueba de causalidad. Los pares se identifican mediante los dos eventos originales ordenados y se conservan una sola vez aunque pertenezcan a varios contextos. Se informa si comparten fuente, si NOC y Prometheus pueden compartir colector o si son fuentes distintas cuya independencia no se ha acreditado.

La clasificación administrativa UP no prueba forwarding. La selección HTTP de respaldo no equivale a indisponibilidad. Una inferencia ICMP no confirma la causa de una degradación. El resultado es histórico respecto al cierre de ventana; no acredita vigencia actual. La priorización de hipótesis y el tratamiento explícito de evidencias a favor y en contra se incorporarán en S07-002C–E. S07-002B fue validada: 56 evidencias utilizables, 240 pares únicos (89 misma fuente, 67 posible colector compartido, 84 fuentes distintas sin independencia probada), separación máxima 3 s, cero inconsistencias; 1038 pruebas ejecutadas, una omitida, CI 45319206152 satisfactoria.

## Hipótesis RCA y auditoría independiente de configuración

S07-002C–F incorpora [diagnóstico RCA](../../scripts/s07/diagnostico_rca.py), [auditoría de costos](../../scripts/s07/auditoria_costos_rca.py) y [ensayos sintéticos](../../tests/test_s07_diagnostico_rca.py). Las reglas distinguen desviaciones administrativas WAN/VLAN, adyacencias OSPF no FULL, selección FIB de respaldo, miembros LACP, existencia de routers, HTTP HA, SDN, inferencias ICMP y adquisición de telemetría. Cada hipótesis identifica eventos ancla, evidencia a favor, evidencia en contra, información desconocida y alcance. El soporte y la oposición se limitan a pares directamente vinculados dentro del umbral de 10 segundos. La oposición representa tensiones de evidencia, no necesariamente incompatibilidad física simultánea. No se suman votos por pares ni se asignan probabilidades.

El orden es ordinal y determinista: SCOPED (desviación acotada sin oposición registrada), LIMITED (inferencia o datos faltantes), AMBIGUOUS (evidencia en contra); dentro de cada categoría se ordena por regla e identidad de contexto. No es una prioridad de reparación ni severidad. Una hipótesis no confirma la causa raíz; un resultado sin candidatos y con datos ausentes no acredita salud global. Si la ventana falla, el motor se abstiene. Las reglas son deliberadamente conservadoras: la desaparición de una fila OSPF permanece desconocida en el adaptador actual.

La auditoría separada verifica los ocho costos WAN explícitos contra el SoT candidato de automatización y el perfil de red multisede (10 principal, 100 respaldo), con comprobación de identidad antes y después de cada lectura. Solo registra campos de costo y no exporta la configuración completa. Una desviación explícita puede clasificarse NON_COMPLIANT; un costo ausente o no verificable se mantiene UNKNOWN. Esta auditoría tiene su propia fecha y no se utiliza retrospectivamente para atribuir causa a la ventana histórica. Los casos sintéticos no modifican la base operacional ni inducen fallas. La aceptación en VM y los ensayos reales compuestos posteriores se mantienen diferenciados.

## Aceptación técnica S07-002

S07-002C–F validado el 23/11/2026: línea base histórica NO_CANDIDATE_WITH_GAPS (dos inferencias IA ausentes), 3/3 escenarios WAN/OSPF/FIB, 6/6 de servicios e IA, 6/6 de incertidumbre y drift, tres hipótesis separadas en el ensayo compuesto. Auditoría real de costos OSPF: 8/8 conformes. Regresión 1057 ejecutadas, 1056 aprobadas, una omitida, CI 45319679019 satisfactoria. SQLite conserva 116 registros; 21 namespaces, cuatro contenedores, siete servicios y gestión intactos. Sin fallas inducidas ni cambios. Los ensayos positivos son sintéticos: no prueban causalidad ni detección de cada falla real; la validación operacional compuesta corresponde a #196. El catálogo gráfico de AIOps quedó publicado al cierre de esta etapa.
