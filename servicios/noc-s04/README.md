# NETLAB360 S04 — NOC central y por sede (incremento inicial)

**Estado:** diseño y código propuestos para el primer panel multisede. Las pruebas offline/CI no acreditan todavía una visualización real en Windows ni la detección de un incidente de WAN activa. La aceptación requiere resultados aportados desde Ubuntu y evidencias de pantalla.

## Alcance realmente implementado

- Web NOC exclusivamente en `127.0.0.1:9120`, servido con la biblioteca estándar Python. Es una interfaz **solo lectura**: no despliega contenedores, no modifica interfaces FRR, no ejecuta OpenTofu y no tiene endpoints de escritura.
- Consolida el colector S04 `127.0.0.1:9110/api/v1/state` y Prometheus `127.0.0.1:9091/api/v1/targets` / `api/v1/alerts`. Solo se consultan esas URL fijas de loopback, con plazos de consulta.
- Vistas seleccionables **CENTRAL / HQ / S1 / S2**: estado real del contenedor de cada sede, interfaces WAN y VLAN desde lectura Docker/nsenter, estado de *scrape* de Prometheus y alertas reales reportadas por su API.
- Cadencia visual de 3 segundos, con tiempo UTC de la consulta. Si la muestra del exporter supera 15 segundos, carece de sello horario o no confirma las tres sedes, se oculta el estado antiguo y se muestra **UNKNOWN**. Prometheus inaccesible equivale a **alertas desconocidas**, no a cero alertas.
- `offline` con fuente confiable expresa contenedores desmontados intencionalmente. `active` indica tres contenedores en ejecución, pero no OSPF Full, HTTP, disponibilidad de capa 7 ni SLI/SLO.
- No hay API externa, credenciales embebidas, conexión a `0.0.0.0`, Alertmanager, persistencia histórica ni inteligencia artificial. Estas funciones mantienen sus propias decisiones y pruebas.

## Comprobaciones previstas

**Antes de iniciar el NOC:** validar que el colector S04 esté operativo en 9110 y Prometheus S04 esté activo en 9091; comprobar la administración `ens33=192.168.47.40/24` y gateway `.2`.

**Terminal Ubuntu NOC (separada de las otras dos):**

```bash
cd ~/proyectos/netlab360
python3 -m unittest discover -s tests -p 'test_s04_*.py' -v
python3 servicios/noc-s04/app.py --check
python3 servicios/noc-s04/app.py --once
python3 servicios/noc-s04/app.py --serve --port 9120
```

**Terminal Ubuntu de verificación:** `curl -fsS http://127.0.0.1:9120/healthz`, `curl -fsS http://127.0.0.1:9120/api/v1/overview` y comprobar `127.0.0.1:9120` con `ss -lntp`. En topología desmontada son esperados exporter fresco, topología `offline`, Prometheus disponible y cero alertas (solo si la API de alertas respondió de manera confiable).

**PowerShell Windows (túnel SSH opcional para visualización):**

```powershell
ssh -N -L 9120:127.0.0.1:9120 netlab360
```

Abrir `http://127.0.0.1:9120/`, comprobar controles de vista central/HQ/S1/S2. Cerrar túnel con `Ctrl+C`.

## Evidencias y pruebas

Las capturas `S04_01` (API exporter real) y `S04_02` (Prometheus *scrape* sin falsa alarma) fueron confirmadas tomadas y están respaldadas por salidas del 26/10/2026, pero **sus PNG no se han inspeccionado ni publicado**.

Para el panel se proponen capturas futuras:
- `S04_03_NOC_Central_Tres_Sedes_Offline` — captura obligatoria con URL local, tarjetas de HQ/S1/S2, fuente actual y Prometheus.
- `S04_04_NOC_Sucursal_Estados_WAN_VLAN` — captura obligatoria de vista por sede, sin confundir `-1` con DOWN.
- `S04_05_NOC_API_Agregada_Fuentes_Confiables` — verificación complementaria de API central y frescura.

La evidencia de enlaces fallidos y restaurados requerirá una prueba **posterior** sobre la red desplegada en condiciones seguras, por lo que no debe derivarse de estos estados `offline`. La cronología persistente de eventos, notificaciones, SLI/SLO y HTTP real continúan pendientes.
