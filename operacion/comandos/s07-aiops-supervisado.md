# AIOps supervisado

## Descripción

Integramos observaciones, correlación de evidencias,
hipótesis RCA, recomendaciones, Intent Assurance y
actuaciones RFC delimitadas con autorización humana.

## Preflight protegido

```bash
sudo -v
sudo -n /usr/bin/python3 -I /usr/local/libexec/netlab360/s07-preflight.py check
```

El resultado MET confirma las condiciones observadas
del preflight, no concede autorización de intervención.

## Adquisición integrada

```bash
python3 scripts/s07/adquisicion_integrada.py
```

La adquisición consulta las fuentes FRR, Prometheus,
NOC e IA y normaliza los eventos de la ventana observada.

La falta de una fuente de diagnóstico debe conservar
su representación de incertidumbre.

## Validación offline

```bash
python3 -m unittest discover -s tests -p 'test_s07_*.py' -v
```

## Consulta de la API Unix

Solo cuando la API protegida se encuentre activa y
el operador disponga del acceso autorizado:

```bash
curl --fail --silent --show-error --max-time 5 --unix-socket /run/netlab360-s07-api/api.sock http://localhost/api/v1/health
```

No iniciamos automáticamente la API, el broker o las
sesiones RFC como parte del arranque general.

## Componentes de diagnóstico y actuación

- [Contrato de eventos](../../scripts/s07/contrato_eventos.py).
- [Persistencia de eventos](../../scripts/s07/almacen_eventos.py).
- [Contexto RCA](../../scripts/s07/contexto_rca.py).
- [Correlación](../../scripts/s07/correlacion_evidencias.py).
- [Diagnóstico RCA](../../scripts/s07/diagnostico_rca.py).
- [Recomendaciones](../../scripts/s07/recomendaciones_rca.py).
- [Recuperación documental](../../scripts/s07/recuperacion_documental.py).
- [Intent Assurance](../../scripts/s07/intent_assurance.py).
- [Broker RFC](../../scripts/s07/rfc_ospf_operacional.py).
- [API controlada](../../scripts/s07/api_s07.py).

## Intervenciones y aceptación

La aceptación operacional requiere revisar los contratos
de autorización, exclusión mutua, watchdog, idempotencia
y restauración antes de realizar una actuación.

No ejecutamos el procedimiento de aceptación de la API
como comprobación rutinaria. Incluye operaciones reales
y exige autorización independiente.

Procedimiento: [aceptación protegida](../../scripts/operacion/s07-aceptar-api.sh).

## Documentación relacionada

- [Preflight](../../docs/diseno/s07-preflight-orquestador.md).
- [Eventos e incidentes](../../docs/diseno/s07-contrato-eventos-e-incidentes.md).
- [Intent Assurance y RFC](../../docs/diseno/s07-intent-assurance-y-rfc.md).
- [Runbooks](../../docs/diseno/s07-runbooks-y-recomendaciones.md).
- [Ensayos operacionales](../../docs/diseno/s07-ensayos-operacionales.md).
- [API controlada](../../docs/diseno/s07-api-controlada.md).
