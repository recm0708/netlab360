# Contexto topológico y correlación RCA S07

## Alcance

S07-002A desarrolla el contexto de correlación de la issue [#191](https://github.com/recm0708/netlab360/issues/191). El [módulo de contexto](../../scripts/s07/contexto_rca.py) verifica la ventana y las 58 identidades de señal, y organiza referencias en 18 contextos. No confirma incidentes ni propone cambios. Las [pruebas](../../tests/test_s07_contexto_rca.py) utilizan datos sintéticos.

## Dependencias y límites

Los contextos incluyen adquisición, tres sedes, cuatro WAN, seis selecciones FIB, dos inferencias ICMP, HTTP HA y SDN. Cada WAN relaciona el indicador NOC, dos extremos administrativos Prometheus y dos extremos OSPF. Los contextos de ruta consideran el primer salto local y sus enlaces principal y de respaldo; no demuestran el trayecto completo. Los contextos se superponen por diseño, sin duplicar las observaciones originales.

NOC y Prometheus pueden depender del mismo colector S04: la coincidencia no es evidencia estadísticamente independiente. La observación FIB no prueba tráfico. El plano de control SDN, el servicio HTTP y la inferencia ICMP conservan ámbitos separados. La adquisición se evalúa en su cierre histórico, no como estado actual. Si la ventana no cumple los límites, ninguna referencia se considera utilizable.

Las hipótesis ordenadas, evidencias contradictorias, desviaciones de configuración y ensayos RCA se incorporarán en bloques posteriores. S07-002A fue aceptada en VM: 18 contextos, 58 señales, 56 elegibles y dos inferencias ausentes; 10 pruebas dirigidas y regresión de 1026 ejecutadas, una omitida. CI 45318910309 satisfactoria.

## Clasificación y proximidad temporal

S07-002B incorpora [correlación de evidencias](../../scripts/s07/correlacion_evidencias.py) y [pruebas](../../tests/test_s07_correlacion_evidencias.py). El módulo verifica nuevamente el contexto original y clasifica cada señal según su procedencia, alcance, detalles y consistencia de estado. Se distingue evidencia administrativa, operacional, de existencia, adquisición, servicio, plano de control e inferencia. Las señales no elegibles o inconsistentes no participan en pares.

Se relacionan dos señales solamente cuando pertenecen a un contexto común y sus fechas de observación difieren como máximo 10 segundos. Este umbral inicial es una decisión de diseño, no una garantía de simultaneidad ni una prueba de causalidad. Los pares se identifican mediante los dos eventos originales ordenados y se conservan una sola vez aunque pertenezcan a varios contextos. Se informa si comparten fuente, si NOC y Prometheus pueden compartir colector o si son fuentes distintas cuya independencia no se ha acreditado.

La clasificación administrativa UP no prueba forwarding. La selección HTTP de respaldo no equivale a indisponibilidad. Una inferencia ICMP no confirma la causa de una degradación. El resultado es histórico respecto al cierre de ventana; no acredita vigencia actual. La priorización de hipótesis y el tratamiento explícito de evidencias a favor y en contra se incorporarán en S07-002C–E. La aceptación de S07-002B en VM está pendiente.
