# B2-L3 — Ensayo de tráfico ICMP continuo y observación de rutas durante conmutación WAN

**Ejecución real:** 2026-10-13, 11:51:41–11:52:40 (América/Panamá, UTC−05).  
**Resultado:** `RESULTADO_EJECUCION_CONVERGENCIA=0`. Instrumentación y limpieza completadas satisfactoriamente.  
**Entorno:** `netlab360-lab`, Ubuntu 26.04.1 LTS, host de gestión `ens33=192.168.47.40/24` / puerta de enlace `192.168.47.2`, FRRouting 10.7.1.  
**Herramienta:** `scripts/laboratorio/b2-dualwan-medicion-continua.py`; orquestador `scripts/laboratorio/b2-dualwan-ospf.sh`.

## 1. Preparación, despliegue y seguridad

- `git pull --ff-only` al commit `83e712b23b18b66b86c96b181ffeb184907ac1f8` y `ast.parse` de Python: **`SINTAXIS_MEDICION: OK`**; sintaxis Bash sin error; Git `main...origin/main` limpio al instante de la prueba.
- Inicio de prueba `2026-10-13T11:51:41-05:00` con `--snapshot-confirmado`; `HOST_PROTEGIDO=SI`. Sudo pidió autenticación y retrasó algunos segundos el arranque, sin afectar el muestreo iniciado tras el `up`.
- `precheck` exitoso a 11:51:52: `RESULTADO_B2_DUALWAN_PRECHECK=0`.
- `up` a 11:51:52–11:52:12: `OSPF_DUAL_FULL: SI`, `RESULTADO_B2_DUALWAN_UP=0`, ambos routers y dos WAN instalados en contenedores Docker aislados de la red administrativa. El monitor empezó a las 11:52:12.
- El sondeo ICMP fue de **un paquete por iteración**, con consulta de FIB mediante `ip route get`, timestamps en hora local y escritura en CSV. Intervalo observado de ~0.37 s entre muestras, no un ping continuo ininterrumpido a nivel de enlace.

## 2. Resultados por fase

| Fase | Muestras | ICMP correctos | Fallidos | Pérdida observada | Rutas |
|---|---:|---:|---:|---:|---|
| Normal | 14 | 14 | 0 | 0.0% | `wan-p` en 14/14 |
| Transición hacia respaldo | 1 | 1 | 0 | 0.0% observado | `wan-b` en el único sondeo |
| Respaldo | 16 | 16 | 0 | 0.0% | `wan-b` en 16/16 |
| Transición hacia principal | 29 | 29 | 0 | 0.0% observado | `wan-b` hasta el sondeo 58, `wan-p` en 59–60 |
| Principal restaurada | 16 | 16 | 0 | 0.0% | `wan-p` en 16/16 |
| **TOTAL** | **76** | **76** | **0** | **0.0% de los sondeos** | **FIB observada en los dos cambios** |

**Conmutación:** `FASE=cambio_respaldo` a las 11:52:17.131; `fail` bajó WAN-P; sondeo #15 a las 11:52:17.333 encontró `wan-b` con ICMP correcto. La métrica de script fue `PRIMER_SONDEO_FIB_cambio_respaldo: 0.186s desde inicio de accion`. Esto es **latencia de primera detección por sondeo**, no duración exacta de convergencia OSPF. `CONMUTACION_WAN_B: OK (sondeo 1)`, `ACCION_FIN=fail RC=0`.

**Retorno:** `FASE=cambio_principal` a las 11:52:23.425; sondeos #32–58 siguieron utilizando `wan-b` sin pérdida, y sondeo **#59 a las 11:52:33.587** observó `wan-p` con ICMP correcto. Métrica script: `PRIMER_SONDEO_FIB_cambio_principal: 10.147s desde inicio de accion`; `RESTAURACION_WAN_P: OK (sondeo 11)`, `ACCION_FIN=restore RC=0`. Esta cifra incorpora tiempo de estado/protocolo/sondeo y **no constituye un tiempo exacto medido por FRR ni SLA garantizado**.

**Precisión/limitaciones:** Las 76 muestras ICMP exitosas prueban que **no se observaron pérdidas en los instantes muestreados**, incluso en las ventanas etiquetadas de transición. No demuestra que absolutamente ningún paquete se perdió entre sondeos (intervalo ~0.37 s), ni que otras condiciones reproduzcan los mismos tiempos. Origen/destino fueron IP LAN **dummy de los routers**, todavía sin estaciones/servicios independientes. La prueba mide tráfico unidireccional HQ→S1, mientras el ensayo anterior de 30/30 sí validó ambas direcciones en fases estables.

## 3. Cleanup y estado final

A las 11:52:40: `down` devolvió `RESULTADO_B2_LIMPIEZA=0` y `ACCION_FIN=down RC=0`, `LIMPIEZA_FINAL=OK`, `HOST_PROTEGIDO=SI`, `CONTENEDORES_B2_RESIDUALES=0`. Postcheck manual confirmó `docker ps -a` sin contenedores, `ip netns list` vacío, `ens33 UP 192.168.47.40/24`, default por `192.168.47.2`, servicios `docker`, `ssh`, `open-vm-tools` en `active`, árbol Git limpio. `RESULTADO_EJECUCION_CONVERGENCIA=0`.

**Archivos locales conservados en la VM (no incluidos automáticamente en Git):**
- `~/netlab360-bootstrap/evidencias/17-b2-convergencia-20261013-115141.log`, ~11 KiB.
- `~/netlab360-bootstrap/evidencias/17-b2-convergencia-20261013-115141.csv`, ~5.3 KiB, 76 filas de datos más encabezado.
- Logs del orquestador `15-b2-dualwan-{precheck,up,fail,restore,down}-20261013-115*.log`.

**Captura:** `B2_16_Medicion_Continua_Convergencia.png` (consulta 11:52:58) delimitada `INICIO CAPTURA B2_16` / `FIN CAPTURA B2_16`, dada por tomada según convención del usuario. **Todavía no inspeccionada visualmente ni subida al repositorio**; seguimiento issue [#43](https://github.com/recm0708/netlab360/issues/43).

## 4. Cierre parcial y próximos pendientes

**Subhito logrado:** red OSPF dual-WAN operativa, conmutación/restauración comprobadas mediante FIB e ICMP muestreado, limpieza segura. No repetir esta prueba automáticamente.

**Permanecen abiertas:** [#42](https://github.com/recm0708/netlab360/issues/42) hasta validar criterios de hosts/servicios y precisión/aceptación; [#12](https://github.com/recm0708/netlab360/issues/12) hasta exporter/Prometheus, evento con timestamps, API/dashboard/alarma; [#1](https://github.com/recm0708/netlab360/issues/1) hasta MVP integral. Sin OVA, manual APA, LACP/ACL, Ansible/OpenTofu aplicados ni analítica de anomalías.

**Corte solicitado por el usuario:** cierre inmediato sin esperar 12:00, sincronizar todos los documentos e issues y apagar Ubuntu/Windows ordenadamente antes 12:15 del 13/10. **No hay confirmación de apagado todavía**.
