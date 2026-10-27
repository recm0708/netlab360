# NETLAB360 — Primer colector de observabilidad multisede (S04)

**Estado:** implementación candidata versionada; **las pruebas reales en Ubuntu deben completarse antes de marcarla como validada**. Este componente complementa, pero no sustituye ni altera, el *exporter* B3 de la fase 1.

## Alcance

- Consulta el SoT local `~/netlab360-bootstrap/s03/rendered/sot-s03.json` en estado `candidate`: tres routers, cuatro enlaces WAN con ocho extremos y nueve interfaces VLAN. El SoT describe el estado esperado, no la disponibilidad real.
- Protege la gestión del host: `netlab360-lab`, `ens33=192.168.47.40/24` y ruta predeterminada por `192.168.47.2`.
- Utiliza exclusivamente `sudo -n docker inspect` de contenedores permitidos, cotejando nombre, proyecto Compose y `network_mode=none`. Sobre contenedores en ejecución consulta `sudo -n nsenter -t PID -n ip -j link show`. **No ejecuta Docker up/down, modificaciones de interfaces, FRR, Ansible ni OpenTofu.**
- Distingue `offline` (ningún router en ejecución), `partial` (uno o dos), `active` (tres) y `unknown` (observación no fiable). `active` **solo confirma presencia de contenedores**; no acredita vecinos OSPF, HTTP o conectividad entre sedes.
- Las interfaces ausentes o no desplegadas se representan con **-1 (desconocidas/no disponibles)**, sin convertir una topología detenida intencionalmente en alarma WAN. Cuando falla la consulta, `source_up=0`, estado `unknown` y no se reutilizan mediciones anteriores.
- `--check`: valida el SoT y la red de gestión, sin Docker. `--once`: una muestra de Docker e interfaces. `--serve`: API únicamente en `127.0.0.1:9110`, sin exponer VMnet8 ni ocupar el puerto 9108 del prototipo B3.
- Endpoints: `GET /api/v1/state`, `GET /healthz` (salud de la lectura, no disponibilidad del servicio empresarial) y `GET /metrics`. Las operaciones de escritura HTTP no están admitidas.

## Validación inicial sin despliegue

**Terminal SSH Ubuntu, ejecutando como cuenta normal:**

```bash
cd ~/proyectos/netlab360
python3 -m unittest discover -s tests -p 'test_s04_*.py' -v
python3 servicios/observabilidad/s04_exporter_multisede.py --check
sudo -v
python3 servicios/observabilidad/s04_exporter_multisede.py --once
```

Al encontrarse desmontados los routers tras las pruebas de S02, la muestra real esperada es `topology=offline`, `source_ok=true` y tres routers con valor 0. No debe observarse una alarma WAN_DOWN. Si falla `sudo -n`, el resultado deberá indicar `unknown` y un error, no un falso `offline`.

La primera prueba del servidor `--serve` se realizará **solo después de validar el resultado anterior**. La exposición en 9110 no implica que Prometheus ya haga *scrape*. No se cambian todavía la configuración ni las reglas B3, diseñadas para interfaces antiguas.

## Pruebas y pendientes

La suite `tests/test_s04_exporter_multisede.py` utiliza respuestas simuladas únicamente para **validar código offline**, sin privilegios ni Docker. Incluye SoT, protección de red, diferencia entre topología apagada y consulta fallida, contenedores de proyecto ajeno, evaluación de interfaces y estado parcial. **No sustituye las pruebas reales sobre Ubuntu**.

Persisten pendientes: OSPF Full, selección real de rutas de S1/S2, pruebas HTTP/VLAN, reglas de alerta nuevas, eventos correlacionados, NOC multisede, notificaciones, SLI/SLO y pruebas de recuperación. Las evidencias `S04_*` se incorporarán durante esas comprobaciones auténticas.

## Prometheus S04 aislado (segundo incremento)

Se añadió la configuración `servicios/observabilidad/prometheus/s04-prometheus.yml`, con destino exclusivo `127.0.0.1:9110` y **Prometheus en `127.0.0.1:9091`**, sin ocupar 9090 ni alterar las reglas B3. La TSDB queda en `~/netlab360-bootstrap/prometheus/s04/data`. El script `scripts/observabilidad/s04-iniciar-prometheus-local.sh` valida primero el colector, la red administrativa, los puertos, las reglas y los casos de prueba; no instala paquetes, no despliega contenedores y no toca FRR/Tofu.

Las cuatro reglas específicas de S04 separan (1) el *scrape* del exporter caído, (2) la fuente Docker desconocida, (3) una interfaz WAN realmente en estado administrativo DOWN y (4) una subinterfaz VLAN realmente en estado administrativo DOWN. No se activa alarma WAN cuando el estado es `-1` por infraestructura desmontada. La comprobación `promtool test rules` utiliza cuatro conjuntos de datos de ensayo aislados; **no** reemplaza las futuras pruebas de falla WAN real.

Para una prueba integrada se utilizan dos terminales SSH independientes y una tercera para consultar la API:

1. En Terminal A: `sudo -v` y `python3 servicios/observabilidad/s04_exporter_multisede.py --serve --port 9110 --interval 2`.
2. En Terminal B: `bash scripts/observabilidad/s04-iniciar-prometheus-local.sh`.
3. En Terminal C: `curl -fsS http://127.0.0.1:9110/metrics`, `curl -fsS http://127.0.0.1:9091/api/v1/targets` y `curl -fsS http://127.0.0.1:9091/api/v1/alerts`. Las consultas deben confirmar que el *scrape* funciona y **no** existen alertas WAN/VLAN activas cuando los routers están desmontados.
4. Para terminar, `Ctrl+C` en la terminal B y luego A. Verificar que los puertos 9091/9110 queden libres y la red administrativa no cambie.

Las capturas oficiales S04 se tomarán con métricas y respuestas reales verificadas, no con el simple resultado de pruebas sintéticas.
