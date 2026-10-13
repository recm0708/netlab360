# NETLAB360 B3 — NOC histórico local (iteración 1)

**Estado:** código creado y versionado en GitHub; **NO se ha ejecutado todavía en Ubuntu**.  
**Fuente de datos:** `~/netlab360-bootstrap/evidencias/b3-linea-base/`, derivada del CSV `17-b2-convergencia-20261013-115141.csv` del 13/10/2026 (76 muestras exitosas).  
**Seguridad:** Python estándar, solo `127.0.0.1:8765`, sin permisos root, Docker o modificaciones de `ens33`/VMnet8.

## Alcance funcional inicial

- `GET /`: HTML con banner **HISTÓRICO / NO EN VIVO**, tarjetas (76 muestras, 76 éxitos, 0 fallos) y tabla/barras por fase/ruta FIB.
- `GET /healthz`: JSON `{"status":"ok","mode":"historical","live_monitoring":false,"samples":76}`; confirma salud del servicio de lectura, **no salud de routers actuales**.
- `GET /api/v1/baseline`: JSON completo de las cinco fases, RTT medio y rutas vistas.
- `GET /metrics`: exposición de métricas históricas en formato Prometheus, **sin Prometheus instalado ni scraping activo**.
- Métodos de escritura `POST` rechazados; rutas ajenas a las anteriores devuelven 404.
- `--check`: valida archivos, esquema, marcadores históricos y conteos; no abre socket.

## Primer ensayo reproducible (pendiente de ejecución)

Terminal 1 SSH/Ubuntu:

```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
python3 - <<'PY'
import ast
from pathlib import Path
p = Path("servicios/noc-historico/app.py")
ast.parse(p.read_text(encoding="utf-8"))
print("B3_SINTAXIS: OK")
PY
python3 servicios/noc-historico/app.py --check
python3 servicios/noc-historico/app.py --serve
```

Mantener **Terminal 1** abierta; su proceso estará en primer plano y mostrará las solicitudes HTTP. Si el servidor falla o termina, revisar la consola; no abrir puertos al exterior.

Terminal 2 SSH/Ubuntu, mientras corre Terminal 1:

```bash
curl -fsS --max-time 5 http://127.0.0.1:8765/healthz
curl -fsS --max-time 5 http://127.0.0.1:8765/api/v1/baseline | python3 -m json.tool
curl -fsS --max-time 5 http://127.0.0.1:8765/metrics
curl -sS -o /dev/null -w 'HTTP_DASHBOARD=%{http_code}\n' --max-time 5 http://127.0.0.1:8765/
curl -sS -o /dev/null -w 'HTTP_NO_EXISTE=%{http_code}\n' --max-time 5 http://127.0.0.1:8765/no-existe
```

En un segundo PowerShell Windows mientras SSH terminales Ubuntu siguen conectadas:
```powershell
ssh -N -L 8765:127.0.0.1:8765 netlab360
```
Mantener ese túnel activo y abrir en navegador Windows `http://127.0.0.1:8765/`. **Nunca** usar IP `192.168.47.40:8765` ni configurar NAT/port forwarding de VMware, ya que el servicio está ligado intencionalmente a loopback del invitado.

Para detener: `Ctrl+C` en PowerShell del túnel y `Ctrl+C` en Terminal 1 Ubuntu. Verificar que `ss -ltn '( sport = :8765 )'` no muestre LISTEN, `docker ps -a` e `ip netns list` vacíos, `ens33` y default intactos, Git limpio. Código de salida del servidor 0 cuando se detiene limpiamente por Ctrl+C.

## Evidencias solicitadas

- **B3_02_API_y_Metricas_Historicas.png**: consultar `/healthz`, `/api/v1/baseline` y `/metrics` dentro de terminal 2, con marcadores de inicio/fin. Mostrar los datos históricos y códigos HTTP.
- **B3_03_Panel_NOC_Historico.png**: captura del navegador con URL `http://127.0.0.1:8765/`, título y banner *HISTÓRICO / NO EN VIVO*, tarjetas y tabla/gráfica visibles. Si no cabe completo, usar dos imágenes con sufijos A/B, sin recortar u ocultar limitaciones.

El usuario considera todas las capturas solicitadas tomadas salvo aviso expreso. Cuando envíe PNG, auditar en issue #43; **no confundir suposición de toma con inspección visual o subida GitHub**.

## Después del primer ensayo

1. No elevar el progreso S01 de 43% hasta observar las pruebas reales, documentarlas y justificar puntos según matriz vigente.
2. Preparar exporter/Prometheus de **datos dinámicos**, con etiquetas de estado actual, timestamps y frescura, preferiblemente contenido versionado bajo `servicios/observabilidad/`.
3. Hacer un evento WAN-P down/up realmente medido y mostrado en la API y dashboard, con alarma, estado de recuperación y criterios de falsos positivos; hasta entonces #12, #15 y #20 permanecen abiertas.
4. Mantener comparación con SoT IPAM y seguridad del host. No exponer tokens SSH/GitHub ni instalar paquetes innecesarios.
