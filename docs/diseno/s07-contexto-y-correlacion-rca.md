# Contexto topológico y correlación RCA S07

## Alcance

S07-002A desarrolla el contexto de correlación de la issue [#191](https://github.com/recm0708/netlab360/issues/191). El [módulo de contexto](../../scripts/s07/contexto_rca.py) verifica la ventana y las 58 identidades de señal, y organiza referencias en 18 contextos. No confirma incidentes ni propone cambios. Las [pruebas](../../tests/test_s07_contexto_rca.py) utilizan datos sintéticos.

## Dependencias y límites

Los contextos incluyen adquisición, tres sedes, cuatro WAN, seis selecciones FIB, dos inferencias ICMP, HTTP HA y SDN. Cada WAN relaciona el indicador NOC, dos extremos administrativos Prometheus y dos extremos OSPF. Los contextos de ruta consideran el primer salto local y sus enlaces principal y de respaldo; no demuestran el trayecto completo. Los contextos se superponen por diseño, sin duplicar las observaciones originales.

NOC y Prometheus pueden depender del mismo colector S04: la coincidencia no es evidencia estadísticamente independiente. La observación FIB no prueba tráfico. El plano de control SDN, el servicio HTTP y la inferencia ICMP conservan ámbitos separados. La adquisición se evalúa en su cierre histórico, no como estado actual. Si la ventana no cumple los límites, ninguna referencia se considera utilizable.

Las hipótesis ordenadas, evidencias contradictorias, desviaciones de configuración y ensayos RCA se incorporarán en bloques posteriores. La aceptación de S07-002A en VM está pendiente.
