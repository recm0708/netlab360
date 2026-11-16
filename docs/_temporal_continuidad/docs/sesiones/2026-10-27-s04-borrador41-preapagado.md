# NETLAB360 — S04: borrador académico 4.1 y preapagado verificado (27/10/2026)

**Fuente primaria:** salida original de cuatro terminales aportada por el operador y PDF `1457-Proyecto Semestral_borrador4.1.pdf` proporcionado en la sesión. Estas fuentes no se publican en el repositorio por ser evidencia administrativa y manuscrito con datos de personas; se registra exclusivamente la síntesis técnica necesaria.

## Auditoría académica 4.1

- Archivo: `1457-Proyecto Semestral_borrador4.1.pdf`, **95 páginas**. PDF exportado el 27/10/2026 alrededor de las 03:57 -05. El documento conserva capítulos 1–8, referencias y el informe único acumulativo; se edita manualmente en Word.
- **Cinco correcciones confirmadas por lectura:** introducción fases 1–4 en pp.7–8; 3.6 en p.21; 3.6.1 alerta/NOC sin notificaciones externas en p.21; 4.7.2 infraestructura de observabilidad en p.32; fila S04 Tabla 5 ya actualizada, p.38.
- **Pendientes reales antes de 5.6/6.9/7.10:** 2.4.1 p.11, 3.8 p.23, apertura capítulo 4 p.23, Tabla 1 pp.24–25 (NOC futuro y nota), apertura 4.7 p.32, 4.8 pp.33–34, apartado 4.8.1 p.34 y presentación del capítulo 5 p.35. Encabezado, nota y párrafo posterior de Tabla 5 pp.37–38 aún dicen "tres primeras fases" aunque la fila S04 está validada. 7–8 y Tabla 12 siguen centrados en las tres primeras fases y 107 PNG; no están adaptados todavía.
- El índice PDF pasa a 95 páginas (borrador4.0 tenía 94). **No hay inserción efectiva todavía de secciones 5.6, 6.9 o 7.10**. Fechas de revisión 30/10 y 13/11 futuras.

## Preapagado controlado S04 — confirmado desde terminal

- `git pull --ff-only origin main` ejecutado, Git `main` limpio `8254376` y sin modificaciones.
- `ens33=192.168.47.40/24`, `default via 192.168.47.2 dev ens33`.
- **Antes de detener servicios**, se confirmaron escuchando **únicamente localhost** 9110, 9091 y 9120.
- Paso **4.69** `S04_PREAPAGADO_FASE1=OK`: estados WAN y LAN copiados fuera de Git. Backup en `~/netlab360-bootstrap/s04/evidencias/S04_Preapagado_20261027T084907083378Z`; backup SQLite realizado usando API `sqlite3.Connection.backup`, `PRAGMA integrity_check=ok` y **3/3 eventos G3** `source=verified_G3_terminal_log`.
- Paso **4.70** procesos detenidos interactivamente: Terminal4 NOC `^CS04_NOC_DETENIDO=SI`; Terminal3 Prometheus `^C` 03:49:33-05 y log completo "Received an OS signal, exiting gracefully", "Rule manager stopped", "Scrape manager stopped", "Notification manager stopped", "See you next time!"; Terminal2 exporter `^CS04_EXPORTER_DETENIDO=SI`. El intento de reutilizar el túnel 9120 después de detenerlo devolvió `Connection refused`, compatible con el apagado NOC, no evidencia de falla de red de gestión.
- **Aún pendiente** paso **4.71**: comprobar efectivamente que 9110/9091/9120 están libres, TSDB y SQLite presentes y `ens33`/GW intactos. **No consta desmontaje** LAN/WAN, `docker compose down`, `poweroff`, snapshot posterior ni aceptación académica S04.
- **Prohibido** afirmar la VM ya apagada o recrear incidentes. Tras 4.71 se decidirá con prueba de estados la secuencia `LAN down→WAN down→Docker Compose S02 down→postcheck→poweroff`; preservar archivos externos y OpenTofu state.

## Seguimiento

El grupo copiará textos en el Word maestro y reenviará el PDF para contraste. El cronograma 30/10 y 13/11 sigue pendiente. SLO 99% permanece candidato, a diferencia de las medidas reales 15m 450/450 y 60m 1698/1740 (42 fallos, margen -25). No atribuir NOC con ML entrenado ni Alertmanager externo.

[Reanudación](../REANUDAR-AQUI.md) · [Protocolo seguro](../05-plan-operativo-y-pausas.md) · [Guion académico](../academico/s04-guion-de-actualizacion-del-informe.md) · [Issue de informe](https://github.com/recm0708/netlab360/issues/27).
