# NETLAB360 — Fase 4 G2: exporter, Prometheus y NOC operativos sobre topología activa

**Corte de pruebas:** 27/10/2026, 00:10–00:15 (America/Panama). **Fuente:** salida real remitida por el operador, no simulación ni futura ejecución. Continúa [G1 LAN/OSPF](2026-10-26-s04-g1-lan-y-muestra-activa.md).

## Estado de infraestructura

- `main` sincronizada por fast-forward `9197486`→`a03b230`, árbol limpio al inicio.
- Tres contenedores FRR del proyecto `netlab360-s02-wan` operativos; **12 namespaces** LAN; 9110/9091/9120 libres antes de iniciar.
- `S04_G2_PRECHECK=OK`. Red administrativa `ens33=192.168.47.40/24`, ruta default por `192.168.47.2` intacta.

## G2 — Pruebas reales validadas

1. **Exporter** en proceso persistente `127.0.0.1:9110`, modo solo lectura, SoT `candidate`; `/healthz` confirmó `source_ok=true`, `topology=active`. Prueba real de `/api/v1/state` y `/metrics`: 3 routers, WAN admin UP **8/8**, VLAN admin UP **9/9**, **25 series** de métricas, antigüedad **3.21 segundos**. Resultado `S04_G2_EXPORTER=OK`.
2. **Prometheus 3.7.0** en proceso persistente `127.0.0.1:9091`: `promtool check config`, `check rules` y `test rules` exitosos, **4 reglas**, TSDB en `~/netlab360-bootstrap/prometheus/s04/data`, instancia B3 intacta. API real target `up`, `netlab360_s04_source_up=1`, series WAN **8/8** y VLAN **9/9** en valor 1, alertas activas **0** (baseline sano). Resultado `S04_G2_PROMETHEUS=OK`.
3. **NOC** en proceso persistente `127.0.0.1:9120`: `--check` aprobado, `--once` confirmó fuente fresca (1.86 s), `topology=active`, sedes HQ/S1/S2, `prometheus.available=true`, `scrape=up`, `alerts_known=true`, 0 alertas. API `/api/v1/overview` comprobada: `S04_G2_NOC=OK`. **La evidencia de visualización final en navegador Windows y captura S04_09 no consta todavía**.
4. Túnel separado desde Windows `ssh -N -L 9120:127.0.0.1:9120 rc-aa-ec@192.168.47.40` quedó en solicitud de contraseña en el registro. **No está acreditado que se estableció el túnel ni que el navegador renderizó el NOC**.

## Estado y continuidad

- **G0 y G1 cerradas; G2 validada funcionalmente por exporter/Prometheus/NOC y pendiente de evidencia visual, captura y publicación.**
- No se recibieron PNG nuevos aún. **No** marcar `S04_07`, `S04_08` ni `S04_09` como capturados/publicados hasta verificación del operador. Persisten 114 PNG publicados (S04=7).
- El usuario solicitó **consolidar las seis terminales en cuatro**: mantener Terminal 2 exporter, Terminal 3 Prometheus y Terminal 4 NOC; Terminal 1 como shell SSH interactivo y **túnel SSH local** usando `ssh -L 9120:127.0.0.1:9120 netlab360`. Cerrar Terminal 5 (validación duplicada) y Terminal 6 (túnel redundante). El túnel interactivo permite verificar la URL en Windows mientras la Terminal 1 ejecuta consultas Linux.
- Antes de G3, asegurar evidencia G2 y comprobar código/temporizadores de regla `NETLAB360S04WANAdminDown` (6 s) y script de fallo/restauración S1; no afirmar incidencia ni `firing/resolved` de una ejecución aún inexistente. Cualquier ejecución G3 requerirá verificación simultánea y conservación segura del estado.
- **No detener** tres servicios ni topología FRR/WAN/LAN en este corte. `source_ok` y `admin_up` son observación administrativa, no prueba autónoma de OSPF/HTTP; OSPF se validó por separado en G1.
- Continuar S04→S08 sin imponer el cierre prematuro de S01/S03; se mantienen indicadores históricos y pendientes reales individuales.

**Archivos de referencia:** [plan S04](../operaciones/s04-cierre-observabilidad-multisede.md), [issue S04 #4](https://github.com/recm0708/netlab360/issues/4), [tablero fases](../control/06-tablero-porcentajes-cierre-fases-2026-10-25.md).
