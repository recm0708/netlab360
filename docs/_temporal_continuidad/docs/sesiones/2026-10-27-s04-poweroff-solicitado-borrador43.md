# NETLAB360 — S04: apagado solicitado por Ubuntu y borrador académico 4.3

**Fecha de registro:** 27/10/2026. Basado exclusivamente en el texto real del operador y en el PDF académico `1457-Proyecto Semestral_borrador4.3.pdf` (99 páginas), inspeccionado el mismo día. Sin inventar una captura de VMware ni afirmación de encendido posterior.

## Paso 4.76: sincronización, respaldo, retirada y apagado

Salida de la terminal de Ubuntu:
- `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`: fast-forward `1781ff5..d5158af` de la PR #81; rama `main` limpia.
- Respaldo en frío `~/netlab360-bootstrap/s04/evidencias/S04_Preapagado_20261027T084907083378Z/prometheus_tsdb_s04.tar.gz`: `sha256sum -c` devuelve **OK**, digest `e7602327d233fcb7dccd60f57fc3230202b1998c592655ec75ed20ef06ba49c1`; estados WAN/LAN e historial SQLite presentes.
- Ausentes los archivos de estado vivos S02 WAN/LAN y los contenedores `nl360-s02-r-hq`, `nl360-s02-r-s1`, `nl360-s02-r-s2`; pertenecientes exclusivamente al laboratorio, desmontados en pasos 4.73–4.74.
- Red administrativa preservada: `ens33 UP 192.168.47.40/24`, `default via 192.168.47.2 dev ens33`.
- Git local `d5158af` y `S04_APAGADO_AUTORIZADO=SI`; se ejecutó `sync`, seguido de `sudo systemctl poweroff`. El túnel SSH respondió `Connection to 192.168.47.40 closed by remote host.` y se volvió a PowerShell del equipo anfitrión.
- **Interpretación:** el sistema operativo inició el apagado de forma normal y cerró SSH. **No consta todavía captura/comprobación de `Powered Off` en VMware Workstation**. Marcar `poweroff iniciado; pendiente confirmación externa` hasta dicha verificación. Los mensajes anteriores `channel 2: connect failed` procedían del reenvío a un servicio NOC ya detenido.

## Informe único: versión 4.3 recibida

- PDF **99 páginas**, mantiene introducción y capítulos 1–8; comprobado que en p.32 se eliminó el párrafo duplicado de 4.7; cierre de 5.5.9 actualizado en p.66.
- Nuevo **5.6 Fase 4: implementación de observabilidad centralizada y gestión de incidentes** y cinco subapartados 5.6.1 a 5.6.5 incorporados en pp.66–70. El contenido refleja colector 9110, Prometheus 9091, NOC 9120, tres sedes, ocho extremos WAN, nueve VLAN, 25 series, incidente real en HQ/s1p, historial SQLite y límites del SLO candidato; no hay que repetir la sección 5.6.
- **Aún faltan** `6.9 Pruebas de observabilidad S04` (después de `6.8`), ampliación del capítulo 7 con interpretación S04, adecuación del capítulo 8 (todavía expresa que el NOC multisede está pendiente), y Tabla 12 con 129 PNG. Revisar la introducción del capítulo 6 en p.70, donde el alcance global sigue terminando en S03. Última figura existente Figura 15, última tabla Tabla 12.
- Correcciones futuras se entregan **por conversación para copiar al Word original**, no modificar ni distribuir el PDF adjunto.
- Revisión Teams 30/10 y ratificación SLO 99 % pendientes. No cerrar S04 académicamente ni iniciar S05 por este avance parcial.

[Guion](../academico/s04-guion-de-actualizacion-del-informe.md) · [Plan operativo](../05-plan-operativo-y-pausas.md) · [Matriz G6](../operaciones/s04-g6-matriz-aceptacion-evidencias-2026-10-27.md)
