# S06-048 — Estados IA explícitos y auditoría LACP/SDN del NOC

## Alcance

Tras S06-047 (backend de NOC validado y captura F09 aprobada), el panel web distingue con precisión entre tres situaciones: **SIN DATOS / UNKNOWN** cuando la fuente IA no está disponible o la muestra caduca; **DESACUERDO IA / UNKNOWN** cuando existen medidas verificadas, pero los tres modelos no coinciden; e **INDICIO DE DEGRADACIÓN / UNKNOWN** cuando todos los modelos clasifican DEGRADED sin corroboración externa de la falla. Mantiene **NORMAL · EGRESO HQ** exclusivamente con consenso NORMAL válido, sin atribuir salud global ni verdad de terreno.

Se modifica únicamente el HTML/JavaScript y las pruebas de contrato de `servicios/topologia-s05/index.html`, con pruebas bajo `tests/test_s06_noc_ia_bridge.py`. No se cambia `app.py`, FRR, LACP, Faucet, OpenFlow, interfaces ni modelos. El NOC sigue siendo de solo lectura.

## Aclaración del aviso LACP/SDN en F09

La previsualización 9131 fue iniciada como `python3 -u servicios/topologia-s05/app.py --serve --port 9131` **sin** `NETLAB360_PRIV_OBSERVER=/usr/local/libexec/netlab360-observer`. Por contrato, `optional_privileged_snapshot()` devuelve la advertencia `Observaciones LACP/SDN: helper privilegiado no configurado` y los indicadores muestran `SIN DATOS` incluso si los agregadores y el controlador permanecen operativos.

El servicio systemd estable `netlab360-s05-noc.service` **sí** define esa variable y el lote S05-145B verificó dos muestras reales de LACP 2/2 en HQ/S1/S2 y Faucet/OpenFlow conectado. Eso es un antecedente, no evidencia de estado actual. Para conocer el estado **actual** consultar solo el endpoint de producción local `http://127.0.0.1:9130/api/v1/graph`, validando `lacp`, `sdn` y `source_warnings`. Si hay datos, el problema fue solo la previsualización; si no hay datos, diagnosticar lecturas/credenciales/frescura sin modificar la topología.

En futuras vistas temporales, únicamente después de comprobar que el helper existe y que `sudo -n /usr/local/libexec/netlab360-observer snapshot` está autorizado, se puede iniciar el NOC de previsualización con:

```bash
NETLAB360_PRIV_OBSERVER=/usr/local/libexec/netlab360-observer \
  python3 -u servicios/topologia-s05/app.py --serve --port 9131
```

Esto **habilita observación**, no activa ni modifica LACP/SDN. No reiniciar el NOC 9130, no ampliar sudoers ni ejecutar como root.

## Criterios antes de aceptar S06-048

1. CI de código y pruebas sin regresiones S05 y S06.
2. Comprobar endpoint 9130 para confirmar lecturas actuales LACP/SDN y advertencias, sin asumir que `SIN DATOS` significa apagado.
3. Validar que los tres textos posibles de incertidumbre aparecen en la implementación y que el NOC original conserva grafo de 18 nodos/21 enlaces, 21 namespaces, cuatro contenedores y red administrativa intacta.
4. Si se toma otra captura, hacerlo solo cuando una validación funcional realmente lo justifique; F09 y F09B ya documentan estado normal y desacuerdo.

No declarar pronóstico de fallas ni remediación automática; el `ground_truth` de mediciones recientes continúa `UNKNOWN`.

## Estado de desarrollo (23/11/2026)

PR [#173](https://github.com/recm0708/netlab360/pull/173) fusionado en `b8265d0`. CI general **753 tests (752 aprobados, uno omitido)**, CI S05 de contrato gráfico también aprobada. **Comprobación en VM aún pendiente:** NOC original 9130, variable del servicio systemd y telemetría actual de LACP/SDN; no se realizaron cambios de red ni reinicios. No se requiere repetir F09.
